"""Position sizing and circuit breakers. Every order the agent places goes through here."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fxagent.models import InstrumentInfo, Quote


@dataclass
class RiskConfig:
    risk_per_trade_pct: float = 0.5   # % of equity lost if the stop is hit
    max_open_trades: int = 3
    max_daily_loss_pct: float = 2.0   # halt new trading for the rest of the UTC day
    max_drawdown_pct: float = 10.0    # halt until a human runs `fxagent resume`
    max_spread_pips: float = 2.5      # skip entries when the spread is wider than this
    max_leverage: float = 10.0        # cap on notional / equity per trade
    live_risk_multiplier: float = 0.5  # live starts smaller than practice


class RiskManager:
    def __init__(self, cfg: RiskConfig, live: bool = False):
        self.cfg = cfg
        self.live = live

    @property
    def risk_fraction(self) -> float:
        mult = self.cfg.live_risk_multiplier if self.live else 1.0
        return self.cfg.risk_per_trade_pct / 100.0 * mult

    def position_size(
        self, equity: float, entry: float, stop: float, quote_to_account: float, info: InstrumentInfo
    ) -> int:
        """Units such that hitting the stop loses about risk_fraction of equity, capped by leverage."""
        dist = abs(entry - stop)
        if equity <= 0 or dist <= 0 or entry <= 0 or quote_to_account <= 0:
            return 0
        units = (equity * self.risk_fraction) / (dist * quote_to_account)
        max_units = equity * self.cfg.max_leverage / (entry * quote_to_account)
        units = int(min(units, max_units))
        return units if units >= info.min_units else 0

    @staticmethod
    def risk_amount(units: int, entry: float, stop: float, quote_to_account: float) -> float:
        return abs(units) * abs(entry - stop) * quote_to_account

    def entry_allowed(self, open_trades: int, quote: Quote, info: InstrumentInfo) -> tuple[bool, str]:
        if not quote.tradeable:
            return False, "market not tradeable"
        if open_trades >= self.cfg.max_open_trades:
            return False, f"max open trades ({self.cfg.max_open_trades}) reached"
        spread_pips = quote.spread / info.pip_size
        if spread_pips > self.cfg.max_spread_pips:
            return False, f"spread {spread_pips:.1f} pips > {self.cfg.max_spread_pips}"
        return True, ""

    def circuit_breaker(self, nav: float, day_start: float, peak: float) -> Optional[tuple[str, str]]:
        """Returns (kind, message) when trading must stop; kind is 'daily' or 'drawdown'."""
        if peak > 0:
            dd = (peak - nav) / peak * 100
            if dd >= self.cfg.max_drawdown_pct:
                return "drawdown", f"drawdown {dd:.2f}% >= {self.cfg.max_drawdown_pct}% from peak {peak:.2f}"
        if day_start > 0:
            loss = (day_start - nav) / day_start * 100
            if loss >= self.cfg.max_daily_loss_pct:
                return "daily", f"daily loss {loss:.2f}% >= {self.cfg.max_daily_loss_pct}%"
        return None
