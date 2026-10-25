"""Performance statistics over closed trades."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Sequence


@dataclass
class Metrics:
    trades: int
    wins: int
    losses: int
    win_rate: float
    net_pnl: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    expectancy: float        # mean pnl per trade, account currency
    avg_r: float             # mean pnl per trade in units of risk taken
    expectancy_tstat: float  # t-statistic of mean R: how far from luck the edge is
    max_drawdown_pct: float
    return_pct: float
    days: float

    def as_dict(self) -> dict:
        return asdict(self)


def compute(trades: Sequence[dict], initial_equity: float) -> Metrics:
    pnls = [float(t["pnl"]) for t in trades]
    n = len(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    gp, gl = sum(wins), -sum(losses)
    if gl > 0:
        pf = gp / gl
    else:
        pf = math.inf if gp > 0 else 0.0

    rs = [float(t["pnl"]) / t["risk_amount"] for t in trades if t.get("risk_amount")]
    avg_r = sum(rs) / len(rs) if rs else 0.0
    tstat = 0.0
    if len(rs) > 1:
        sd = math.sqrt(sum((r - avg_r) ** 2 for r in rs) / (len(rs) - 1))
        tstat = avg_r / sd * math.sqrt(len(rs)) if sd > 0 else 0.0

    equity = peak = initial_equity
    max_dd = 0.0
    for p in pnls:
        equity += p
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak * 100)

    days = 0.0
    if trades:
        start = datetime.fromisoformat(trades[0]["entry_time"])
        end = datetime.fromisoformat(trades[-1]["exit_time"])
        days = max(0.0, (end - start).total_seconds() / 86400)

    net = sum(pnls)
    return Metrics(
        trades=n,
        wins=len(wins),
        losses=len(losses),
        win_rate=len(wins) / n if n else 0.0,
        net_pnl=net,
        gross_profit=gp,
        gross_loss=gl,
        profit_factor=pf,
        expectancy=net / n if n else 0.0,
        avg_r=avg_r,
        expectancy_tstat=tstat,
        max_drawdown_pct=max_dd,
        return_pct=net / initial_equity * 100 if initial_equity else 0.0,
        days=days,
    )


def format_metrics(m: Metrics) -> str:
    pf = "inf" if math.isinf(m.profit_factor) else f"{m.profit_factor:.2f}"
    return "\n".join([
        f"  trades            {m.trades}  ({m.wins} W / {m.losses} L, win rate {m.win_rate:.1%})",
        f"  net P&L           {m.net_pnl:,.2f}  ({m.return_pct:+.2f}%)",
        f"  profit factor     {pf}",
        f"  expectancy        {m.expectancy:,.2f} per trade  ({m.avg_r:+.3f} R)",
        f"  edge t-stat       {m.expectancy_tstat:.2f}",
        f"  max drawdown      {m.max_drawdown_pct:.2f}%",
        f"  period            {m.days:.1f} days",
    ])
