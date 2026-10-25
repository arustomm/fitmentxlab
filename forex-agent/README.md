# fxagent: forex watch agent

An agent that watches the forex market, trades a **sandbox (OANDA practice account, fake money)**
first, and refuses to trade live until the sandbox record proves the strategy is profitable.

Pure Python 3.11+ standard library. Nothing to `pip install`.

```
backtest (history, paper broker) ──► practice (OANDA demo, real prices) ──► go-live gate ──► live (real money, reduced size)
          same Agent code                      same Agent code                                     same Agent code
```

## How it works

Every `poll_seconds` the agent wakes up and:

1. Checks the **kill switch** (`data/STOP` file). If present: closes its trades and exits.
2. Reconciles with the broker: trades closed broker-side by stop loss / take profit get journaled.
3. Checks **circuit breakers**: daily loss limit (stops trading until the next UTC day) and
   max drawdown from peak (stops until you run `fxagent resume`). Both flatten positions.
4. For each instrument, when a **new candle has completed**, asks the strategy for a signal.
5. Entries go through the **risk manager**: market must be open, spread under the limit,
   max open trades, size so a stop-out loses `risk_per_trade_pct` of equity, leverage cap.
   **Every order carries a broker-side stop loss** (the OANDA client refuses orders without one),
   so positions stay protected even if the agent crashes or loses its connection.
6. Everything goes in an SQLite journal (`data/journal.sqlite`): trades, equity, every decision.

Positions you open by hand are left alone, and the agent won't trade an instrument you hold.

The default strategy (`ema_trend`) is a plain trend follower: EMA 20/50 crossover in the
direction of EMA 200, stop at 2×ATR, target at 3×ATR. It's a baseline to prove out the
pipeline, not a known edge. Add your own in `fxagent/strategy.py`.

## Setup

1. Create a free **OANDA practice (demo) account** at oanda.com.
2. In the account portal: *Manage API Access* → generate a token. Note the account id
   (looks like `101-001-1234567-001`).
3. Configure:
   ```bash
   cd forex-agent
   cp config.example.toml config.toml
   cp .env.example .env        # fill in OANDA_PRACTICE_TOKEN and OANDA_PRACTICE_ACCOUNT_ID
   python3 -m fxagent check    # prints balance and live spreads
   ```

## Workflow

**1. Backtest.** Download real history and replay it through the agent:
```bash
python3 -m fxagent backtest --fetch 5000           # 5000 H1 candles per pair, saved to data/history/
python3 -m fxagent backtest --instrument EUR_USD --csv data/history/EUR_USD_H1.csv
python3 -m fxagent backtest                        # synthetic data: plumbing check only
```
Fills are pessimistic: spread + slippage on every trade, and when a bar touches both
stop and target the stop is assumed to fill. A good backtest is necessary, not sufficient.
Watch out for curve fitting: every parameter you tune on history makes backtests look better
than reality.

**2. Run on the sandbox.** Leave it running on a machine that stays on (a small VPS, a Raspberry Pi):
```bash
python3 -m fxagent run                 # practice mode, Ctrl-C to stop
python3 -m fxagent report              # P&L, open trades, recent decisions
touch data/STOP                        # kill switch: flatten and exit
```

**3. Check the go-live gate.**
```bash
python3 -m fxagent gate
```
Practice trades only count toward the gate if they were made with the **exact strategy and
parameters** you'd run live (a fingerprint is stored with every trade). Change a parameter and
the record starts over. Defaults in `[gate]`:

| check | default |
|---|---|
| closed trades | ≥ 50 |
| time in sandbox | ≥ 30 days |
| net P&L | > 0 |
| profit factor | ≥ 1.3 |
| max drawdown | ≤ 10% |
| t-statistic of mean R per trade | ≥ 2.0 (the edge is unlikely to be luck) |

**4. Go live**, only after the gate passes:
1. Open a live OANDA account, fund it with money you can afford to lose, create a live token.
2. Put `OANDA_LIVE_TOKEN` and `OANDA_LIVE_ACCOUNT_ID` in `.env`.
3. Run:
   ```bash
   FXAGENT_ALLOW_LIVE=yes python3 -m fxagent run --mode live --confirm-live
   ```
The agent refuses unless all three hold: the `--confirm-live` flag, the env variable, and a
passing gate. Live risk per trade is multiplied by `live_risk_multiplier` (default 0.5).
Practice and live use separate credentials, so a practice token can never place a live order.
Keep the practice agent running in parallel: if live results drift from practice, stop.

## Layout

```
fxagent/
  agent.py         watch loop: safety checks, reconciliation, signal → order
  strategy.py      strategies (ema_trend) + fingerprinting
  risk.py          position sizing, entry filters, circuit breakers
  gate.py          go-live criteria
  journal.py       SQLite journal
  performance.py   metrics (profit factor, R expectancy, t-stat, drawdown)
  backtest.py      history replay through the real Agent
  brokers/oanda.py OANDA v20 REST (practice + live)
  brokers/paper.py local simulator for backtests
tests/             python3 -m unittest discover -s tests -t .
```

## Caveats

- Most retail forex traders lose money, and most strategies that backtest well don't survive
  live trading. The gate lowers the odds of going live with a fluke; it can't remove them.
- Practice fills are kinder than live ones (no requotes, ideal liquidity), and slippage is worse
  around news releases and on weekend gaps.
- Leverage and product availability depend on your jurisdiction (e.g. US accounts: FIFO, no hedging,
  max 50:1 on majors). The agent never hedges, so it's compatible with FIFO rules.
- This is software, not financial advice. Read the code before giving it real money.
