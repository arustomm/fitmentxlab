import math
import unittest

from fxagent.gate import GateConfig, evaluate
from fxagent.indicators import atr, ema
from fxagent.models import InstrumentInfo, Quote, quote_to_account_rate
from fxagent.performance import compute
from fxagent.risk import RiskConfig, RiskManager
from fxagent.strategy import EmaTrendStrategy, build_strategy
from tests.helpers import bar


class IndicatorTests(unittest.TestCase):
    def test_ema_seeds_with_sma(self):
        out = ema([1, 2, 3, 4, 5], 3)
        self.assertEqual(out[:2], [None, None])
        self.assertAlmostEqual(out[2], 2.0)
        self.assertAlmostEqual(out[3], 3.0)
        self.assertAlmostEqual(out[4], 4.0)

    def test_atr_constant_range(self):
        candles = [bar(i, 1.0, 1.01, 0.99, 1.0) for i in range(20)]
        self.assertAlmostEqual(atr(candles, 14)[-1], 0.02)


class RiskTests(unittest.TestCase):
    info = InstrumentInfo.default_for("EUR_USD")

    def test_sizes_to_risk_fraction(self):
        rm = RiskManager(RiskConfig(risk_per_trade_pct=0.5, max_leverage=100))
        units = rm.position_size(10_000, 1.1000, 1.0980, 1.0, self.info)  # 20 pip stop
        self.assertAlmostEqual(units, 25_000, delta=1)
        self.assertAlmostEqual(rm.risk_amount(units, 1.1, 1.098, 1.0), 50.0, delta=0.01)

    def test_live_multiplier_halves_risk(self):
        cfg = RiskConfig(risk_per_trade_pct=0.5, max_leverage=100, live_risk_multiplier=0.5)
        self.assertAlmostEqual(RiskManager(cfg, live=True).position_size(10_000, 1.1, 1.098, 1.0, self.info), 12_500, delta=1)

    def test_leverage_cap(self):
        rm = RiskManager(RiskConfig(risk_per_trade_pct=5, max_leverage=2))
        self.assertEqual(rm.position_size(10_000, 1.0, 0.9999, 1.0, self.info), 20_000)

    def test_zero_stop_distance_is_no_trade(self):
        self.assertEqual(RiskManager(RiskConfig()).position_size(10_000, 1.1, 1.1, 1.0, self.info), 0)

    def test_entry_filters(self):
        rm = RiskManager(RiskConfig(max_spread_pips=2, max_open_trades=1))
        self.assertTrue(rm.entry_allowed(0, Quote("EUR_USD", 1.1, 1.1001), self.info)[0])
        self.assertFalse(rm.entry_allowed(0, Quote("EUR_USD", 1.1, 1.1003), self.info)[0])
        self.assertFalse(rm.entry_allowed(1, Quote("EUR_USD", 1.1, 1.1001), self.info)[0])
        self.assertFalse(rm.entry_allowed(0, Quote("EUR_USD", 1.1, 1.1001, tradeable=False), self.info)[0])

    def test_circuit_breakers(self):
        rm = RiskManager(RiskConfig(max_daily_loss_pct=2, max_drawdown_pct=10))
        self.assertIsNone(rm.circuit_breaker(9_900, 10_000, 10_000))
        self.assertEqual(rm.circuit_breaker(9_790, 10_000, 10_000)[0], "daily")
        self.assertEqual(rm.circuit_breaker(8_990, 9_000, 10_000)[0], "drawdown")


class ConversionTests(unittest.TestCase):
    def test_conversions(self):
        prices = {"USD_JPY": 150.0, "GBP_USD": 1.25}
        f = prices.get
        self.assertEqual(quote_to_account_rate("EUR_USD", "USD", f), 1.0)
        self.assertAlmostEqual(quote_to_account_rate("USD_JPY", "USD", f), 1 / 150)
        self.assertAlmostEqual(quote_to_account_rate("EUR_GBP", "USD", f), 1.25)
        with self.assertRaises(ValueError):
            quote_to_account_rate("EUR_CHF", "USD", f)


class StrategyTests(unittest.TestCase):
    def test_fingerprint_changes_with_params(self):
        a = build_strategy({"name": "ema_trend"}).fingerprint()
        self.assertEqual(a, build_strategy({"name": "ema_trend"}).fingerprint())
        self.assertNotEqual(a, build_strategy({"name": "ema_trend", "stop_atr": 2.5}).fingerprint())

    def test_long_signal_on_bullish_cross_with_mandatory_stop(self):
        s = EmaTrendStrategy(fast=3, slow=5, trend=8, atr_period=3)
        # long uptrend, a dip that pulls fast below slow, then a sharp recovery -> cross up
        closes = [1.0 + 0.01 * i for i in range(20)] + [1.12, 1.10, 1.08, 1.30]
        candles = [bar(i, c, c + 0.005, c - 0.005, c) for i, c in enumerate(closes)]
        sig = s.evaluate(candles, None)
        self.assertIsNotNone(sig)
        self.assertEqual(sig.action.value, "open_long")
        self.assertLess(sig.stop_loss, closes[-1])
        self.assertGreater(sig.take_profit, closes[-1])

    def test_unknown_strategy(self):
        with self.assertRaises(ValueError):
            build_strategy({"name": "nope"})


def _trades(pnls, risk=50.0, days_apart=1.0):
    from datetime import datetime, timedelta, timezone
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [{"pnl": p, "risk_amount": risk, "entry_time": (t0 + timedelta(days=i * days_apart)).isoformat(),
             "exit_time": (t0 + timedelta(days=i * days_apart, hours=5)).isoformat()} for i, p in enumerate(pnls)]


class PerformanceAndGateTests(unittest.TestCase):
    def test_metrics(self):
        m = compute(_trades([100, -50, 100, -50]), 10_000)
        self.assertEqual(m.trades, 4)
        self.assertAlmostEqual(m.profit_factor, 2.0)
        self.assertAlmostEqual(m.net_pnl, 100)
        self.assertAlmostEqual(m.avg_r, 0.5)
        self.assertAlmostEqual(m.max_drawdown_pct, 50 / 10_100 * 100)

    def test_no_losses_is_infinite_profit_factor(self):
        self.assertTrue(math.isinf(compute(_trades([10, 10]), 1000).profit_factor))

    def test_gate_rejects_short_record(self):
        g = evaluate(_trades([75, -50] * 5), 10_000, GateConfig())
        self.assertFalse(g.passed)
        failed = {name for name, ok, _ in g.checks if not ok}
        self.assertIn("enough trades", failed)
        self.assertIn("enough time", failed)

    def test_gate_rejects_unprofitable(self):
        g = evaluate(_trades([50, -60] * 40), 10_000, GateConfig())
        self.assertFalse(g.passed)

    def test_gate_passes_strong_record(self):
        g = evaluate(_trades([75, 75, -50] * 25), 10_000, GateConfig())
        self.assertTrue(g.passed, g.report())


if __name__ == "__main__":
    unittest.main()
