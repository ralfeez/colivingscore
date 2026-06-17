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
