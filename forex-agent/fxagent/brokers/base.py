"""The broker interface. The agent only talks to brokers through these methods, so the same
agent code runs against the local paper simulator, the OANDA practice account and OANDA live."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from fxagent.models import AccountState, BrokerTrade, Candle, ClosedTrade, InstrumentInfo, OrderResult, Quote


class BrokerError(Exception):
    pass


class Broker(ABC):
    @abstractmethod
    def account(self) -> AccountState: ...

    @abstractmethod
    def candles(self, instrument: str, granularity: str, count: int) -> list[Candle]:
        """Most recent *completed* candles, oldest first."""

    @abstractmethod
    def price(self, instrument: str) -> Quote: ...

    @abstractmethod
    def instrument_info(self, instrument: str) -> InstrumentInfo: ...

    @abstractmethod
    def open_trades(self) -> list[BrokerTrade]: ...

    @abstractmethod
    def market_order(
        self, instrument: str, units: int, stop_loss: float, take_profit: Optional[float]
    ) -> OrderResult:
        """Signed units. The stop loss is mandatory and attached on fill."""

    @abstractmethod
    def close_trade(self, trade_id: str) -> Optional[ClosedTrade]: ...

    @abstractmethod
    def closed_trade(self, trade_id: str) -> Optional[ClosedTrade]:
        """Details of a trade closed broker-side (stop loss / take profit hit)."""

    @abstractmethod
    def quote_to_account_rate(self, instrument: str) -> float: ...
