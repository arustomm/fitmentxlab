# Government Contracting Strategy — FitmentXLab

Scope: federal + state/local, open to any industry that's winnable (not just
wheels/tires/suspension). Two concrete tracks are set up below — automotive
parts (your existing specialty) and medical/general courier (high win-rate
for a new small business) — plus a toolkit to scan for more.

All dollar figures below are real, pulled live from USASpending.gov on
2026-07-07 (see `gov-contracting/` for the scripts that produced them).

---

## 1. Entity setup (do this first, ~2-4 weeks, mostly waiting on the govt)

1. **Get a D-U-N-S/UEI.** SAM.gov now issues a **Unique Entity ID (UEI)**
   directly — no separate D-U-N-S step anymore.
2. **Register at SAM.gov** (sam.gov) — free. You'll need: legal business
   name/EIN, NAICS codes (pick from the tracks below), banking info for
   EFT payment, and a notarized letter if you're a first-time registrant
   (SAM sometimes requires this for identity verification — budget 1-2
   weeks for that step alone).
3. **Complete Reps & Certifications** in SAM — this is where you self-certify
   as small business, and (if applicable) as WOSB/EDWOSB, SDVOSB, veteran-owned,
   HUBZone, or 8(a)-eligible. These set-asides are the single biggest lever
   for a new entrant: they legally exclude large primes from competing.
