# Source: SeniorTruth.com, 2026 — state average monthly costs, updated annually.

IL_COSTS = {
    "AL": {"range": "avg. $2,650/mo", "state": "Alabama"},
    "AK": {"range": "avg. $4,800/mo", "state": "Alaska"},
    "AZ": {"range": "avg. $3,200/mo", "state": "Arizona"},
    "AR": {"range": "avg. $2,600/mo", "state": "Arkansas"},
    "CA": {"range": "avg. $4,200/mo", "state": "California"},
    "CO": {"range": "avg. $3,700/mo", "state": "Colorado"},
    "CT": {"range": "avg. $4,500/mo", "state": "Connecticut"},
    "DE": {"range": "avg. $3,800/mo", "state": "Delaware"},
    "DC": {"range": "avg. $5,000/mo", "state": "District of Columbia"},
    "FL": {"range": "avg. $3,200/mo", "state": "Florida"},
    "GA": {"range": "avg. $2,900/mo", "state": "Georgia"},
    "HI": {"range": "avg. $4,600/mo", "state": "Hawaii"},
    "ID": {"range": "avg. $3,100/mo", "state": "Idaho"},
    "IL": {"range": "avg. $3,400/mo", "state": "Illinois"},
    "IN": {"range": "avg. $2,900/mo", "state": "Indiana"},
    "IA": {"range": "avg. $2,800/mo", "state": "Iowa"},
    "KS": {"range": "avg. $2,800/mo", "state": "Kansas"},
    "KY": {"range": "avg. $2,650/mo", "state": "Kentucky"},
    "LA": {"range": "avg. $2,500/mo", "state": "Louisiana"},
    "ME": {"range": "avg. $4,000/mo", "state": "Maine"},
    "MD": {"range": "avg. $3,500/mo", "state": "Maryland"},
    "MA": {"range": "avg. $4,400/mo", "state": "Massachusetts"},
    "MI": {"range": "avg. $3,000/mo", "state": "Michigan"},
    "MN": {"range": "avg. $3,600/mo", "state": "Minnesota"},
    "MS": {"range": "avg. $2,300/mo", "state": "Mississippi"},
    "MO": {"range": "avg. $2,500/mo", "state": "Missouri"},
    "MT": {"range": "avg. $3,300/mo", "state": "Montana"},
    "NE": {"range": "avg. $3,000/mo", "state": "Nebraska"},
    "NV": {"range": "avg. $3,100/mo", "state": "Nevada"},
    "NH": {"range": "avg. $4,200/mo", "state": "New Hampshire"},
    "NJ": {"range": "avg. $4,300/mo", "state": "New Jersey"},
    "NM": {"range": "avg. $3,000/mo", "state": "New Mexico"},
    "NY": {"range": "avg. $4,500/mo", "state": "New York"},
    "NC": {"range": "avg. $3,100/mo", "state": "North Carolina"},
    "ND": {"range": "avg. $3,000/mo", "state": "North Dakota"},
    "OH": {"range": "avg. $3,000/mo", "state": "Ohio"},
    "OK": {"range": "avg. $2,500/mo", "state": "Oklahoma"},
    "OR": {"range": "avg. $3,800/mo", "state": "Oregon"},
    "PA": {"range": "avg. $3,600/mo", "state": "Pennsylvania"},
    "RI": {"range": "avg. $4,100/mo", "state": "Rhode Island"},
    "SC": {"range": "avg. $2,800/mo", "state": "South Carolina"},
    "SD": {"range": "avg. $2,800/mo", "state": "South Dakota"},
    "TN": {"range": "avg. $2,800/mo", "state": "Tennessee"},
    "TX": {"range": "avg. $3,000/mo", "state": "Texas"},
    "UT": {"range": "avg. $3,100/mo", "state": "Utah"},
    "VT": {"range": "avg. $4,100/mo", "state": "Vermont"},
    "VA": {"range": "avg. $3,400/mo", "state": "Virginia"},
    "WA": {"range": "avg. $4,100/mo", "state": "Washington"},
    "WV": {"range": "avg. $2,500/mo", "state": "West Virginia"},
    "WI": {"range": "avg. $3,300/mo", "state": "Wisconsin"},
    "WY": {"range": "avg. $3,200/mo", "state": "Wyoming"},
}

_SOURCE = "SeniorTruth.com, 2026"


def get_il_cost(state_abbr: str) -> dict | None:
    entry = IL_COSTS.get(state_abbr.upper())
    if entry is None:
        return None
    return {**entry, "source": _SOURCE}
