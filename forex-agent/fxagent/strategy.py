"""Trading strategies. A strategy looks at completed candles and the current position and
returns a Signal or None. It never sizes positions or talks to the broker."""

from __future__ import annotations

import hashlib
import json
from typing import Optional, Sequence

from fxagent.indicators import atr, ema
from fxagent.models import Action, Candle, Side, Signal


class Strategy:
    name = "base"

    def __init__(self, **params):
        self.params = params

    @property
    def warmup(self) -> int:
        raise NotImplementedError

    def evaluate(self, candles: Sequence[Candle], position: Optional[Side]) -> Optional[Signal]:
        raise NotImplementedError

    def fingerprint(self) -> str:
        """Stable id for this strategy + parameters. The go-live gate only counts trades whose
        fingerprint matches the strategy you are about to run live: change a parameter and the
        sandbox track record starts over."""
        blob = json.dumps({"name": self.name, "params": self.params}, sort_keys=True)
        return f"{self.name}-{hashlib.sha256(blob.encode()).hexdigest()[:10]}"


class EmaTrendStrategy(Strategy):
    """Trend following: enter when the fast EMA crosses the slow EMA in the direction of the
    long-term trend EMA. Stop and target are ATR multiples; exit early on the opposite cross."""

    name = "ema_trend"

    def __init__(self, fast=20, slow=50, trend=200, atr_period=14, stop_atr=2.0, target_atr=3.0):
        if not fast < slow <= trend:
            raise ValueError("need fast < slow <= trend")
        super().__init__(
            fast=fast, slow=slow, trend=trend, atr_period=atr_period, stop_atr=stop_atr, target_atr=target_atr
        )
        self.fast, self.slow, self.trend = fast, slow, trend
        self.atr_period, self.stop_atr, self.target_atr = atr_period, stop_atr, target_atr

    @property
    def warmup(self) -> int:
        return max(self.trend, self.atr_period) + 2

    def evaluate(self, candles, position):
        if len(candles) < self.warmup:
            return None
        closes = [c.close for c in candles]
        f, s, t = ema(closes, self.fast), ema(closes, self.slow), ema(closes, self.trend)
        a = atr(candles, self.atr_period)[-1]
        if None in (f[-1], f[-2], s[-1], s[-2], t[-1], a) or not a:
            return None
        crossed_up = f[-2] <= s[-2] and f[-1] > s[-1]
        crossed_down = f[-2] >= s[-2] and f[-1] < s[-1]
        close = closes[-1]

        if position is Side.LONG and crossed_down:
            return Signal(Action.CLOSE, "fast EMA crossed below slow EMA")
        if position is Side.SHORT and crossed_up:
            return Signal(Action.CLOSE, "fast EMA crossed above slow EMA")
        if position is not None:
            return None

        if crossed_up and close > t[-1]:
            return Signal(
                Action.OPEN_LONG,
                f"EMA{self.fast} crossed above EMA{self.slow}, price above EMA{self.trend}",
                stop_loss=close - self.stop_atr * a,
                take_profit=close + self.target_atr * a,
            )
        if crossed_down and close < t[-1]:
            return Signal(
                Action.OPEN_SHORT,
                f"EMA{self.fast} crossed below EMA{self.slow}, price below EMA{self.trend}",
                stop_loss=close + self.stop_atr * a,
                take_profit=close - self.target_atr * a,
            )
        return None


STRATEGIES = {EmaTrendStrategy.name: EmaTrendStrategy}


def build_strategy(spec: dict) -> Strategy:
    spec = dict(spec)
    name = spec.pop("name", "ema_trend")
    if name not in STRATEGIES:
        raise ValueError(f"unknown strategy {name!r}; available: {sorted(STRATEGIES)}")
    return STRATEGIES[name](**spec)
