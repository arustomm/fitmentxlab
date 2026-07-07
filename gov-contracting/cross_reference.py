#!/usr/bin/env python3
"""For each live SAM.gov opportunity in a track, show the historical USASpending.gov
price range for that NAICS code, so you know roughly what to quote before you bid.

Requires SAM_API_KEY (see sam_opportunities.py). USASpending needs no key.
"""
import argparse
import os
import sys

from codes import TRACKS, all_naics
from sam_opportunities import search_opportunities
from usaspending_history import search_awards, summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", required=True, choices=list(TRACKS))
    parser.add_argument("--set-aside", nargs="*")
    parser.add_argument("--posted-days", type=int, default=30)
    args = parser.parse_args()

    api_key = os.environ.get("SAM_API_KEY")
    if not api_key:
        sys.exit("Set SAM_API_KEY first -- see sam_opportunities.py --help")

    naics = all_naics(args.track)
    opps = search_opportunities(api_key, naics=naics, set_asides=args.set_aside,
                                 posted_days=args.posted_days)
    print(f"{len(opps)} open opportunities in '{args.track}'\n")

    for o in opps:
        code = o.get("naicsCode")
        hist = search_awards(naics=[code] if code else naics, years_back=3, limit=25)
        stats = summarize(hist)
        print(f"[{o.get('solicitationNumber', '?')}] {o.get('title', '')[:70]}")
        print(f"    due: {o.get('responseDeadLine', '?')}  set-aside: {o.get('typeOfSetAsideDescription') or 'none'}")
        if stats.get("count"):
            print(f"    historical price benchmark (NAICS {code}, n={stats['count']}): "
                  f"${stats['min']:,.0f} - ${stats['max']:,.0f}, median ${stats['median']:,.0f}")
        else:
            print(f"    historical price benchmark (NAICS {code}): no comparable awards found")
        link = o.get("uiLink")
        if link:
            print(f"    {link}")
        print()


if __name__ == "__main__":
    main()
