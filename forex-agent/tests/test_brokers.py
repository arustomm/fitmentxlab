import unittest

from fxagent.brokers.base import BrokerError
from fxagent.brokers.oanda import OandaBroker, parse_time
from fxagent.brokers.paper import PaperBroker
from tests.helpers import bar, flat


class PaperBrokerTests(unittest.TestCase):
    def make(self, bars, inst="EUR_USD", **kw):
        b = PaperBroker({inst: bars}, balance=10_000, spread_pips=0, slippage_pips=0, **kw)
        b.advance()
        return b

    def test_take_profit_fills(self):
        b = self.make(flat(1) + [bar(1, 1.1, 1.1050, 1.0995, 1.104)])
        res = b.market_order("EUR_USD", 10_000, stop_loss=1.0980, take_profit=1.1040)
        self.assertTrue(res.ok)
        b.advance()
        self.assertEqual(b.open_trades(), [])
        closed = b.closed_trade(res.trade_id)
        self.assertAlmostEqual(closed.exit_price, 1.1040)
        self.assertAlmostEqual(closed.pnl, 40.0)
        self.assertAlmostEqual(b.balance, 10_040.0)

    def test_stop_wins_when_bar_hits_both(self):
        b = self.make(flat(1) + [bar(1, 1.1, 1.1100, 1.0900, 1.1)])
        res = b.market_order("EUR_USD", 10_000, stop_loss=1.0980, take_profit=1.1040)
        b.advance()
        self.assertAlmostEqual(b.closed_trade(res.trade_id).exit_price, 1.0980)

    def test_gap_through_stop_fills_at_open(self):
        b = self.make(flat(1) + [bar(1, 1.0950, 1.0960, 1.0940, 1.095)])
        res = b.market_order("EUR_USD", 10_000, stop_loss=1.0980, take_profit=1.1040)
        b.advance()
        self.assertAlmostEqual(b.closed_trade(res.trade_id).exit_price, 1.0950)

    def test_short_stop_and_jpy_pnl_in_usd(self):
        b = self.make([bar(0, 150, 150.01, 149.99, 150)] + [bar(1, 150, 150.6, 149.9, 150.5)], inst="USD_JPY")
        res = b.market_order("USD_JPY", -10_000, stop_loss=150.5, take_profit=149.0)
        b.advance()
        closed = b.closed_trade(res.trade_id)
        # lost 0.5 JPY * 10k units = 5000 JPY at ~150.5 -> ~33.2 USD
        self.assertAlmostEqual(closed.pnl, -5000 / 150.5, places=4)

    def test_spread_costs_money(self):
        b = PaperBroker({"EUR_USD": flat(2)}, spread_pips=1.0, slippage_pips=0)
        b.advance()
        res = b.market_order("EUR_USD", 10_000, 1.09, 1.12)
        closed = b.close_trade(res.trade_id)
        self.assertAlmostEqual(closed.pnl, -1.0)

    def test_candles_never_leak_the_future(self):
        b = PaperBroker({"EUR_USD": flat(10)})
        for _ in range(4):
            b.advance()
        cs = b.candles("EUR_USD", "H1", 100)
        self.assertEqual(len(cs), 4)
        self.assertEqual(cs[-1].time, b.now)


class FakeTransport:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def __call__(self, method, path, params, body):
        self.calls.append((method, path, params, body))
        for (m, suffix), resp in self.routes.items():
            if m == method and path.endswith(suffix):
                return resp(params, body) if callable(resp) else resp
        raise BrokerError(f"no route for {method} {path}")


INSTRUMENTS = {"instruments": [{"name": "EUR_USD", "pipLocation": -4, "displayPrecision": 5,
                                "minimumTradeSize": "1"}]}


class OandaBrokerTests(unittest.TestCase):
    def broker(self, routes):
        routes = {("GET", "/instruments"): INSTRUMENTS, **routes}
        t = FakeTransport(routes)
        return OandaBroker("practice", "101-001-1", transport=t), t

    def test_parse_nanosecond_time(self):
        self.assertEqual(parse_time("2024-01-02T03:00:00.000000000Z").hour, 3)

    def test_requires_credentials(self):
        with self.assertRaises(BrokerError):
            OandaBroker("practice", "101-001-1", token="")

    def test_drops_incomplete_candles(self):
        candles = {"candles": [
            {"complete": True, "time": "2024-01-01T00:00:00.000000000Z", "volume": 5,
             "mid": {"o": "1.1", "h": "1.2", "l": "1.0", "c": "1.15"}},
            {"complete": False, "time": "2024-01-01T01:00:00.000000000Z", "volume": 1,
             "mid": {"o": "1.15", "h": "1.2", "l": "1.1", "c": "1.16"}},
        ]}
        b, _ = self.broker({("GET", "/candles"): candles})
        out = b.candles("EUR_USD", "H1", 10)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].close, 1.15)

    def test_market_order_attaches_rounded_stop_and_target(self):
        fill = {"orderFillTransaction": {"price": "1.10012", "tradeOpened": {"tradeID": "42", "units": "1000"}}}
        b, t = self.broker({("POST", "/orders"): fill})
        res = b.market_order("EUR_USD", 1000, stop_loss=1.0980123, take_profit=1.104)
        self.assertTrue(res.ok)
        self.assertEqual(res.trade_id, "42")
        order = t.calls[-1][3]["order"]
        self.assertEqual(order["stopLossOnFill"], {"price": "1.09801"})
        self.assertEqual(order["takeProfitOnFill"], {"price": "1.10400"})
        self.assertEqual(order["units"], "1000")

    def test_refuses_order_without_stop(self):
        b, _ = self.broker({})
        with self.assertRaises(BrokerError):
            b.market_order("EUR_USD", 1000, stop_loss=None, take_profit=None)

    def test_cancelled_order_is_not_ok(self):
        b, _ = self.broker({("POST", "/orders"): {"orderCancelTransaction": {"reason": "MARKET_HALTED"}}})
        res = b.market_order("EUR_USD", 1000, 1.09, None)
        self.assertFalse(res.ok)
        self.assertEqual(res.reason, "MARKET_HALTED")

    def test_home_conversion_uses_loss_rate(self):
        pricing = {"prices": [{"instrument": "USD_JPY", "bids": [{"price": "150.0"}], "asks": [{"price": "150.02"}]}],
                   "homeConversions": [{"currency": "JPY", "accountGain": "0.00666", "accountLoss": "0.00667"}]}
        b, _ = self.broker({("GET", "/pricing"): pricing})
        self.assertAlmostEqual(b.quote_to_account_rate("USD_JPY"), 0.00667)

    def test_closed_trade(self):
        b, _ = self.broker({("GET", "/trades/7"): {"trade": {"state": "CLOSED", "averageClosePrice": "1.1",
                                                             "realizedPL": "-12.5",
                                                             "closeTime": "2024-01-01T00:00:00Z"}}})
        self.assertAlmostEqual(b.closed_trade("7").pnl, -12.5)


if __name__ == "__main__":
    unittest.main()
