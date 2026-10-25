"""Local paper broker that replays historical candles. Used for backtests and offline demos.

Fills: market orders fill at the last close plus half the spread plus slippage. Stops and
targets are checked against each new bar's range; when a bar touches both, the stop is assumed
to fill first (pessimistic), and a bar that gaps through a level fills at the bar's open."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fxagent.brokers.base import Broker, BrokerError
from fxagent.models import (
    AccountState, BrokerTrade, Candle, ClosedTrade, InstrumentInfo, OrderResult, Quote, quote_to_account_rate,
)


class PaperBroker(Broker):
    def __init__(self, history: dict[str, list[Candle]], balance: float = 10_000.0, currency: str = "USD",
                 spread_pips: float = 1.0, slippage_pips: float = 0.2):
        self._hist = {k: sorted(v, key=lambda c: c.time) for k, v in history.items()}
        self._times = sorted({c.time for cs in self._hist.values() for c in cs})
        self._step = -1
        self._cursor = {k: -1 for k in self._hist}
        self.balance = balance
        self.currency = currency
        self.spread_pips = spread_pips
        self.slippage_pips = slippage_pips
        self._open: dict[str, BrokerTrade] = {}
        self._closed: dict[str, ClosedTrade] = {}
        self._next_id = 1

    # clock
    @property
    def now(self) -> Optional[datetime]:
        return self._times[self._step] if self._step >= 0 else None

    def advance(self) -> bool:
        """Move the clock to the next bar. Returns False when history is exhausted."""
        if self._step + 1 >= len(self._times):
            return False
        self._step += 1
        t = self._times[self._step]
        for inst, cs in self._hist.items():
            moved = False
            while self._cursor[inst] + 1 < len(cs) and cs[self._cursor[inst] + 1].time <= t:
                self._cursor[inst] += 1
                moved = True
            if moved:
                self._process_bar(inst, cs[self._cursor[inst]])
        return True

    def _half_spread(self, inst: str) -> float:
        return self.spread_pips * self.instrument_info(inst).pip_size / 2

    def _last(self, inst: str) -> Optional[Candle]:
        i = self._cursor.get(inst, -1)
        return self._hist[inst][i] if i >= 0 else None

    def _process_bar(self, inst: str, bar: Candle) -> None:
        h = self._half_spread(inst)
        for tid, t in list(self._open.items()):
            if t.instrument != inst:
                continue
            exit_price = None
            if t.units > 0:  # long exits on the bid
                o, lo, hi = bar.open - h, bar.low - h, bar.high - h
                if t.stop_loss is not None and lo <= t.stop_loss:
                    exit_price, why = (o if o <= t.stop_loss else t.stop_loss), "stop_loss"
                elif t.take_profit is not None and hi >= t.take_profit:
                    exit_price, why = (o if o >= t.take_profit else t.take_profit), "take_profit"
            else:  # short exits on the ask
                o, lo, hi = bar.open + h, bar.low + h, bar.high + h
                if t.stop_loss is not None and hi >= t.stop_loss:
                    exit_price, why = (o if o >= t.stop_loss else t.stop_loss), "stop_loss"
                elif t.take_profit is not None and lo <= t.take_profit:
                    exit_price, why = (o if o <= t.take_profit else t.take_profit), "take_profit"
            if exit_price is not None:
                self._settle(tid, exit_price, bar.time)

    def _settle(self, tid: str, exit_price: float, when: datetime) -> ClosedTrade:
        t = self._open.pop(tid)
        pnl = (exit_price - t.entry_price) * t.units * self.quote_to_account_rate(t.instrument)
        self.balance += pnl
        closed = ClosedTrade(tid, exit_price, pnl, when)
        self._closed[tid] = closed
        return closed

    # Broker interface
    def account(self) -> AccountState:
        upl = 0.0
        for t in self._open.values():
            q = self.price(t.instrument)
            mark = q.bid if t.units > 0 else q.ask
            upl += (mark - t.entry_price) * t.units * self.quote_to_account_rate(t.instrument)
        return AccountState(self.balance, self.balance + upl, self.currency)

    def candles(self, instrument, granularity, count):
        i = self._cursor.get(instrument, -1)
        if i < 0:
            return []
        return self._hist[instrument][max(0, i + 1 - count): i + 1]

    def price(self, instrument):
        bar = self._last(instrument)
        if bar is None:
            raise BrokerError(f"no price for {instrument} yet")
        h = self._half_spread(instrument)
        return Quote(instrument, bar.close - h, bar.close + h, True)

    def instrument_info(self, instrument):
        return InstrumentInfo.default_for(instrument)

    def open_trades(self):
        return list(self._open.values())

    def market_order(self, instrument, units, stop_loss, take_profit):
        if units == 0:
            return OrderResult(False, reason="zero units")
        q = self.price(instrument)
        info = self.instrument_info(instrument)
        slip = self.slippage_pips * info.pip_size
        fill = round(q.ask + slip if units > 0 else q.bid - slip, info.display_precision + 1)
        tid = str(self._next_id)
        self._next_id += 1
        self._open[tid] = BrokerTrade(tid, instrument, units, fill, stop_loss, take_profit, self.now)
        return OrderResult(True, tid, fill, units)

    def close_trade(self, trade_id):
        t = self._open.get(trade_id)
        if t is None:
            return None
        q = self.price(t.instrument)
        return self._settle(trade_id, q.bid if t.units > 0 else q.ask, self.now)

    def closed_trade(self, trade_id):
        return self._closed.get(trade_id)

    def quote_to_account_rate(self, instrument):
        def mid(pair):
            bar = self._last(pair) if pair in self._hist else None
            return bar.close if bar else None
        return quote_to_account_rate(instrument, self.currency, mid)
