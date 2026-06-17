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


def test_state_fips_texas():
    assert STATE_FIPS["TX"] == "48"


def test_state_fips_dc():
    assert STATE_FIPS["DC"] == "11"


def test_is_valid_state_fips_known():
    assert is_valid_state_fips("48") is True


def test_is_valid_state_fips_unknown():
    assert is_valid_state_fips("99") is False


def test_is_valid_county_fips_dallas():
    # Dallas County, TX = FIPS 48113 — makes a live Census API call
    assert is_valid_county_fips("48", "113") is True


def test_is_valid_county_fips_bad():
    assert is_valid_county_fips("48", "000") is False
