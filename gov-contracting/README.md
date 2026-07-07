# Gov Contracting Toolkit

Small set of scripts to find winnable federal/state contract opportunities and
check what the government has historically paid for similar work, across
whatever industries you want to pursue (not locked to auto parts).

## Setup

```bash
pip install -r requirements.txt
export SAM_API_KEY=your-key   # only needed for live opportunity search
```

Get a SAM.gov API key (free): log into sam.gov -> your profile -> "Account
Details" -> "API Key". This is **not** the same as a data.gov `DEMO_KEY` --
using a fake/demo key gets you a `404` from SAM.gov's gateway, not a clear
auth error.

## Scripts

- `codes.py` -- reference NAICS/PSC codes grouped into "tracks" (industries).
  Ships with `automotive_fitment`, `courier_logistics`, and
  `general_easy_entry`. Add more tracks the same way, or just pass raw
  `--naics`/`--psc` codes to either tool below.

- `usaspending_history.py` -- **no API key needed.** Pulls real historical
  award data (who won, what agency, what it paid) from USASpending.gov for a
  track or explicit codes. Use this to price a bid and to see which agencies
  actually buy this work.

  ```bash
  python3 usaspending_history.py --track automotive_fitment --max-amount 100000
  python3 usaspending_history.py --naics 492110 492210 --keywords "medical courier" --max-amount 300000
  ```

- `sam_opportunities.py` -- **needs SAM_API_KEY.** Searches currently open
  solicitations on SAM.gov by NAICS/track/set-aside.

  ```bash
  python3 sam_opportunities.py --track courier_logistics --set-aside SBA WOSB SDVOSBC
  ```

- `cross_reference.py` -- combines both: for every open opportunity in a
  track, prints the historical price range for that NAICS so you have a
  target number before you quote.

  ```bash
  python3 cross_reference.py --track automotive_fitment --set-aside SBA
  ```

See `../GOV_CONTRACTING_STRATEGY.md` for the full step-by-step plan these
scripts support.
