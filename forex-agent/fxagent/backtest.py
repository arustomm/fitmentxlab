"""Backtesting: replay history through the *same* Agent used for practice and live, against
the paper broker, then score the journal."""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fxagent.agent import Agent
from fxagent.brokers.paper import PaperBroker
from fxagent.config import Config
from fxagent.journal import Journal
from fxagent.models import Candle
from fxagent.performance import Metrics, compute
from fxagent.risk import RiskManager
from fxagent.strategy import build_strategy


def load_csv(path: str | Path) -> list[Candle]:
    """CSV with header: time,open,high,low,close[,volume]. time is ISO 8601 (UTC assumed)."""
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            t = datetime.fromisoformat(row["time"].replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            out.append(Candle(t, float(row["open"]), float(row["high"]), float(row["low"]),
                              float(row["close"]), int(float(row.get("volume") or 0))))
    return sorted(out, key=lambda c: c.time)


def save_csv(candles: list[Candle], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "open", "high", "low", "close", "volume"])
        for c in candles:
            w.writerow([c.time.isoformat(), c.open, c.high, c.low, c.close, c.volume])


def synthetic(n: int = 3000, start_price: float = 1.10, seed: int = 7, hours: int = 1) -> list[Candle]:
    """Random-walk candles with drifting regimes, for smoke-testing the pipeline.
    Results on synthetic data say nothing about real-market profitability."""
    rng = random.Random(seed)
    t = datetime(2024, 1, 1, tzinfo=timezone.utc)
    price, drift, out = start_price, 0.0, []
    vol = 0.0012 * math.sqrt(hours)
    for _ in range(n):
        if rng.random() < 0.01:
            drift = rng.gauss(0, vol / 8)
        o = price
        steps = [o]
        for _ in range(4):
            steps.append(steps[-1] * (1 + drift / 4 + rng.gauss(0, vol / 2)))
        c = steps[-1]
        out.append(Candle(t, round(o, 5), round(max(steps), 5), round(min(steps), 5), round(c, 5)))
        price = c
        t += timedelta(hours=hours)
        if t.weekday() >= 5:  # skip weekends like the real market
            t += timedelta(days=7 - t.weekday())
    return out


@dataclass
class BacktestResult:
    metrics: Metrics
    trades: list[dict]
    final_balance: float
    journal: Journal


def run_backtest(cfg: Config, history: dict[str, list[Candle]], balance: float = 10_000.0,
                 spread_pips: float = 1.0, slippage_pips: float = 0.2, currency: str = "USD") -> BacktestResult:
    broker = PaperBroker(history, balance=balance, currency=currency,
                         spread_pips=spread_pips, slippage_pips=slippage_pips)
    journal = Journal(":memory:")
    strategy = build_strategy(cfg.strategy)
    agent = Agent(broker=broker, strategy=strategy, risk=RiskManager(cfg.risk), journal=journal,
                  mode="backtest", instruments=list(history), granularity=cfg.granularity,
                  candle_count=cfg.candle_count, close_on_halt=cfg.close_on_halt)
    journal.record_equity("backtest", datetime(1970, 1, 1, tzinfo=timezone.utc), balance, balance)
    while broker.advance():
        if not agent.tick(broker.now):
            break
    for t in list(broker.open_trades()):  # mark-to-market whatever is still open at the end
        closed = broker.close_trade(t.trade_id)
        journal.record_close("backtest", t.trade_id, closed.exit_price, closed.exit_time, closed.pnl, "end_of_data")
    trades = journal.closed_trades("backtest")
    return BacktestResult(compute(trades, balance), trades, broker.balance, journal)
