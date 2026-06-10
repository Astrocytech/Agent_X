from __future__ import annotations

from tool_gateway.seed_tools.clothing_fixture_read import FIXTURES
from clothing_advice_agent import ask_clothing


def test_full_pipeline_below_0_deg() -> None:
    result = ask_clothing("below_0_deg")
    valid = ("warm", "cool", "moderate", "light", "hot", "rain_gear",
             "snow_gear", "wind_block", "shelter", "unknown")
    assert result["recommendation"] in valid
    assert isinstance(result["reason"], str) and len(result["reason"]) > 0


def test_full_pipeline_hot_32() -> None:
    result = ask_clothing("hot_32")
    valid = ("warm", "cool", "moderate", "light", "hot", "rain_gear",
             "snow_gear", "wind_block", "shelter", "unknown")
    assert result["recommendation"] in valid
    assert isinstance(result["reason"], str) and len(result["reason"]) > 0


def test_full_pipeline_rainy_day() -> None:
    result = ask_clothing("rainy_day")
    valid = ("warm", "cool", "moderate", "light", "hot", "rain_gear",
             "snow_gear", "wind_block", "shelter", "unknown")
    assert result["recommendation"] in valid
    assert isinstance(result["reason"], str) and len(result["reason"]) > 0


def test_all_fields_present_in_output() -> None:
    result = ask_clothing("below_0_deg")
    assert "recommendation" in result
    assert "reason" in result
    assert "confidence" in result
    assert "data_source" in result
    assert "safe_failure" in result
    assert "location" in result


def test_safe_failure_false_for_valid_data() -> None:
    result = ask_clothing("below_0_deg")
    assert result["safe_failure"] is False


def test_pipeline_unknown_location() -> None:
    result = ask_clothing("Atlantis")
    assert result["recommendation"] == "unknown"
    assert result["safe_failure"] is True


def test_pipeline_all_fixtures() -> None:
    for location in FIXTURES:
        result = ask_clothing(location)
        valid = ("warm", "cool", "moderate", "light", "hot", "rain_gear",
                 "snow_gear", "wind_block", "shelter", "unknown")
        assert result["recommendation"] in valid
        assert isinstance(result["reason"], str) and len(result["reason"]) > 0
