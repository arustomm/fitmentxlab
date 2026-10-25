"""The watch agent. Each tick it checks safety rails, reconciles trades with the broker, and
on every newly completed candle asks the strategy what to do. The same `tick` drives
backtests (paper broker, simulated clock) and practice/live (OANDA, wall clock)."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fxagent.brokers.base import Broker, BrokerError
from fxagent.journal import Journal
from fxagent.models import Action, BrokerTrade, Side, Signal
from fxagent.risk import RiskManager
from fxagent.strategy import Strategy

log = logging.getLogger("fxagent")


class Agent:
    def __init__(self, *, broker: Broker, strategy: Strategy, risk: RiskManager, journal: Journal,
                 mode: str, instruments: list[str], granularity: str, candle_count: int,
                 kill_switch_path: Optional[Path] = None, close_on_halt: bool = True):
        self.broker = broker
        self.strategy = strategy
        self.risk = risk
        self.journal = journal
        self.mode = mode
        self.instruments = instruments
        self.granularity = granularity
        self.candle_count = max(candle_count, strategy.warmup)
        self.kill_switch_path = kill_switch_path
        self.close_on_halt = close_on_halt
        self.fingerprint = strategy.fingerprint()

    # helpers
    def _event(self, now, level, msg):
        getattr(log, level)(f"[{self.mode}] {msg}")
        self.journal.log_event(self.mode, now, level, msg)

    def _state(self, key, default=None):
        return self.journal.get_state(self.mode, key, default)

    def _set(self, key, value):
        self.journal.set_state(self.mode, key, value)

    def _my_open(self) -> dict[str, dict]:
        return {r["broker_trade_id"]: dict(r) for r in self.journal.open_trades(self.mode)}

    # main loop
    def run_forever(self, poll_seconds: int) -> None:
        self._event(datetime.now(timezone.utc), "info",
                    f"agent started: {self.fingerprint} on {', '.join(self.instruments)} {self.granularity}")
        while True:
            now = datetime.now(timezone.utc)
            try:
                if not self.tick(now):
                    return
            except BrokerError as e:
                self._event(now, "warning", f"broker error, will retry: {e}")
            except Exception as e:  # keep watching; a crash loop is worse than a logged error
                self._event(now, "error", f"unexpected error: {e!r}")
            time.sleep(poll_seconds)

    def tick(self, now: datetime) -> bool:
        """One pass. Returns False when the agent should stop (kill switch / permanent halt)."""
        if self.kill_switch_path and self.kill_switch_path.exists():
            self._halt(now, "kill switch file present")
            return False
        if self._state("halted") == "drawdown":
            return False

        self._sync_closed(now)
        acct = self.broker.account()
        day = now.astimezone(timezone.utc).date().isoformat()
        if self._state("day") != day:
            self._set("day", day)
            self._set("day_start_equity", acct.nav)
            if self._state("halted") == "daily":
                self._set("halted", None)
                self._event(now, "info", "new trading day, daily halt lifted")
        peak = max(float(self._state("peak_equity", acct.nav)), acct.nav)
        self._set("peak_equity", peak)

        if self._state("halted") == "daily":
            return True
        breach = self.risk.circuit_breaker(acct.nav, float(self._state("day_start_equity")), peak)
        if breach:
            kind, msg = breach
            self._set("halted", kind)
            self._halt(now, msg)
            return kind != "drawdown"

        processed = False
        for inst in self.instruments:
            processed |= self._on_instrument(inst, now)
        if processed:
            acct = self.broker.account()
            self.journal.record_equity(self.mode, now, acct.balance, acct.nav)
        return True

    def _halt(self, now, why):
        self._event(now, "warning", f"HALT: {why}")
        if self.close_on_halt:
            for tid in list(self._my_open()):
                self._close(tid, now, f"halt: {why}")

    def _sync_closed(self, now):
        """Record trades the broker closed on its own (stop loss or take profit hit)."""
        mine = self._my_open()
        if not mine:
            return
        live_ids = {t.trade_id for t in self.broker.open_trades()}
        for tid, row in mine.items():
            if tid in live_ids:
                continue
            closed = self.broker.closed_trade(tid)
            if closed is None:
                continue
            why = _exit_reason(row, closed.exit_price)
            self.journal.record_close(self.mode, tid, closed.exit_price, closed.exit_time, closed.pnl, why)
            self._event(now, "info", f"{row['instrument']} trade {tid} closed by {why}: pnl {closed.pnl:+.2f}")

    def _close(self, tid, now, why):
        closed = self.broker.close_trade(tid)
        if closed is None:
            return
        self.journal.record_close(self.mode, tid, closed.exit_price, closed.exit_time, closed.pnl, why)
        self._event(now, "info", f"closed trade {tid} ({why}): pnl {closed.pnl:+.2f}")

    def _on_instrument(self, inst: str, now: datetime) -> bool:
        candles = self.broker.candles(inst, self.granularity, self.candle_count)
        if not candles:
            return False
        last = candles[-1].time.isoformat()
        if self._state(f"last_bar:{inst}") == last:
            return False
        self._set(f"last_bar:{inst}", last)

        mine = self._my_open()
        broker_open = self.broker.open_trades()
        here = [t for t in broker_open if t.instrument == inst]
        foreign = [t for t in here if t.trade_id not in mine]
        if foreign:
            # someone else (you, manually) holds a position here: don't touch it, don't add to it
            return True
        current: Optional[BrokerTrade] = here[0] if here else None

        signal = self.strategy.evaluate(candles, current.side if current else None)
        if signal is None:
            return True
        if signal.action is Action.CLOSE:
            if current:
                self._close(current.trade_id, now, f"signal: {signal.reason}")
            return True
        if current is None:
            self._open(inst, signal, candles[-1].close, len(broker_open), now)
        return True

    def _open(self, inst: str, signal: Signal, ref_price: float, open_count: int, now: datetime):
        side = Side.LONG if signal.action is Action.OPEN_LONG else Side.SHORT
        info = self.broker.instrument_info(inst)
        quote = self.broker.price(inst)
        ok, why = self.risk.entry_allowed(open_count, quote, info)
        if not ok:
            self._event(now, "info", f"{inst} {side.value} signal skipped: {why}")
            return
        # keep the strategy's stop/target distances, re-anchored to the executable price
        entry = quote.ask if side is Side.LONG else quote.bid
        stop = entry + (signal.stop_loss - ref_price)
        target = entry + (signal.take_profit - ref_price) if signal.take_profit is not None else None
        q2a = self.broker.quote_to_account_rate(inst)
        acct = self.broker.account()
        units = self.risk.position_size(acct.nav, entry, stop, q2a, info)
        if units <= 0:
            self._event(now, "info", f"{inst} {side.value} signal skipped: position size rounds to zero")
            return
        stop, target = info.round_price(stop), (info.round_price(target) if target is not None else None)
        res = self.broker.market_order(inst, units * side.sign, stop, target)
        if not res.ok:
            self._event(now, "warning", f"{inst} {side.value} order rejected: {res.reason}")
            return
        risk_amt = self.risk.risk_amount(res.units, res.price, stop, q2a)
        self.journal.record_open(
            mode=self.mode, strategy=self.fingerprint, broker_trade_id=res.trade_id, instrument=inst,
            side=side.value, units=res.units, entry_price=res.price, entry_time=now, stop_loss=stop,
            take_profit=target, risk_amount=risk_amt, reason=signal.reason,
        )
        self._event(now, "info", f"opened {side.value} {abs(res.units)} {inst} @ {res.price} "
                                 f"SL {stop} TP {target} risk {risk_amt:.2f}: {signal.reason}")


def _exit_reason(row: dict, exit_price: float) -> str:
    sl, tp = row.get("stop_loss"), row.get("take_profit")
    if sl is not None and tp is not None:
        return "stop_loss" if abs(exit_price - sl) <= abs(exit_price - tp) else "take_profit"
    return "broker"
