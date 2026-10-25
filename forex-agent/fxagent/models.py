"""Plain data types shared by brokers, strategies, the risk manager and the agent."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Optional


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"

    @property
    def sign(self) -> int:
        return 1 if self is Side.LONG else -1

    @staticmethod
    def from_units(units: float) -> "Side":
        return Side.LONG if units > 0 else Side.SHORT


class Action(str, Enum):
    OPEN_LONG = "open_long"
    OPEN_SHORT = "open_short"
    CLOSE = "close"


@dataclass(frozen=True)
class Candle:
    """A completed mid-price candle. `time` is the candle's open time (UTC)."""

    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int = 0


@dataclass(frozen=True)
class Quote:
    instrument: str
    bid: float
    ask: float
    tradeable: bool = True

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread(self) -> float:
        return self.ask - self.bid


@dataclass(frozen=True)
class InstrumentInfo:
    name: str
    pip_location: int
    display_precision: int
    min_units: int = 1

    @property
    def pip_size(self) -> float:
        return 10.0 ** self.pip_location

    def round_price(self, price: float) -> float:
        return round(price, self.display_precision)

    @staticmethod
    def default_for(instrument: str) -> "InstrumentInfo":
        quote = instrument.split("_")[1]
        if quote == "JPY":
            return InstrumentInfo(instrument, pip_location=-2, display_precision=3)
        return InstrumentInfo(instrument, pip_location=-4, display_precision=5)


@dataclass
class AccountState:
    balance: float
    nav: float
    currency: str


@dataclass
class BrokerTrade:
    trade_id: str
    instrument: str
    units: int  # signed: positive long, negative short
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    open_time: Optional[datetime] = None

    @property
    def side(self) -> Side:
        return Side.from_units(self.units)


@dataclass
class OrderResult:
    ok: bool
    trade_id: Optional[str] = None
    price: Optional[float] = None
    units: int = 0
    reason: str = ""


@dataclass
class ClosedTrade:
    trade_id: str
    exit_price: float
    pnl: float
    exit_time: datetime


@dataclass
class Signal:
    action: Action
    reason: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


def quote_to_account_rate(
    instrument: str, account_ccy: str, price_of: Callable[[str], Optional[float]]
) -> float:
    """How many units of account currency one unit of the instrument's quote currency is worth."""
    base, quote = instrument.split("_")
    if quote == account_ccy:
        return 1.0
    if base == account_ccy:
        p = price_of(instrument)
        if p:
            return 1.0 / p
    p = price_of(f"{quote}_{account_ccy}")
    if p:
        return p
    p = price_of(f"{account_ccy}_{quote}")
    if p:
        return 1.0 / p
    raise ValueError(f"cannot convert {quote} to {account_ccy}: no price for a conversion pair")
