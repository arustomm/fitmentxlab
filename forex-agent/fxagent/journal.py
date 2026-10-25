"""SQLite trade journal: every trade, equity snapshot and decision the agent makes.
The go-live gate reads its evidence from here."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT NOT NULL,
    strategy TEXT NOT NULL,
    broker_trade_id TEXT NOT NULL,
    instrument TEXT NOT NULL,
    side TEXT NOT NULL,
    units INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    entry_time TEXT NOT NULL,
    stop_loss REAL,
    take_profit REAL,
    risk_amount REAL,
    reason TEXT,
    exit_price REAL,
    exit_time TEXT,
    exit_reason TEXT,
    pnl REAL,
    status TEXT NOT NULL DEFAULT 'open'
);
CREATE INDEX IF NOT EXISTS trades_mode_status ON trades(mode, status);
CREATE TABLE IF NOT EXISTS equity (
    time TEXT NOT NULL,
    mode TEXT NOT NULL,
    balance REAL NOT NULL,
    nav REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    time TEXT NOT NULL,
    mode TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS state (
    mode TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (mode, key)
);
"""


def _iso(t: datetime) -> str:
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc).isoformat()


class Journal:
    def __init__(self, path: str | Path = ":memory:"):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    # trades
    def record_open(self, *, mode, strategy, broker_trade_id, instrument, side, units, entry_price,
                    entry_time, stop_loss, take_profit, risk_amount, reason) -> None:
        self.db.execute(
            "INSERT INTO trades (mode, strategy, broker_trade_id, instrument, side, units, entry_price,"
            " entry_time, stop_loss, take_profit, risk_amount, reason) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (mode, strategy, broker_trade_id, instrument, side, units, entry_price, _iso(entry_time),
             stop_loss, take_profit, risk_amount, reason),
        )
        self.db.commit()

    def record_close(self, mode, broker_trade_id, exit_price, exit_time, pnl, exit_reason) -> None:
        self.db.execute(
            "UPDATE trades SET exit_price=?, exit_time=?, pnl=?, exit_reason=?, status='closed'"
            " WHERE mode=? AND broker_trade_id=? AND status='open'",
            (exit_price, _iso(exit_time), pnl, exit_reason, mode, broker_trade_id),
        )
        self.db.commit()

    def open_trades(self, mode) -> list[sqlite3.Row]:
        return self.db.execute("SELECT * FROM trades WHERE mode=? AND status='open'", (mode,)).fetchall()

    def closed_trades(self, mode, strategy: Optional[str] = None) -> list[dict]:
        q, args = "SELECT * FROM trades WHERE mode=? AND status='closed'", [mode]
        if strategy:
            q += " AND strategy=?"
            args.append(strategy)
        return [dict(r) for r in self.db.execute(q + " ORDER BY exit_time, id", args)]

    # equity / events
    def record_equity(self, mode, time, balance, nav) -> None:
        self.db.execute("INSERT INTO equity VALUES (?,?,?,?)", (_iso(time), mode, balance, nav))
        self.db.commit()

    def first_equity(self, mode) -> Optional[float]:
        row = self.db.execute("SELECT balance FROM equity WHERE mode=? ORDER BY time LIMIT 1", (mode,)).fetchone()
        return row[0] if row else None

    def log_event(self, mode, time, level, message) -> None:
        self.db.execute("INSERT INTO events VALUES (?,?,?,?)", (_iso(time), mode, level, message))
        self.db.commit()

    def events(self, mode, limit=50) -> list[sqlite3.Row]:
        return self.db.execute(
            "SELECT * FROM events WHERE mode=? ORDER BY rowid DESC LIMIT ?", (mode, limit)
        ).fetchall()

    # key/value agent state
    def get_state(self, mode, key, default=None) -> Optional[str]:
        row = self.db.execute("SELECT value FROM state WHERE mode=? AND key=?", (mode, key)).fetchone()
        return row[0] if row else default

    def set_state(self, mode, key, value) -> None:
        self.db.execute(
            "INSERT INTO state VALUES (?,?,?) ON CONFLICT(mode, key) DO UPDATE SET value=excluded.value",
            (mode, key, None if value is None else str(value)),
        )
        self.db.commit()