4. **Get a CAGE code** (issued automatically with SAM registration).
5. **State/local registration** — separate from SAM.gov. Each state runs its
   own vendor portal (e.g., a state's central procurement office + often a
   third-party bid board like BidNet Direct, Ionwave/Periscope, or
   PlanetBids). Tell me your state and I'll pull the specific portal + any
   state small-business/M/WBE certification program (usually free, run by
   the state's Office of Minority/Women Business or similar).
6. **Register for cooperative purchasing contracts** — Sourcewell,
   OMNIA Partners, and NASPO ValuePoint let one master contract sell to
   thousands of state/local/school agencies without re-bidding each one.
   These run open solicitation cycles a few times a year — worth watching
   for automotive parts, fleet maintenance, and courier/delivery categories.

## 2. Certifications worth pursuing (do in parallel with step 1)

- **Small Business** (self-certified, free, immediate via SAM reps & certs).
- **WOSB / EDWOSB, SDVOSB/VOSB, HUBZone, 8(a)** — only pursue the ones you
  actually qualify for; each unlocks its own competition pool with far less
  competition than full-and-open. If any apply to you personally, say so and
  I'll fold the exact application steps in.
- **State M/WBE certifications** — separate from federal, usually recognized
  by that state's agencies and sometimes reciprocal with nearby states.

## 3. Two concrete tracks to start bidding, plus a general scanner

### Track A — Automotive: wheels, tires, suspension/lift kits, truck accessories

Your existing specialty. Real historical awards (last 3 years) at the small
end of the market — i.e., sizes a new vendor can realistically win:

| Winner | Agency | Item | Amount |
|---|---|---|---|
| LOC Performance Products LLC | DLA | Hub and arm assembly | $99,245 |
| General Dynamics Land Systems | DLA | Hose and tube assembly | $99,023 |
| Facet (Oklahoma) LLC | DLA | Filter canister | $98,319 |
| Equipment Parts Sales | DLA | Sensor linear detector | $97,790 |
| SupplyCore LLC | DLA | Idler assembly, track | $97,346 |

The buyer that matters most here is the **Defense Logistics Agency (DLA)**,
which runs almost all of this through **DIBBS** (dibbs2.bsm.dla.mil) — a
separate RFQ portal from SAM.gov, specifically for parts. Register there once
you have your CAGE code. Bigger-picture channel: **GSA Multiple Award
Schedule (MAS), Vehicular & Fleet category** — getting on this schedule
(3-6 month process) lets agencies buy from you directly off GSA Advantage
without a fresh competition each time.

### Track B — Medical/general courier (recommended as your easiest near-term win)

This is a service, not a product: no inventory, no manufacturing, just a
reliable driver + vehicle + insurance. The data shows individuals and
tiny LLCs winning these directly:

| Winner | Agency | Contract | Amount |
|---|---|---|---|
| William Lyons (individual) | Dept. of the Air Force | Medical courier service | $190,700 |
| FCX, LLC | Dept. of Veterans Affairs | Blood/stat medical courier | $184,571 |
| All American Express Solutions LLC | VA | Outpatient clinic medical courier | $209,200 |
| AMS Express LLC | Air Force | Medical courier service | $211,575 |
| Crosstown Courier Service Inc | VA | Medical courier services | $246,157 |

Pattern: **individual VA medical centers and Air Force bases** buy this
locally, in the **$180K-$300K/year** range, frequently as sole-source or
small-business set-aside renewals to the incumbent. That means: (a) low
competition once you're in, (b) a realistic entry price point, (c) you can
literally call/email the contracting office serving your nearest VA medical
center or Air Force base and ask about their courier contract's next
recompete date. NAICS 492110 (Couriers and Express Delivery) is the
primary code.

### Track C — General easy-entry scan

Janitorial (561720), landscaping (561730), local hauling/moving (484210),
and similar service categories consistently show up as the fastest
first-contract wins for brand-new small businesses government-wide, because
of low capital requirements and heavy small-business set-aside usage. Not
built out with sample data here, but wired into the toolkit (`codes.py` ->
`general_easy_entry`) so you can scan it the same way.

## 4. Where "easy to win" contracts actually live

Ranked by how little competition you'll face as a new vendor:

1. **Micro-purchases (<$10,000)** — no competition required at all; a
   contracting officer can just call/email you. Build relationships with COs
   at your nearest agency site.
2. **Simplified Acquisition Threshold buys ($10K-$250K)** — streamlined
   competition, often small-business set-aside by default. This is where
   almost every example above falls.
3. **Sole-source set-asides** (SDVOSB, 8(a), HUBZone) — if you or a partner
   qualifies, agencies can award to you *without* competition up to much
   higher thresholds.
4. **State/local cooperative contracts** (Sourcewell, OMNIA, NASPO) — one
   bid, many buyers.
5. **GSA Schedule / MAS** — more setup effort, but once on it, agencies can
   buy from you directly.
6. **Full-and-open, unrestricted competitions** — hardest, most competition;
   deprioritize until you have past-performance history.

## 5. The toolkit (`gov-contracting/`)

Built and tested this session, using live data:

- `usaspending_history.py` — **works right now, no API key** — pulls
  historical award pricing so you can benchmark any bid before you quote.
- `sam_opportunities.py` — searches *live* open solicitations. Needs your
  own free SAM.gov API key (Account Details -> API Key on sam.gov — a
  `DEMO_KEY` will not work, SAM's gateway returns a bare 404 for invalid
  keys instead of a clear auth error).
- `cross_reference.py` — combines both: shows live opportunities next to
  the historical price range for that NAICS code.
- `codes.py` — the NAICS/PSC reference list per track; add new industries
  here as you decide to pursue them.

```bash
cd gov-contracting
pip install -r requirements.txt
python3 usaspending_history.py --track automotive_fitment --max-amount 100000
python3 usaspending_history.py --naics 492110 492210 --keywords "medical courier" --max-amount 300000
export SAM_API_KEY=...   # once you have one
python3 sam_opportunities.py --track courier_logistics --set-aside SBA WOSB SDVOSBC
python3 cross_reference.py --track automotive_fitment
```

## 6. What actually wins a bid, once you find one

1. **One-page capability statement** — company overview, NAICS/PSC codes,
   past performance (or comparable commercial experience if no gov history
   yet), CAGE/UEI, and set-aside status. Contracting officers ask for this
   before you're even on their radar for micro-purchases.
2. **Respond to the exact evaluation criteria** in the solicitation, not just
   price. For simplified acquisitions this is usually just price + technical
   capability + past performance narrative.
3. **Register in DIBBS** if pursuing Track A (parts) — most DLA tire/wheel/
   suspension-component RFQs never touch SAM.gov's opportunity search at all.
4. **Watch for recompetes**, not just fresh postings — Track B's VA/Air Force
   courier contracts are typically annual renewals; the month before a
   contract's period of performance ends is when a new RFQ drops.

## 7. Suggested 30/60/90

- **Days 1-15:** SAM.gov registration + reps & certs, decide on any
  qualifying certifications (WOSB/SDVOSB/etc.), draft capability statement.
- **Days 15-30:** DIBBS registration (Track A) if pursuing parts; identify
  3-5 nearest VA medical centers / Air Force bases and find their current
  courier contract + incumbent + expiration (Track B). Run
  `cross_reference.py` weekly once SAM_API_KEY is set up.
- **Days 30-90:** Bid on the first 3-5 realistic opportunities (prioritize
  set-asides you qualify for and dollar amounts under $250K), start a
  Sourcewell/OMNIA/NASPO cooperative-contract application if a relevant
  solicitation cycle is open, register on your state's vendor portal.

## Open questions for you

- Which state are you based in (for state/local portal + M/WBE cert specifics)?
- Do you personally qualify for veteran, HUBZone, or WOSB/EDWOSB status? This
  changes which sole-source lanes are available.
- Do you have a vehicle/driver capacity to actually run courier routes, or
  would that track need subcontracted drivers?
