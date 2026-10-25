"""The go-live gate. Live trading is refused unless the sandbox (practice) record for the
exact strategy fingerprint you are about to run passes every check here."""

from __future__ import annotations

from dataclasses import dataclass, field

from fxagent.performance import Metrics, compute


@dataclass
class GateConfig:
    min_trades: int = 50
    min_days: float = 30.0
    min_profit_factor: float = 1.3
    max_drawdown_pct: float = 10.0
    min_expectancy_tstat: float = 2.0


@dataclass
class GateResult:
    passed: bool
    metrics: Metrics
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def report(self) -> str:
        lines = [f"Go-live gate: {'PASSED' if self.passed else 'NOT PASSED'}"]
        for name, ok, detail in self.checks:
            lines.append(f"  [{'x' if ok else ' '}] {name}: {detail}")
        return "\n".join(lines)


def evaluate(trades: list[dict], initial_equity: float, cfg: GateConfig) -> GateResult:
    m = compute(trades, initial_equity)
    checks = [
        ("enough trades", m.trades >= cfg.min_trades, f"{m.trades} / {cfg.min_trades}"),
        ("enough time", m.days >= cfg.min_days, f"{m.days:.1f} / {cfg.min_days} days"),
        ("profitable", m.net_pnl > 0, f"net {m.net_pnl:,.2f}"),
        ("profit factor", m.profit_factor >= cfg.min_profit_factor,
         f"{m.profit_factor:.2f} >= {cfg.min_profit_factor}"),
        ("drawdown", m.max_drawdown_pct <= cfg.max_drawdown_pct,
         f"{m.max_drawdown_pct:.2f}% <= {cfg.max_drawdown_pct}%"),
        ("edge is not luck", m.expectancy_tstat >= cfg.min_expectancy_tstat,
         f"t={m.expectancy_tstat:.2f} >= {cfg.min_expectancy_tstat}"),
    ]
    return GateResult(all(ok for _, ok, _ in checks), m, checks)
