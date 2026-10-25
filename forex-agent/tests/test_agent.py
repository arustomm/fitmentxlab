import tempfile
import unittest
from pathlib import Path

from fxagent.agent import Agent
from fxagent.backtest import run_backtest, synthetic
from fxagent.brokers.paper import PaperBroker
from fxagent.cli import main
from fxagent.config import Config
from fxagent.journal import Journal
from fxagent.models import Action, Signal
from fxagent.risk import RiskConfig, RiskManager
from fxagent.strategy import Strategy
from tests.helpers import bar, flat


class ScriptedStrategy(Strategy):
    """Emits a given signal on a given bar index (by number of candles seen)."""
    name = "scripted"

    def __init__(self, script):
        super().__init__()
        self.script = script

    @property
    def warmup(self):
        return 1

    def evaluate(self, candles, position):
        return self.script.get(len(candles))


def make_agent(bars, script, risk=None, kill=None):
    broker = PaperBroker({"EUR_USD": bars}, spread_pips=0, slippage_pips=0)
    journal = Journal()
    agent = Agent(broker=broker, strategy=ScriptedStrategy(script), risk=RiskManager(risk or RiskConfig()),
                  journal=journal, mode="practice", instruments=["EUR_USD"], granularity="H1",
                  candle_count=1000, kill_switch_path=kill)
    return agent, broker, journal


def step(agent, broker):
    broker.advance()
    return agent.tick(broker.now)


class AgentTests(unittest.TestCase):
    def test_opens_with_stop_and_journals_take_profit(self):
        bars = flat(3) + [bar(3, 1.1, 1.1100, 1.0999, 1.11)]
        long = Signal(Action.OPEN_LONG, "test", stop_loss=1.0980, take_profit=1.1040)
        agent, broker, journal = make_agent(bars, {2: long})
        for _ in range(4):
            step(agent, broker)
        trades = journal.closed_trades("practice")
        self.assertEqual(len(trades), 1)
        t = trades[0]
        self.assertEqual(t["exit_reason"], "take_profit")
        self.assertAlmostEqual(t["stop_loss"], 1.0980)
        self.assertAlmostEqual(t["risk_amount"], 50.0, delta=1)  # 0.5% of 10k
        self.assertGreater(t["pnl"], 0)

    def test_close_signal_exits(self):
        long = Signal(Action.OPEN_LONG, "in", stop_loss=1.09, take_profit=1.2)
        agent, broker, journal = make_agent(flat(6), {2: long, 4: Signal(Action.CLOSE, "out")})
        for _ in range(6):
            step(agent, broker)
        self.assertEqual(journal.closed_trades("practice")[0]["exit_reason"], "signal: out")

    def test_does_not_touch_foreign_position(self):
        long = Signal(Action.OPEN_LONG, "in", stop_loss=1.09, take_profit=1.2)
        agent, broker, journal = make_agent(flat(5), {3: long, 4: Signal(Action.CLOSE, "out")})
        step(agent, broker)
        manual = broker.market_order("EUR_USD", 1000, 1.0, 1.3)  # opened by a human
        for _ in range(4):
            step(agent, broker)
        self.assertEqual([t.trade_id for t in broker.open_trades()], [manual.trade_id])
        self.assertEqual(journal.open_trades("practice"), [])

    def test_kill_switch_flattens_and_stops(self):
        with tempfile.TemporaryDirectory() as d:
            kill = Path(d) / "STOP"
            long = Signal(Action.OPEN_LONG, "in", stop_loss=1.09, take_profit=1.2)
            agent, broker, journal = make_agent(flat(5), {2: long}, kill=kill)
            step(agent, broker)
            step(agent, broker)
            self.assertEqual(len(broker.open_trades()), 1)
            kill.touch()
            self.assertFalse(step(agent, broker))
            self.assertEqual(broker.open_trades(), [])

    def test_drawdown_halt_is_permanent(self):
        crash = [bar(3, 1.0, 1.0, 0.95, 0.96)]
        long = Signal(Action.OPEN_LONG, "in", stop_loss=0.90, take_profit=1.5)
        risk = RiskConfig(risk_per_trade_pct=50, max_leverage=100, max_drawdown_pct=5, max_daily_loss_pct=99)
        agent, broker, journal = make_agent(flat(3, price=1.0) + crash + flat(3, price=0.96, start=4),
                                            {2: long}, risk=risk)
        results = [step(agent, broker) for _ in range(5)]
        self.assertFalse(results[-1])
        self.assertEqual(journal.get_state("practice", "halted"), "drawdown")
        self.assertEqual(broker.open_trades(), [])

    def test_backtest_runs_end_to_end(self):
        cfg = Config(candle_count=300)
        res = run_backtest(cfg, {"EUR_USD": synthetic(1500, seed=3)})
        self.assertGreater(res.metrics.trades, 0)
        self.assertAlmostEqual(res.final_balance, 10_000 + res.metrics.net_pnl, places=6)


class LiveGuardTests(unittest.TestCase):
    def test_live_refused_without_gate_and_flags(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "config.toml"
            cfg.write_text('[agent]\nmode = "practice"\ndata_dir = "data"\n')
            # no credentials needed: the guard must refuse before any broker is built
            self.assertEqual(main(["--config", str(cfg), "run", "--mode", "live", "--confirm-live"]), 1)


if __name__ == "__main__":
    unittest.main()
