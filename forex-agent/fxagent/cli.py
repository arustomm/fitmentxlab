"""Command line: python -m fxagent <command>.

  check      verify OANDA credentials and connectivity (practice by default)
  backtest   replay history (CSV, OANDA download, or synthetic) through the agent
  run        start the watch agent (practice by default; live is gated)
  report     performance of the journaled trades
  gate       show whether the practice record qualifies for live trading
  resume     clear a drawdown halt after you have reviewed what happened
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone

from fxagent.agent import Agent
from fxagent.backtest import load_csv, run_backtest, save_csv, synthetic
from fxagent.brokers.oanda import OandaBroker
from fxagent.config import Config, load_config, oanda_credentials
from fxagent.gate import evaluate
from fxagent.journal import Journal
from fxagent.performance import compute, format_metrics
from fxagent.risk import RiskManager
from fxagent.strategy import build_strategy

LIVE_ENV_FLAG = "FXAGENT_ALLOW_LIVE"


def _broker(mode: str) -> OandaBroker:
    token, account = oanda_credentials(mode)
    return OandaBroker(mode, account, token)


def practice_gate(cfg: Config, journal: Journal):
    fingerprint = build_strategy(cfg.strategy).fingerprint()
    trades = journal.closed_trades("practice", strategy=fingerprint)
    initial = journal.first_equity("practice") or 10_000.0
    return fingerprint, evaluate(trades, initial, cfg.gate)


def cmd_check(cfg, args):
    mode = args.mode or "practice"
    b = _broker(mode)
    a = b.account()
    print(f"OANDA {mode} account {b.account_id}: balance {a.balance:,.2f} {a.currency}, NAV {a.nav:,.2f}")
    for inst in cfg.instruments:
        q = b.price(inst)
        info = b.instrument_info(inst)
        print(f"  {inst}: bid {q.bid} ask {q.ask} spread {q.spread / info.pip_size:.1f} pips"
              f"{'' if q.tradeable else ' (market closed)'}")
    return 0


def cmd_backtest(cfg, args):
    instruments = args.instrument or cfg.instruments
    history = {}
    if args.csv:
        if len(args.csv) != len(instruments):
            print("give one --instrument per --csv file", file=sys.stderr)
            return 2
        history = {inst: load_csv(p) for inst, p in zip(instruments, args.csv)}
    elif args.fetch:
        b = _broker("practice")
        for inst in instruments:
            history[inst] = b.candles(inst, cfg.granularity, args.fetch)
            path = cfg.data_dir / "history" / f"{inst}_{cfg.granularity}.csv"
            save_csv(history[inst], path)
            print(f"downloaded {len(history[inst])} {cfg.granularity} candles for {inst} -> {path}")
    else:
        print("No data given: using SYNTHETIC random-walk candles. This only proves the plumbing works;"
              " it says nothing about real profitability.\n")
        starts = {"EUR_USD": 1.10, "GBP_USD": 1.27, "USD_JPY": 150.0}
        history = {inst: synthetic(args.bars, starts.get(inst, 1.0), seed=i + 1)
                   for i, inst in enumerate(instruments)}

    if not args.verbose:
        logging.getLogger("fxagent").setLevel(logging.WARNING)
    res = run_backtest(cfg, history, balance=args.balance, spread_pips=args.spread, slippage_pips=args.slippage)
    bars = sum(len(v) for v in history.values())
    print(f"Backtest {build_strategy(cfg.strategy).fingerprint()} over {bars} bars, "
          f"{', '.join(history)} {cfg.granularity}")
    print(format_metrics(res.metrics))
    print(f"  final balance     {res.final_balance:,.2f}")
    g = evaluate(res.trades, args.balance, cfg.gate)
    print("\nWould this backtest pass the go-live gate? (practice results are what actually count)")
    print(g.report())
    return 0


def cmd_run(cfg, args):
    mode = args.mode or cfg.mode
    journal = Journal(cfg.journal_path)
    live = mode == "live"
    if live:
        problems = []
        if not args.confirm_live:
            problems.append("pass --confirm-live")
        if os.environ.get(LIVE_ENV_FLAG) != "yes":
            problems.append(f"set {LIVE_ENV_FLAG}=yes")
        fingerprint, g = practice_gate(cfg, journal)
        if not g.passed:
            problems.append(f"the practice record for {fingerprint} must pass the go-live gate:\n{g.report()}")
        if problems:
            print("Refusing to trade live:\n- " + "\n- ".join(problems), file=sys.stderr)
            return 1
        print("LIVE TRADING with real money. Touch", cfg.kill_switch_path, "to stop and flatten.")

    broker = _broker(mode)
    agent = Agent(broker=broker, strategy=build_strategy(cfg.strategy), risk=RiskManager(cfg.risk, live=live),
                  journal=journal, mode=mode, instruments=cfg.instruments, granularity=cfg.granularity,
                  candle_count=cfg.candle_count, kill_switch_path=cfg.kill_switch_path,
                  close_on_halt=cfg.close_on_halt)
    if journal.first_equity(mode) is None:
        a = broker.account()
        journal.record_equity(mode, datetime.now(timezone.utc), a.balance, a.nav)
    if args.once:
        agent.tick(datetime.now(timezone.utc))
        return 0
    try:
        agent.run_forever(cfg.poll_seconds)
    except KeyboardInterrupt:
        print("\nstopped (open trades keep their broker-side stop loss and take profit)")
    return 0


def cmd_report(cfg, args):
    journal = Journal(cfg.journal_path)
    mode = args.mode or "practice"
    trades = journal.closed_trades(mode)
    initial = journal.first_equity(mode) or 10_000.0
    print(f"{mode} journal: {cfg.journal_path}")
    by_strategy: dict[str, list] = {}
    for t in trades:
        by_strategy.setdefault(t["strategy"], []).append(t)
    for fp, ts in by_strategy.items():
        print(f"\n{fp}")
        print(format_metrics(compute(ts, initial)))
    opened = journal.open_trades(mode)
    print(f"\nopen trades: {len(opened)}")
    for r in opened:
        print(f"  {r['instrument']} {r['side']} {abs(r['units'])} @ {r['entry_price']} SL {r['stop_loss']} TP {r['take_profit']}")
    print("\nrecent events:")
    for e in reversed(journal.events(mode, args.events)):
        print(f"  {e['time'][:19]} {e['level']:7} {e['message']}")
    return 0


def cmd_gate(cfg, args):
    fingerprint, g = practice_gate(cfg, Journal(cfg.journal_path))
    print(f"strategy {fingerprint}\n{format_metrics(g.metrics)}\n\n{g.report()}")
    return 0 if g.passed else 1


def cmd_resume(cfg, args):
    journal = Journal(cfg.journal_path)
    mode = args.mode or cfg.mode
    journal.set_state(mode, "halted", None)
    journal.set_state(mode, "peak_equity", None)
    print(f"{mode}: halt cleared and drawdown peak reset")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fxagent", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="config.toml")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("check")
    s.add_argument("--mode", choices=["practice", "live"])
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("backtest")
    s.add_argument("--instrument", action="append")
    s.add_argument("--csv", action="append", help="CSV per --instrument, in the same order")
    s.add_argument("--fetch", type=int, metavar="N", help="download N candles per instrument from OANDA practice")
    s.add_argument("--bars", type=int, default=4000, help="bars of synthetic data when no data is given")
    s.add_argument("--balance", type=float, default=10_000.0)
    s.add_argument("--spread", type=float, default=1.0, help="simulated spread in pips")
    s.add_argument("--slippage", type=float, default=0.2, help="simulated slippage in pips")
    s.set_defaults(func=cmd_backtest)

    s = sub.add_parser("run")
    s.add_argument("--mode", choices=["practice", "live"])
    s.add_argument("--once", action="store_true", help="run a single tick and exit")
    s.add_argument("--confirm-live", action="store_true")
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("report")
    s.add_argument("--mode", choices=["practice", "live"])
    s.add_argument("--events", type=int, default=20)
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("gate")
    s.set_defaults(func=cmd_gate)

    s = sub.add_parser("resume")
    s.add_argument("--mode", choices=["practice", "live"])
    s.set_defaults(func=cmd_resume)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config(args.config)
    try:
        return args.func(cfg, args)
    except Exception as e:
        if args.verbose:
            raise
        print(f"error: {e}", file=sys.stderr)
        return 1
