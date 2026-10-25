"""OANDA v20 REST broker. Practice (demo, free fake money) and live use the same API on
different hosts, with separate tokens and account ids so practice credentials can never
place a live order."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Callable, Optional

from fxagent.brokers.base import Broker, BrokerError
from fxagent.models import AccountState, BrokerTrade, Candle, ClosedTrade, InstrumentInfo, OrderResult, Quote

log = logging.getLogger(__name__)

HOSTS = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}

# (method, path, query params, json body) -> parsed json response
Transport = Callable[[str, str, Optional[dict], Optional[dict]], dict]


def parse_time(s: str) -> datetime:
    """OANDA timestamps carry nanoseconds ('2024-01-02T03:00:00.000000000Z'); trim to micros."""
    s = s.rstrip("Z")
    if "." in s:
        head, frac = s.split(".", 1)
        s = f"{head}.{frac[:6]}"
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def http_transport(host: str, token: str, timeout: float = 15.0, retries: int = 3) -> Transport:
    def call(method, path, params=None, body=None):
        url = host + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body is not None else None
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": "RFC3339",
        }
        for attempt in range(retries + 1):
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return json.loads(resp.read() or b"{}")
            except urllib.error.HTTPError as e:
                payload = e.read().decode(errors="replace")
                retryable = e.code == 429 or e.code >= 500
                # never blindly retry an order POST: it may have been accepted
                if retryable and method == "GET" and attempt < retries:
                    time.sleep(2 ** attempt)
                    continue
                try:
                    msg = json.loads(payload).get("errorMessage", payload)
                except ValueError:
                    msg = payload
                raise BrokerError(f"OANDA {method} {path} -> HTTP {e.code}: {msg}") from None
            except (urllib.error.URLError, TimeoutError) as e:
                if method == "GET" and attempt < retries:
                    time.sleep(2 ** attempt)
                    continue
                raise BrokerError(f"OANDA {method} {path} failed: {e}") from None
        raise BrokerError("unreachable")
    return call


class OandaBroker(Broker):
    def __init__(self, environment: str, account_id: str, token: Optional[str] = None,
                 transport: Optional[Transport] = None):
        if environment not in HOSTS:
            raise ValueError(f"environment must be one of {list(HOSTS)}")
        if transport is None:
            if not token:
                raise BrokerError(f"no OANDA {environment} API token configured")
            transport = http_transport(HOSTS[environment], token)
        if not account_id:
            raise BrokerError(f"no OANDA {environment} account id configured")
        self.environment = environment
        self.account_id = account_id
        self._call = transport
        self._info: dict[str, InstrumentInfo] = {}

    def _acct(self, suffix: str) -> str:
        return f"/v3/accounts/{self.account_id}{suffix}"

    def account(self):
        a = self._call("GET", self._acct("/summary"), None, None)["account"]
        return AccountState(float(a["balance"]), float(a["NAV"]), a["currency"])

    def candles(self, instrument, granularity, count):
        r = self._call("GET", f"/v3/instruments/{instrument}/candles",
                       {"granularity": granularity, "count": min(count + 1, 5000), "price": "M"}, None)
        out = []
        for c in r.get("candles", []):
            if not c.get("complete"):
                continue
            m = c["mid"]
            out.append(Candle(parse_time(c["time"]), float(m["o"]), float(m["h"]), float(m["l"]),
                              float(m["c"]), int(c.get("volume", 0))))
        return out[-count:]

    def _pricing(self, instrument):
        r = self._call("GET", self._acct("/pricing"),
                       {"instruments": instrument, "includeHomeConversions": "true"}, None)
        prices = r.get("prices") or []
        if not prices:
            raise BrokerError(f"no price returned for {instrument}")
        return prices[0], r.get("homeConversions") or []

    def price(self, instrument):
        p, _ = self._pricing(instrument)
        return Quote(instrument, float(p["bids"][0]["price"]), float(p["asks"][0]["price"]),
                     bool(p.get("tradeable", True)))

    def instrument_info(self, instrument):
        if instrument not in self._info:
            r = self._call("GET", self._acct("/instruments"), {"instruments": instrument}, None)
            i = r["instruments"][0]
            self._info[instrument] = InstrumentInfo(
                instrument, int(i["pipLocation"]), int(i["displayPrecision"]),
                max(1, int(float(i.get("minimumTradeSize", "1")))),
            )
        return self._info[instrument]

    def open_trades(self):
        r = self._call("GET", self._acct("/openTrades"), None, None)
        out = []
        for t in r.get("trades", []):
            sl = t.get("stopLossOrder", {}).get("price")
            tp = t.get("takeProfitOrder", {}).get("price")
            out.append(BrokerTrade(
                t["id"], t["instrument"], int(float(t["currentUnits"])), float(t["price"]),
                float(sl) if sl else None, float(tp) if tp else None,
                parse_time(t["openTime"]) if t.get("openTime") else None,
            ))
        return out

    def market_order(self, instrument, units, stop_loss, take_profit):
        if stop_loss is None:
            raise BrokerError("refusing to place an order without a stop loss")
        info = self.instrument_info(instrument)
        order = {
            "type": "MARKET",
            "instrument": instrument,
            "units": str(int(units)),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"price": f"{info.round_price(stop_loss):.{info.display_precision}f}"},
        }
        if take_profit is not None:
            order["takeProfitOnFill"] = {"price": f"{info.round_price(take_profit):.{info.display_precision}f}"}
        try:
            r = self._call("POST", self._acct("/orders"), None, {"order": order})
        except BrokerError as e:
            return OrderResult(False, reason=str(e))
        fill = r.get("orderFillTransaction")
        if not fill or "tradeOpened" not in fill:
            cancel = r.get("orderCancelTransaction", {})
            return OrderResult(False, reason=cancel.get("reason", "order not filled"))
        opened = fill["tradeOpened"]
        return OrderResult(True, opened["tradeID"], float(fill["price"]), int(float(opened["units"])))

    def close_trade(self, trade_id):
        r = self._call("PUT", self._acct(f"/trades/{trade_id}/close"), None, {"units": "ALL"})
        fill = r.get("orderFillTransaction")
        if not fill:
            raise BrokerError(f"close of trade {trade_id} not filled: {r.get('orderCancelTransaction')}")
        return ClosedTrade(trade_id, float(fill["price"]), float(fill.get("pl", 0.0)), parse_time(fill["time"]))

    def closed_trade(self, trade_id):
        t = self._call("GET", self._acct(f"/trades/{trade_id}"), None, None)["trade"]
        if t.get("state") != "CLOSED":
            return None
        return ClosedTrade(trade_id, float(t.get("averageClosePrice", 0.0)), float(t.get("realizedPL", 0.0)),
                           parse_time(t["closeTime"]))

    def quote_to_account_rate(self, instrument):
        quote_ccy = instrument.split("_")[1]
        _, conversions = self._pricing(instrument)
        for c in conversions:
            if c.get("currency") == quote_ccy:
                # accountLoss is the less favourable rate: sizing with it never under-estimates risk
                return float(c.get("accountLoss") or c["accountGain"])
        raise BrokerError(f"no home conversion for {quote_ccy}")
