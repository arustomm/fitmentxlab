#!/usr/bin/env python3
"""Search live federal contract opportunities on SAM.gov.

Requires a free SAM.gov API key (NOT the same as DEMO_KEY/data.gov keys):
  1. Create/log into your account at https://sam.gov
  2. Go to your profile -> "Account Details" -> "API Key"
  3. export SAM_API_KEY=your-key-here

Docs: https://open.gsa.gov/api/get-opportunities-public-api/

Examples:
    python3 sam_opportunities.py --track automotive_fitment --set-aside SBA
    python3 sam_opportunities.py --track courier_logistics --posted-days 30
    python3 sam_opportunities.py --naics 492110 --set-aside SBA WOSB SDVOSBC
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta

import requests

from codes import TRACKS, all_naics, SET_ASIDES

API_URL = "https://api.sam.gov/opportunities/v2/search"


def search_opportunities(api_key, naics=None, keywords=None, set_asides=None,
                          posted_days=30, limit=100, active_only=True):
    all_results = []
    naics_list = naics or [None]
    for code in naics_list:
        params = {
            "api_key": api_key,
            "limit": min(limit, 1000),
            "postedFrom": (date.today() - timedelta(days=posted_days)).strftime("%m/%d/%Y"),
            "postedTo": date.today().strftime("%m/%d/%Y"),
        }
        if code:
            params["ncode"] = code
        if keywords:
            params["title"] = keywords
        if active_only:
            params["status"] = "active"

        resp = requests.get(API_URL, params=params, timeout=30)
        if resp.status_code == 404:
            raise RuntimeError(
                "SAM.gov returned 404 -- this almost always means the api_key is "
                "missing/invalid (SAM.gov's gateway masks auth failures as 404). "
                "Get a real key from your SAM.gov account (Account Details > API Key), "
                "not a data.gov DEMO_KEY."
            )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("opportunitiesData", [])
        if set_asides:
            results = [
                r for r in results
                if (r.get("typeOfSetAsideDescription") or "") and
                any(sa in (r.get("typeOfSetAside") or "") for sa in set_asides)
            ]
        all_results.extend(results)
    return all_results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--track", choices=list(TRACKS), help="Predefined industry track from codes.py")
    parser.add_argument("--naics", nargs="*", help="Explicit NAICS codes")
    parser.add_argument("--keywords", help="Free-text title keyword filter")
    parser.add_argument("--set-aside", nargs="*", choices=list(SET_ASIDES),
                         help="Only show these set-aside types (e.g. SBA WOSB SDVOSBC)")
    parser.add_argument("--posted-days", type=int, default=30, help="Look back this many days (max 365)")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("SAM_API_KEY")
    if not api_key:
        parser.error("Set SAM_API_KEY env var first. See --help for how to get one.")

    naics = list(args.naics or [])
    if args.track:
        naics += all_naics(args.track)

    results = search_opportunities(
        api_key, naics=naics or None, keywords=args.keywords,
        set_asides=args.set_aside, posted_days=args.posted_days, limit=args.limit,
    )

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"\n{len(results)} open opportunities "
          f"(last {args.posted_days}d, NAICS={naics or '-'}, set-aside={args.set_aside or 'any'})\n")
    for r in results:
        deadline = r.get("responseDeadLine", "?")
        setaside = r.get("typeOfSetAsideDescription") or "no set-aside"
        print(f"[{r.get('solicitationNumber', '?')}] {r.get('title', '')[:80]}")
        print(f"    agency: {r.get('fullParentPathName', '?')}")
        print(f"    naics: {r.get('naicsCode', '?')}  set-aside: {setaside}  due: {deadline}")
        link = r.get("uiLink")
        if link:
            print(f"    {link}")
        print()


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"SAM.gov API error: {e}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
