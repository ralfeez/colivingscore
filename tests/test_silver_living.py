import pytest
import os
from colivingscore.silver_living.il_costs import get_il_cost


def test_known_state_returns_range():
    result = get_il_cost("TX")
    assert result is not None
    assert "range" in result
    assert "source" in result
    assert result["source"] == "SeniorLiving.org, 2026"
    assert result["state"] == "Texas"
    assert result["range"] == "$2,400–$3,800/mo"


def test_unknown_state_returns_none():
    assert get_il_cost("XX") is None


def test_all_50_states_plus_dc_present():
    from colivingscore.silver_living.il_costs import IL_COSTS
    assert len(IL_COSTS) == 51
    assert "DC" in IL_COSTS
    assert "CA" in IL_COSTS
    # Spot-check a few values
    ca = get_il_cost("CA")
    assert ca["state"] == "California"
    dc = get_il_cost("DC")
    assert dc["state"] == "District of Columbia"


from colivingscore.silver_living.fips import (
    STATE_FIPS,
    is_valid_state_fips,
    is_valid_county_fips,
)
from unittest.mock import patch as _patch, MagicMock as _MagicMock


def test_state_fips_texas():
    assert STATE_FIPS["TX"] == "48"


def test_state_fips_dc():
    assert STATE_FIPS["DC"] == "11"


def test_is_valid_state_fips_known():
    assert is_valid_state_fips("48") is True


def test_is_valid_state_fips_unknown():
    assert is_valid_state_fips("99") is False


def _mock_county_response():
    m = _MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = [
        ["NAME", "state", "county"],
        ["Dallas County, Texas", "48", "113"],
        ["Tarrant County, Texas", "48", "439"],
        ["Harris County, Texas", "48", "201"],
    ]
    return m


def test_is_valid_county_fips_dallas():
    with _patch("colivingscore.silver_living.fips.requests.get", return_value=_mock_county_response()):
        # Clear cache so mock is used
        from colivingscore.silver_living import fips as _fips
        _fips._county_cache.clear()
        assert is_valid_county_fips("48", "113") is True


def test_is_valid_county_fips_bad():
    with _patch("colivingscore.silver_living.fips.requests.get", return_value=_mock_county_response()):
        from colivingscore.silver_living import fips as _fips
        _fips._county_cache.clear()
        assert is_valid_county_fips("48", "000") is False


from unittest.mock import patch, MagicMock
from colivingscore.silver_living.census import get_demographics

_MOCK_B09020_CURRENT = [
    ["B09020_001E", "B09020_021E", "state", "county"],
    ["142810", "44271", "48", "113"]
]
_MOCK_B09020_PRIOR = [
    ["B09020_001E", "B09020_021E", "state", "county"],
    ["108855", "33700", "48", "113"]
]
_MOCK_S0101 = [
    ["S0101_C01_008E","S0101_C01_009E","S0101_C01_010E",
     "S0101_C01_011E","S0101_C01_012E","S0101_C01_013E",
     "S0101_C01_014E","state","county"],
    ["112000","98000","88000","140000","98000","72000","52000","48","113"]
]
_MOCK_PUMS = [
    ["CIT", "PWGTP", "AGEP", "state"],
    ["1", "500", "70", "48"],
    ["2", "300", "68", "48"],
    ["3", "100", "72", "48"],
    ["4", "50",  "66", "48"],
    ["5", "60",  "67", "48"],
    ["1", "200", "40", "48"],  # under 65, should be excluded
]


def _mock_resp(data):
    m = MagicMock()
    m.json.return_value = data
    m.raise_for_status.return_value = None
    return m


def test_get_demographics_structure():
    from colivingscore.silver_living import census as _census
    _census._cache.clear()
    with patch("colivingscore.silver_living.census.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_resp(_MOCK_B09020_CURRENT),
            _mock_resp(_MOCK_B09020_PRIOR),
            _mock_resp(_MOCK_S0101),
            _mock_resp(_MOCK_PUMS),
        ]
        result = get_demographics("48", "113")
    assert "pop65" in result
    assert "living_alone" in result
    assert "living_alone_pct" in result
    assert "growth_pct" in result
    assert "age_brackets" in result
    assert "citizenship" in result


