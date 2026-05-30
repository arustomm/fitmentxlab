"""SQLite-backed upload result tracker."""
from __future__ import annotations
import sqlite3
from datetime import datetime
from pathlib import Path
from .models import UploadResult

DB_PATH = Path("upload_tracker.db")


def _conn(db_path: Path = DB_PATH) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    return con


def init_db(db_path: Path = DB_PATH) -> None:
    with _conn(db_path) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sku         TEXT NOT NULL,
            title       TEXT,
            status      TEXT NOT NULL,
            ebay_item_id TEXT,
            ebay_url    TEXT,
            sale_price  REAL,
            error       TEXT,
            warnings    TEXT,
            uploaded_at TEXT NOT NULL
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_sku ON uploads(sku)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_status ON uploads(status)")


def save_result(result: UploadResult, db_path: Path = DB_PATH) -> None:
    with _conn(db_path) as con:
        con.execute("""
        INSERT INTO uploads (sku, title, status, ebay_item_id, ebay_url,
                             sale_price, error, warnings, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            result.sku,
            result.title,
            result.status,
            result.ebay_item_id,
            result.ebay_url,
            result.sale_price,
            result.error,
            "; ".join(result.warnings),
            datetime.utcnow().isoformat(),
        ))


def is_already_live(sku: str, db_path: Path = DB_PATH) -> bool:
    with _conn(db_path) as con:
        row = con.execute(
            "SELECT id FROM uploads WHERE sku=? AND status='success' LIMIT 1", (sku,)
        ).fetchone()
        return row is not None


def get_failed_skus(db_path: Path = DB_PATH) -> list[str]:
    with _conn(db_path) as con:
        rows = con.execute(
            "SELECT DISTINCT sku FROM uploads WHERE status='failed'"
        ).fetchall()
        return [r["sku"] for r in rows]


def summary(db_path: Path = DB_PATH) -> dict[str, int]:
    with _conn(db_path) as con:
        rows = con.execute(
            "SELECT status, COUNT(*) as cnt FROM uploads GROUP BY status"
        ).fetchall()
        return {r["status"]: r["cnt"] for r in rows}
