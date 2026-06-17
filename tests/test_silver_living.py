import pytest
from colivingscore.silver_living.il_costs import get_il_cost


def test_known_state_returns_range():
    result = get_il_cost("TX")
    assert result is not None
    assert "range" in result
    assert "source" in result
    assert result["source"] == "SeniorLiving.org, 2026"


def test_unknown_state_returns_none():
    assert get_il_cost("XX") is None


def test_all_50_states_plus_dc_present():
    from colivingscore.silver_living.il_costs import IL_COSTS
    assert len(IL_COSTS) == 51
    assert "DC" in IL_COSTS
    assert "CA" in IL_COSTS
