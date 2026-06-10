from __future__ import annotations

from tool_gateway.seed_tools.clothing_fixture_read import FIXTURES, ClothingFixtureReadTool
from clothing_advice_agent.planner import ClothingPlannerPort


def test_tool_returns_data_for_below_0_deg() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="below_0_deg")
    assert result["success"]
    assert result["data"]["temperature_c"] == -5


def test_tool_returns_data_for_chilly_5() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="chilly_5")
    assert result["success"]
    assert result["data"]["temperature_c"] == 5


def test_tool_returns_data_for_cool_12() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="cool_12")
    assert result["success"]
    assert result["data"]["temperature_c"] == 12


def test_tool_returns_data_for_mild_20() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="mild_20")
    assert result["success"]
    assert result["data"]["temperature_c"] == 20


def test_tool_returns_data_for_hot_32() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="hot_32")
    assert result["success"]
    assert result["data"]["temperature_c"] == 32


def test_tool_returns_data_for_rainy_day() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="rainy_day")
    assert result["success"]
    assert result["data"]["condition"] == "rain"


def test_tool_returns_data_for_snowy_day() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="snowy_day")
    assert result["success"]
    assert result["data"]["condition"] == "snow"


def test_tool_returns_data_for_windy_day() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="windy_day")
    assert result["success"]
    assert result["data"]["wind_speed_kph"] == 50


def test_tool_returns_data_for_severe_storm() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="severe_storm")
    assert result["success"]
    assert result["data"]["severe_weather_flag"] is True


def test_tool_returns_data_for_missing_data() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="missing_data")
    assert result["success"]
    assert result["data"]["temperature_c"] is None


def test_tool_returns_data_for_contradictory_data() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="contradictory_data")
    assert result["success"]
    assert result["data"]["condition"] == "rain"
    assert result["data"]["precipitation_probability"] == 0


def test_tool_returns_data_for_malformed_temp() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="malformed_temp")
    assert result["success"]
    assert result["data"]["temperature_c"] == "not-a-number"


def test_tool_returns_data_for_bad_precip() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="bad_precip")
    assert result["success"]
    assert result["data"]["precipitation_probability"] == "invalid"


def test_tool_null_location_returns_failure() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location=None)
    assert not result["success"]


def test_tool_empty_location_returns_failure() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="")
    assert not result["success"]


def test_all_fixture_locations_success() -> None:
    tool = ClothingFixtureReadTool()
    for location in FIXTURES:
        result = tool(location=location)
        assert result["success"], f"Location {location} failed"
        assert "data" in result


def test_tool_api_endpoint_in_response() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="below_0_deg")
    assert result["success"]
    assert result["data"]["api_endpoint"] == \
        "https://api.clothing.example.com/current?location=below_0_deg"
    assert result["data"]["api_status"] == 200


def test_parse_llm_json_extracts_plain_json() -> None:
    raw = '{"recommendation": "warm", "reason": "Cold weather", "confidence": "high"}'
    result = ClothingPlannerPort._parse_llm_json(raw)
    assert result is not None
    assert result["recommendation"] == "warm"


def test_parse_llm_json_extracts_from_markdown() -> None:
    raw = '```json\n{"recommendation": "cool", "reason": "Chilly", "confidence": "medium"}\n```'
    result = ClothingPlannerPort._parse_llm_json(raw)
    assert result is not None
    assert result["recommendation"] == "cool"


def test_parse_llm_json_extracts_with_surrounding_text() -> None:
    raw = 'Here is the result:\n{"recommendation": "hot", "reason": "Very hot", "confidence": "high"}\nDone.'
    result = ClothingPlannerPort._parse_llm_json(raw)
    assert result is not None
    assert result["recommendation"] == "hot"


def test_parse_llm_json_returns_none_for_invalid() -> None:
    assert ClothingPlannerPort._parse_llm_json("not json") is None
    assert ClothingPlannerPort._parse_llm_json("") is None
    assert ClothingPlannerPort._parse_llm_json("{}") is not None


def test_build_output_safe_failure_for_none_data() -> None:
    planner = ClothingPlannerPort()
    output = planner._build_output(None)
    assert output["safe_failure"] is True
    assert output["recommendation"] == "unknown"
