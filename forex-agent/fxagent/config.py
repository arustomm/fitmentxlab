"""Configuration (config.toml) and credentials (environment variables or a .env file)."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

from fxagent.gate import GateConfig
from fxagent.risk import RiskConfig

MODES = ("practice", "live")


@dataclass
class Config:
    mode: str = "practice"
    instruments: list[str] = field(default_factory=lambda: ["EUR_USD", "GBP_USD", "USD_JPY"])
    granularity: str = "H1"
    poll_seconds: int = 30
    candle_count: int = 600  # history fed to the strategy each bar; identical in backtest and live
    data_dir: Path = Path("data")
    close_on_halt: bool = True
    strategy: dict = field(default_factory=lambda: {"name": "ema_trend"})
    risk: RiskConfig = field(default_factory=RiskConfig)
    gate: GateConfig = field(default_factory=GateConfig)

    @property
    def journal_path(self) -> Path:
        return self.data_dir / "journal.sqlite"

    @property
    def kill_switch_path(self) -> Path:
        return self.data_dir / "STOP"


def _pick(cls, table: dict):
    known = {f.name for f in fields(cls)}
    unknown = set(table) - known
    if unknown:
        raise ValueError(f"unknown {cls.__name__} keys: {sorted(unknown)}")
    return cls(**table)


def load_config(path: str | Path | None) -> Config:
    if path is None or not Path(path).exists():
        cfg = Config()
        base = Path.cwd()
    else:
        path = Path(path)
        base = path.parent
        raw = tomllib.loads(path.read_text())
        agent = dict(raw.get("agent", {}))
        if "data_dir" in agent:
            agent["data_dir"] = Path(agent["data_dir"])
        cfg = _pick(Config, agent)
        cfg.strategy = raw.get("strategy", cfg.strategy)
        cfg.risk = _pick(RiskConfig, raw.get("risk", {}))
        cfg.gate = _pick(GateConfig, raw.get("gate", {}))
    if not cfg.data_dir.is_absolute():
        cfg.data_dir = base / cfg.data_dir
    if cfg.mode not in MODES:
        raise ValueError(f"agent.mode must be one of {MODES}")
    load_dotenv(base / ".env")
    return cfg


def load_dotenv(path: Path) -> None:
    """Minimal .env loader: KEY=VALUE lines; real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def oanda_credentials(mode: str) -> tuple[str, str]:
    prefix = f"OANDA_{mode.upper()}"
    return os.environ.get(f"{prefix}_TOKEN", ""), os.environ.get(f"{prefix}_ACCOUNT_ID", "")
