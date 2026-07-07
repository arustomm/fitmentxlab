#!/usr/bin/env python3
"""Pull historical federal contract award data from USASpending.gov.

No API key required -- this is a fully public API. Use it to see what the
government actually paid in the past for work like yours, so you know
whether a live opportunity is priced realistically before you bid, and so
you know what price to quote.

Examples:
    # Past awards for the whole automotive_fitment track
    python3 usaspending_history.py --track automotive_fitment

    # Only small awards (the ones a new small business can realistically win)
    python3 usaspending_history.py --track courier_logistics --max-amount 250000

    # Raw NAICS/PSC codes instead of a predefined track
    python3 usaspending_history.py --naics 492110 --min-amount 1000 --max-amount 50000
"""
import argparse
import json
import sys
from datetime import date, timedelta

import requests

from codes import TRACKS, all_naics, all_psc

API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
AWARD_TYPE_CODES = ["A", "B", "C", "D"]  # definitive contract award types


def search_awards(naics=None, psc=None, keywords=None, min_amount=None,
                   max_amount=None, years_back=3, limit=25):
    filters = {
        "award_type_codes": AWARD_TYPE_CODES,
        "time_period": [{
            "start_date": (date.today() - timedelta(days=365 * years_back)).isoformat(),
            "end_date": date.today().isoformat(),
        }],
    }
    if naics:
        filters["naics_codes"] = {"require": naics}
    if psc:
        filters["psc_codes"] = {"require": [["Product", code] for code in psc]}
    if keywords:
        filters["keywords"] = [keywords]
    if min_amount is not None or max_amount is not None:
        filters["award_amounts"] = [{
            "lower_bound": min_amount if min_amount is not None else 0,
            "upper_bound": max_amount if max_amount is not None else 999_999_999_999,
        }]

    body = {
        "filters": filters,
        "fields": [
            "Award ID", "Recipient Name", "Awarding Agency",
            "Awarding Sub Agency", "Start Date", "End Date",
            "Award Amount", "Description",
        ],
        "sort": "Award Amount",
        "order": "desc",
        "limit": limit,
        "subawards": False,
    }
    resp = requests.post(API_URL, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json().get("results", [])


def summarize(results):
    if not results:
        return {"count": 0}
    amounts = sorted(r["Award Amount"] for r in results if r.get("Award Amount"))
    if not amounts:
        return {"count": len(results)}
    n = len(amounts)
    return {
        "count": n,
        "min": amounts[0],
        "max": amounts[-1],
        "median": amounts[n // 2],
        "avg": round(sum(amounts) / n, 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--track", choices=list(TRACKS), help="Predefined industry track from codes.py")
    parser.add_argument("--naics", nargs="*", help="Explicit NAICS codes (overrides/adds to --track)")
    parser.add_argument("--psc", nargs="*", help="Explicit PSC codes (overrides/adds to --track)")
    parser.add_argument("--keywords", help="Free-text keyword filter, e.g. 'lift kit'")
    parser.add_argument("--min-amount", type=float, default=None)
    parser.add_argument("--max-amount", type=float, default=None)
    parser.add_argument("--years-back", type=int, default=3)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--json", action="store_true", help="Print raw JSON instead of a table")
    args = parser.parse_args()

    naics = list(args.naics or [])
    psc = list(args.psc or [])
    if args.track:
        naics += all_naics(args.track)
        psc += all_psc(args.track)
    if not naics and not psc and not args.keywords:
        parser.error("Provide --track, --naics/--psc, or --keywords")

    results = search_awards(
        naics=naics or None, psc=psc or None, keywords=args.keywords,
        min_amount=args.min_amount, max_amount=args.max_amount,
        years_back=args.years_back, limit=args.limit,
    )

    if args.json:
        print(json.dumps(results, indent=2))
        return

    stats = summarize(results)
    print(f"\n{stats.get('count', 0)} awards found "
          f"(last {args.years_back}y, NAICS={naics or '-'}, PSC={psc or '-'})")
    if stats.get("count"):
        print(f"  price range: ${stats['min']:,.0f} - ${stats['max']:,.0f}  "
              f"median: ${stats['median']:,.0f}  avg: ${stats['avg']:,.0f}\n")

    for r in results:
        amt = r.get("Award Amount") or 0
        print(f"${amt:>14,.2f}  {r.get('Recipient Name', '')[:35]:35s}  "
              f"{r.get('Awarding Sub Agency') or r.get('Awarding Agency', ''):30s}  "
              f"{r.get('Award ID', '')}")
        desc = (r.get("Description") or "").strip()
        if desc:
            print(f"               {desc[:110]}")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"USASpending API error: {e}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
