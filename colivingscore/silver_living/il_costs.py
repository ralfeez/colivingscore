# Source: SeniorLiving.org, 2026 — state medians, updated annually.
# IMPORTANT: Verify these ranges against SeniorLiving.org before deploying.

IL_COSTS = {
    "AL": {"range": "$2,200–$3,400/mo", "state": "Alabama"},
    "AK": {"range": "$3,800–$5,500/mo", "state": "Alaska"},
    "AZ": {"range": "$2,500–$4,000/mo", "state": "Arizona"},
    "AR": {"range": "$2,000–$3,200/mo", "state": "Arkansas"},
    "CA": {"range": "$3,200–$4,800/mo", "state": "California"},
    "CO": {"range": "$2,800–$4,400/mo", "state": "Colorado"},
    "CT": {"range": "$3,500–$5,200/mo", "state": "Connecticut"},
    "DE": {"range": "$3,200–$4,800/mo", "state": "Delaware"},
    "DC": {"range": "$4,000–$6,000/mo", "state": "District of Columbia"},
    "FL": {"range": "$2,500–$4,200/mo", "state": "Florida"},
    "GA": {"range": "$2,200–$3,800/mo", "state": "Georgia"},
    "HI": {"range": "$4,000–$6,500/mo", "state": "Hawaii"},
    "ID": {"range": "$2,400–$3,800/mo", "state": "Idaho"},
    "IL": {"range": "$2,800–$4,500/mo", "state": "Illinois"},
    "IN": {"range": "$2,200–$3,600/mo", "state": "Indiana"},
    "IA": {"range": "$2,100–$3,400/mo", "state": "Iowa"},
    "KS": {"range": "$2,200–$3,500/mo", "state": "Kansas"},
    "KY": {"range": "$2,200–$3,500/mo", "state": "Kentucky"},
    "LA": {"range": "$2,200–$3,600/mo", "state": "Louisiana"},
    "ME": {"range": "$3,000–$4,600/mo", "state": "Maine"},
    "MD": {"range": "$3,400–$5,000/mo", "state": "Maryland"},
    "MA": {"range": "$3,800–$5,600/mo", "state": "Massachusetts"},
    "MI": {"range": "$2,400–$3,800/mo", "state": "Michigan"},
    "MN": {"range": "$2,800–$4,400/mo", "state": "Minnesota"},
    "MS": {"range": "$2,000–$3,200/mo", "state": "Mississippi"},
    "MO": {"range": "$2,200–$3,600/mo", "state": "Missouri"},
    "MT": {"range": "$2,600–$4,000/mo", "state": "Montana"},
    "NE": {"range": "$2,200–$3,600/mo", "state": "Nebraska"},
    "NV": {"range": "$2,600–$4,200/mo", "state": "Nevada"},
    "NH": {"range": "$3,400–$5,000/mo", "state": "New Hampshire"},
    "NJ": {"range": "$3,500–$5,400/mo", "state": "New Jersey"},
    "NM": {"range": "$2,400–$3,800/mo", "state": "New Mexico"},
    "NY": {"range": "$3,500–$5,500/mo", "state": "New York"},
    "NC": {"range": "$2,400–$3,800/mo", "state": "North Carolina"},
    "ND": {"range": "$2,200–$3,500/mo", "state": "North Dakota"},
    "OH": {"range": "$2,400–$3,800/mo", "state": "Ohio"},
    "OK": {"range": "$2,200–$3,500/mo", "state": "Oklahoma"},
    "OR": {"range": "$2,800–$4,400/mo", "state": "Oregon"},
    "PA": {"range": "$2,800–$4,400/mo", "state": "Pennsylvania"},
    "RI": {"range": "$3,200–$5,000/mo", "state": "Rhode Island"},
    "SC": {"range": "$2,400–$3,800/mo", "state": "South Carolina"},
    "SD": {"range": "$2,200–$3,500/mo", "state": "South Dakota"},
    "TN": {"range": "$2,200–$3,800/mo", "state": "Tennessee"},
    "TX": {"range": "$2,400–$3,800/mo", "state": "Texas"},
    "UT": {"range": "$2,600–$4,000/mo", "state": "Utah"},
    "VT": {"range": "$3,200–$5,000/mo", "state": "Vermont"},
    "VA": {"range": "$3,000–$4,800/mo", "state": "Virginia"},
    "WA": {"range": "$3,000–$4,800/mo", "state": "Washington"},
    "WV": {"range": "$2,200–$3,400/mo", "state": "West Virginia"},
    "WI": {"range": "$2,600–$4,000/mo", "state": "Wisconsin"},
    "WY": {"range": "$2,400–$3,800/mo", "state": "Wyoming"},
}

_SOURCE = "SeniorLiving.org, 2026"


def get_il_cost(state_abbr: str) -> dict | None:
    """Return IL cost info for a state abbreviation, or None if unknown."""
    entry = IL_COSTS.get(state_abbr.upper())
    if entry is None:
        return None
    return {**entry, "source": _SOURCE}
