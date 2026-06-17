import threading
import requests
import os

# Maps 2-letter state abbreviation → 2-digit Census FIPS code
STATE_FIPS = {
    "AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09",
    "DE":"10","DC":"11","FL":"12","GA":"13","HI":"15","ID":"16","IL":"17",
    "IN":"18","IA":"19","KS":"20","KY":"21","LA":"22","ME":"23","MD":"24",
    "MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30","NE":"31",
    "NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38",
    "OH":"39","OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46",
    "TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53","WV":"54",
    "WI":"55","WY":"56",
}

# Reverse map: FIPS → abbreviation
FIPS_STATE = {v: k for k, v in STATE_FIPS.items()}

_VALID_STATE_FIPS = set(STATE_FIPS.values())

# Cache: state_fips → list of county dicts
_county_cache: dict[str, list[dict]] = {}
_cache_lock = threading.Lock()

_CENSUS_BASE = "https://api.census.gov/data/2023/acs/acs5"
_CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")


def is_valid_state_fips(state_fips: str) -> bool:
    return state_fips in _VALID_STATE_FIPS


def get_counties(state_fips: str) -> list[dict]:
    """
    Return list of {"name": "Dallas County", "fips": "113"} for a state.
    Results cached in memory for the process lifetime.
    Requires CENSUS_API_KEY environment variable.
    Returns empty list if API key is missing or API call fails.
    """
    if not is_valid_state_fips(state_fips):
        return []
    with _cache_lock:
        if state_fips not in _county_cache:
            if not _CENSUS_API_KEY:
                _county_cache[state_fips] = []
                return []
            try:
                url = f"{_CENSUS_BASE}?get=NAME&for=county:*&in=state:{state_fips}&key={_CENSUS_API_KEY}"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                rows = resp.json()
                counties = [
                    {"name": row[0].split(",")[0].strip(), "fips": row[2]}
                    for row in rows[1:]
                ]
                counties.sort(key=lambda c: c["name"])
                _county_cache[state_fips] = counties
            except Exception:
                _county_cache[state_fips] = []
        return _county_cache[state_fips]


def is_valid_county_fips(state_fips: str, county_fips: str) -> bool:
    """Return True if the county_fips is a real county in the given state."""
    counties = get_counties(state_fips)
    return any(c["fips"] == county_fips for c in counties)