def test_get_demographics_pop65():
    from colivingscore.silver_living import census as _census
    _census._cache.clear()
    with patch("colivingscore.silver_living.census.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_resp(_MOCK_B09020_CURRENT),
            _mock_resp(_MOCK_B09020_PRIOR),
            _mock_resp(_MOCK_S0101),
            _mock_resp(_MOCK_PUMS),
        ]
        result = get_demographics("48", "113")
    assert result["pop65"] == 142810
    assert result["living_alone"] == 44271
    assert result["living_alone_pct"] == round(44271 / 142810 * 100, 1)


def test_get_demographics_growth():
    from colivingscore.silver_living import census as _census
    _census._cache.clear()
    with patch("colivingscore.silver_living.census.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_resp(_MOCK_B09020_CURRENT),
            _mock_resp(_MOCK_B09020_PRIOR),
            _mock_resp(_MOCK_S0101),
            _mock_resp(_MOCK_PUMS),
        ]
        result = get_demographics("48", "113")
    assert result["growth_pct"] == round((142810 - 108855) / 108855 * 100, 1)


def test_get_demographics_age_brackets():
    from colivingscore.silver_living import census as _census
    _census._cache.clear()
    with patch("colivingscore.silver_living.census.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_resp(_MOCK_B09020_CURRENT),
            _mock_resp(_MOCK_B09020_PRIOR),
            _mock_resp(_MOCK_S0101),
            _mock_resp(_MOCK_PUMS),
        ]
        result = get_demographics("48", "113")
    brackets = result["age_brackets"]
    assert len(brackets) == 7
    assert brackets[0] == {"label": "55–59", "count": 112000, "target": False}
    assert brackets[2] == {"label": "65–69", "count": 88000, "target": True}


def test_get_demographics_citizenship():
    from colivingscore.silver_living import census as _census
    _census._cache.clear()
    with patch("colivingscore.silver_living.census.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_resp(_MOCK_B09020_CURRENT),
            _mock_resp(_MOCK_B09020_PRIOR),
            _mock_resp(_MOCK_S0101),
            _mock_resp(_MOCK_PUMS),
        ]
        result = get_demographics("48", "113")
    cit = result["citizenship"]
    assert "citizen_pct" in cit
    assert "noncitizen_pct" in cit
    # citizen weight = 500+300+100+50=950, non-citizen=60, under-65 (200) excluded
    assert cit["citizen_pct"] == round(950 / 1010 * 100, 1)


def test_get_demographics_cached():
    """Second call with same FIPS returns cached result without extra API calls."""
    from colivingscore.silver_living import census as _census
    _census._cache.clear()
    with patch("colivingscore.silver_living.census.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_resp(_MOCK_B09020_CURRENT),
            _mock_resp(_MOCK_B09020_PRIOR),
            _mock_resp(_MOCK_S0101),
            _mock_resp(_MOCK_PUMS),
        ]
        get_demographics("48", "113")
        get_demographics("48", "113")  # second call
    assert mock_get.call_count == 4  # only 4 calls, not 8


import json
from unittest.mock import patch


def _get_app():
    from colivingscore.app import app
    app.config["TESTING"] = True
    return app


def test_silver_living_page_loads():
    client = _get_app().test_client()
    resp = client.get("/silver-living")
    assert resp.status_code == 200
    assert b"Silver Living" in resp.data


def test_counties_endpoint_texas():
    _mock_counties = [
        {"name": "Dallas County", "fips": "113"},
        {"name": "Harris County", "fips": "201"},
    ]
    with patch("colivingscore.silver_living.routes.get_counties", return_value=_mock_counties):
        client = _get_app().test_client()
        resp = client.get("/api/silver-living/counties?state=TX")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "counties" in data
    names = [c["name"] for c in data["counties"]]
    assert "Dallas County" in names


def test_counties_endpoint_invalid_state():
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/counties?state=XX")
    assert resp.status_code == 400


