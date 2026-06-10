from __future__ import annotations

from clothing_advice_agent import ask_clothing
from tool_gateway.seed_tools.clothing_fixture_read import ClothingFixtureReadTool


def test_ask_unknown_location_returns_unknown() -> None:
    result = ask_clothing("Atlantis")
    assert result["recommendation"] == "unknown"
    assert result["safe_failure"] is True


def test_output_contains_all_required_fields() -> None:
    result = ask_clothing("below_0_deg")
    required = {"recommendation", "reason", "confidence", "data_source", "safe_failure", "location"}
    assert required.issubset(result.keys())


def test_safe_failure_is_true_for_missing_data() -> None:
    result = ask_clothing("missing_data")
    assert result["safe_failure"] is True


def test_safe_failure_is_true_for_malformed_temp() -> None:
    result = ask_clothing("malformed_temp")
    assert result["safe_failure"] is True


def test_recommendation_is_valid_for_known_location() -> None:
    result = ask_clothing("below_0_deg")
    valid = ("warm", "cool", "moderate", "light", "hot", "rain_gear",
             "snow_gear", "wind_block", "shelter", "unknown")
    assert result["recommendation"] in valid
    assert isinstance(result["reason"], str)
    assert len(result["reason"]) > 0


def test_tool_gateway_registered() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="below_0_deg")
    assert result["success"]
    assert result["data"]["temperature_c"] == -5
    assert result["data"]["condition"] == "snow"


def test_tool_gateway_unknown_location() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="Atlantis")
    assert not result["success"]


def test_output_runtime_null_location() -> None:
    result = ask_clothing("")
    assert result["recommendation"] == "unknown"
    assert result["safe_failure"] is True
