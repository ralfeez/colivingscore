import os
import threading
import requests

_BASE = "https://api.census.gov/data/2023/acs/acs5"
_BASE_PRIOR = "https://api.census.gov/data/2019/acs/acs5"
_PUMS_BASE = "https://api.census.gov/data/2023/acs/acs5/pums"

_cache: dict[str, dict] = {}
_lock = threading.Lock()

_B09020_TOTAL = "B09020_001E"
_B09020_ALONE = "B09020_021E"

_S0101_VARS = [
    "S0101_C01_008E",  # 55–59
    "S0101_C01_009E",  # 60–64
    "S0101_C01_010E",  # 65–69
    "S0101_C01_011E",  # 70–74
    "S0101_C01_012E",  # 75–79
    "S0101_C01_013E",  # 80–84
    "S0101_C01_014E",  # 85+
]
_AGE_LABELS = ["55–59", "60–64", "65–69", "70–74", "75–79", "80–84", "85+"]
_AGE_TARGET = [False, False, True, True, True, True, True]


def _key_param() -> str:
    key = os.environ.get("CENSUS_API_KEY", "")
    return f"&key={key}" if key else ""


def _fetch_b09020(state_fips: str, county_fips: str, base_url: str) -> tuple[int, int]:
    vars_param = f"{_B09020_TOTAL},{_B09020_ALONE}"
    url = (
        f"{base_url}?get={vars_param}"
        f"&for=county:{county_fips}&in=state:{state_fips}"
        f"{_key_param()}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    rows = resp.json()
    data_row = rows[1]
    total = int(data_row[0]) if data_row[0] else 0
    alone = int(data_row[1]) if data_row[1] else 0
    return total, alone


def _fetch_s0101(state_fips: str, county_fips: str) -> list[int]:
    vars_param = ",".join(_S0101_VARS)
    url = (
        f"{_BASE}/subject?get={vars_param}"
        f"&for=county:{county_fips}&in=state:{state_fips}"
        f"{_key_param()}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    rows = resp.json()
    data_row = rows[1]
    return [int(data_row[i]) if data_row[i] else 0 for i in range(7)]


def _fetch_pums_citizenship(state_fips: str) -> tuple[float, float]:
    # UCGID predicate not available on PUMS; filter age server-side where supported.
    # We request only the three needed variables and filter to AGEP>=65 via query param.
    url = (
        f"{_PUMS_BASE}?get=CIT,PWGTP,AGEP"
        f"&for=state:{state_fips}"
        f"&AGEP=65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95"
        f"{_key_param()}"
    )
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        rows = resp.json()
    except Exception:
        # Fall back to unfiltered query if age-filtered query fails
        url_fallback = (
            f"{_PUMS_BASE}?get=CIT,PWGTP,AGEP"
            f"&for=state:{state_fips}"
            f"{_key_param()}"
        )
        try:
            resp = requests.get(url_fallback, timeout=45)
            resp.raise_for_status()
            rows = resp.json()
        except Exception:
            return 100.0, 0.0

    try:
        header = rows[0]
        cit_idx = header.index("CIT")
        wgt_idx = header.index("PWGTP")
        age_idx = header.index("AGEP")
    except (IndexError, ValueError):
        return 100.0, 0.0

    citizen_w = 0
    noncitizen_w = 0
    for row in rows[1:]:
        try:
            age = int(row[age_idx])
        except (ValueError, TypeError):
            continue
        if age < 65:
            continue
        try:
            weight = int(row[wgt_idx])
            cit = int(row[cit_idx])
        except (ValueError, TypeError):
            continue
        if cit in (1, 2, 3, 4):
            citizen_w += weight
        elif cit == 5:
            noncitizen_w += weight

    total = citizen_w + noncitizen_w
    if total == 0:
        return 100.0, 0.0
    return round(citizen_w / total * 100, 1), round(noncitizen_w / total * 100, 1)


def get_demographics(state_fips: str, county_fips: str) -> dict:
    """Return all demographic data for a county. Results cached in memory."""
    cache_key = f"{state_fips}:{county_fips}"
    with _lock:
        if cache_key in _cache:
            return _cache[cache_key]

    pop65_current, alone_current = _fetch_b09020(state_fips, county_fips, _BASE)
    pop65_prior, _ = _fetch_b09020(state_fips, county_fips, _BASE_PRIOR)
    age_counts = _fetch_s0101(state_fips, county_fips)
    citizen_pct, noncitizen_pct = _fetch_pums_citizenship(state_fips)

    growth_pct = (
        round((pop65_current - pop65_prior) / pop65_prior * 100, 1)
        if pop65_prior > 0 else 0.0
    )
    alone_pct = (
        round(alone_current / pop65_current * 100, 1)
        if pop65_current > 0 else 0.0
    )

    result = {
        "pop65": pop65_current,
        "living_alone": alone_current,
        "living_alone_pct": alone_pct,
        "growth_pct": growth_pct,
        "age_brackets": [
            {"label": _AGE_LABELS[i], "count": age_counts[i], "target": _AGE_TARGET[i]}
            for i in range(7)
        ],
        "citizenship": {
            "citizen_pct": citizen_pct,
            "noncitizen_pct": noncitizen_pct,
        },
    }

    with _lock:
        _cache[cache_key] = result

    return result