def test_lookup_endpoint_validates_fips():
    with patch("colivingscore.silver_living.routes.is_valid_county_fips", return_value=False):
        client = _get_app().test_client()
        resp = client.get("/api/silver-living/lookup?state=48&county=000")
    assert resp.status_code == 400


def test_lookup_endpoint_invalid_state_fips():
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/lookup?state=99&county=113")
    assert resp.status_code == 400


def test_lookup_endpoint_returns_demographics():
    _MOCK_DEMO = {
        "pop65": 219430, "living_alone": 67024, "living_alone_pct": 30.5,
        "growth_pct": 31.2,
        "age_brackets": [{"label": "55–59", "count": 112000, "target": False}],
        "citizenship": {"citizen_pct": 89.0, "noncitizen_pct": 11.0},
    }
    with patch("colivingscore.silver_living.routes.get_demographics", return_value=_MOCK_DEMO), \
         patch("colivingscore.silver_living.routes.is_valid_county_fips", return_value=True):
        client = _get_app().test_client()
        resp = client.get("/api/silver-living/lookup?state=48&county=113")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["pop65"] == 219430
    assert "il_cost" in data
    assert data["il_cost"]["range"] is not None


# ============================================================================
# Security Hardening Tests (Tasks 1-13)
# ============================================================================

# Input injection / traversal on counties endpoint
def test_counties_invalid_state_empty():
    """Empty state parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/counties?state=")
    assert resp.status_code == 400


def test_counties_sql_injection():
    """SQL injection attempt in state parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/counties?state=TX'; DROP TABLE--")
    assert resp.status_code == 400


def test_counties_path_traversal():
    """Path traversal attempt in state parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/counties?state=../../etc")
    assert resp.status_code == 400


def test_counties_xss_attempt():
    """XSS attempt in state parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/counties?state=<script>alert(1)</script>")
    assert resp.status_code == 400


def test_counties_numeric_state():
    """FIPS number instead of state abbreviation should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/counties?state=48")
    assert resp.status_code == 400


# Input injection on lookup endpoint
def test_lookup_invalid_state_fips():
    """Invalid state FIPS (99) should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/lookup?state=99&county=001")
    assert resp.status_code == 400


def test_lookup_sql_injection_state():
    """SQL injection attempt in state parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/lookup?state=48'; DROP--&county=113")
    assert resp.status_code == 400


def test_lookup_path_traversal_county():
    """Path traversal attempt in county parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/lookup?state=48&county=../../etc")
    assert resp.status_code == 400


def test_lookup_xss_county():
    """XSS attempt in county parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/lookup?state=48&county=<img src=x>")
    assert resp.status_code == 400


def test_lookup_empty_params():
    """No parameters should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/lookup")
    assert resp.status_code == 400


def test_lookup_missing_county():
    """Missing county parameter should return 400."""
    client = _get_app().test_client()
    resp = client.get("/api/silver-living/lookup?state=48")
    assert resp.status_code == 400


# Response safety
def test_lookup_response_is_json():
    """Valid lookup should return application/json content type."""
    _MOCK_DEMO = {
        "pop65": 219430, "living_alone": 67024, "living_alone_pct": 30.5,
        "growth_pct": 31.2,
        "age_brackets": [{"label": "55–59", "count": 112000, "target": False}],
        "citizenship": {"citizen_pct": 89.0, "noncitizen_pct": 11.0},
    }
    with patch("colivingscore.silver_living.routes.get_demographics", return_value=_MOCK_DEMO), \
         patch("colivingscore.silver_living.routes.is_valid_county_fips", return_value=True):
        client = _get_app().test_client()
        resp = client.get("/api/silver-living/lookup?state=48&county=113")
    assert resp.status_code == 200
    assert resp.content_type == "application/json"


def test_counties_response_is_json():
    """Valid counties endpoint should return application/json content type."""
    _mock_counties = [
        {"name": "Dallas County", "fips": "113"},
        {"name": "Harris County", "fips": "201"},
    ]
    with patch("colivingscore.silver_living.routes.get_counties", return_value=_mock_counties):
        client = _get_app().test_client()
        resp = client.get("/api/silver-living/counties?state=TX")
    assert resp.status_code == 200
    assert resp.content_type == "application/json"
