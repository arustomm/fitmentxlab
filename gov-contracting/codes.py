"""Reference NAICS/PSC codes and set-aside types, organized by "track" (industry).

Each track is a self-contained target market you can register under in SAM.gov
and search against with sam_opportunities.py / usaspending_history.py. Start
with the tracks below, add more by copying the pattern -- any NAICS/PSC code
works with both tools, this file just keeps the ones worth watching in one place.

Tracks included:
  - automotive_fitment : FitmentXLab's existing specialty (wheels, tires,
    suspension/lift kits, off-road truck accessories)
  - courier_logistics   : medical/general courier, messenger, last-mile
    delivery -- notoriously low barrier to entry (no inventory, no
    manufacturing, just a vehicle + insurance + a driver)
  - general_easy_entry  : other categories the SBA/GSA data consistently
    show as easiest for a brand-new small business to win first awards in
"""

TRACKS = {
    "automotive_fitment": {
        "label": "Wheels / Tires / Suspension / Off-Road Truck Accessories",
        "naics": {
            "423120": "Motor Vehicle Supplies and New Parts Merchant Wholesalers (PRIMARY)",
            "441320": "Tire Dealers",
            "336390": "Other Motor Vehicle Parts Manufacturing",
            "811198": "All Other Automotive Repair and Maintenance (install services)",
        },
        "psc": {
            "2610": "Tires and Tubes, Pneumatic, except Aircraft",
            "2640": "Tires and Tubes, Solid and Cushion, and Repair Materials",
            "2530": "Vehicular Brake, Steering, Axle, Wheel and Track Components",
            "2520": "Vehicular Cab, Body, and Frame Structural Components",
            "2590": "Miscellaneous Vehicular Components",
        },
    },
    "courier_logistics": {
        "label": "Medical / General Courier, Messenger, Last-Mile Delivery",
        "naics": {
            "492110": "Couriers and Express Delivery Services (PRIMARY)",
            "492210": "Local Messengers and Local Delivery",
            "484122": "General Freight Trucking, Long-Distance, Less Than Truckload",
            "621999": "All Other Miscellaneous Ambulatory Health Care Services (specimen/lab courier runs)",
            "492000": "Couriers and Messengers (parent category, some solicitations use this)",
        },
        "psc": {
            "V231": "Transportation/Travel/Relocation - Local Trucking (household goods excluded)",
            "V125": "Transportation/Travel/Relocation - Contract Mail Service (courier/messenger)",
            "S209": "Housekeeping - Specimen/Medical Records Courier (agency-dependent, verify)",
        },
    },
    "general_easy_entry": {
        "label": "Other consistently low-barrier categories worth scanning opportunistically",
        "naics": {
            "561720": "Janitorial Services",
            "561730": "Landscaping Services",
            "484210": "Used Household and Office Goods Moving (local hauling/junk removal)",
            "561990": "All Other Support Services (general small-purchase catch-all)",
            "423450": "Medical, Dental, and Hospital Equipment and Supplies Wholesalers",
        },
        "psc": {
            "S201": "Housekeeping - Custodial Janitorial",
            "S208": "Housekeeping - Landscaping/Groundskeeping",
            "V119": "Transportation - Other",
        },
    },
}

# Small-business set-aside codes (SAM.gov typeOfSetAside values) worth
# filtering for -- these exclude large primes, which is most of why these
# lanes are winnable for a new entrant.
SET_ASIDES = {
    "SBA": "Total Small Business Set-Aside",
    "SBP": "Partial Small Business Set-Aside",
    "WOSB": "Women-Owned Small Business",
    "EDWOSB": "Economically Disadvantaged WOSB",
    "SDVOSBC": "Service-Disabled Veteran-Owned Small Business (Set-Aside)",
    "SDVOSBS": "Service-Disabled Veteran-Owned Small Business (Sole Source)",
    "8A": "8(a) Set-Aside",
    "HZC": "HUBZone Set-Aside",
}

SIMPLIFIED_ACQUISITION_THRESHOLD = 250_000
MICRO_PURCHASE_THRESHOLD = 10_000


def all_naics(track: str) -> list[str]:
    return list(TRACKS[track]["naics"].keys())


def all_psc(track: str) -> list[str]:
    return list(TRACKS[track]["psc"].keys())
