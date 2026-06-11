from __future__ import annotations

from umbrella_agent.recommendation_engine import recommend


def test_precip_60_or_more_returns_yes() -> None:
    result = recommend({"precipitation_probability": 60})
    assert result["recommendation"] == "yes"
    assert result["confidence"] == 0.7


def test_precip_80_returns_yes() -> None:
    result = recommend({"precipitation_probability": 80})
    assert result["recommendation"] == "yes"
    assert result["confidence"] == 0.7


def test_precip_100_returns_yes() -> None:
    result = recommend({"precipitation_probability": 100})
    assert result["recommendation"] == "yes"
    assert result["confidence"] == 0.7


def test_precip_30_returns_maybe() -> None:
    result = recommend({"precipitation_probability": 30})
    assert result["recommendation"] == "maybe"
    assert result["confidence"] == 0.4


def test_precip_45_returns_maybe() -> None:
    result = recommend({"precipitation_probability": 45})
    assert result["recommendation"] == "maybe"
    assert result["confidence"] == 0.4


def test_precip_59_returns_maybe() -> None:
    result = recommend({"precipitation_probability": 59})
    assert result["recommendation"] == "maybe"
    assert result["confidence"] == 0.4


def test_precip_below_30_returns_no() -> None:
    result = recommend({"precipitation_probability": 29})
    assert result["recommendation"] == "no"
    assert result["confidence"] == 0.8


def test_precip_0_returns_no() -> None:
    result = recommend({"precipitation_probability": 0})
    assert result["recommendation"] == "no"
    assert result["confidence"] == 0.8


def test_precip_10_returns_no() -> None:
    result = recommend({"precipitation_probability": 10})
    assert result["recommendation"] == "no"
    assert result["confidence"] == 0.8


def test_precip_none_returns_unknown() -> None:
    result = recommend({"precipitation_probability": None})
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == 0.0


def test_precip_missing_returns_unknown() -> None:
    result = recommend({})
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == 0.0


def test_deterministic_same_input_same_output() -> None:
    data = {"precipitation_probability": 60}
    r1 = recommend(data)
    r2 = recommend(data)
    assert r1 == r2


def test_all_11_fixture_locations() -> None:
    from tool_gateway.seed_tools.weather_fixture_read import FIXTURES, WeatherFixtureReadTool

    tool = WeatherFixtureReadTool()
    for location in FIXTURES:
        result = tool(location=location, date=WeatherFixtureReadTool.FIXTURE_DATE_UTC)
        assert result["success"]
        rec = recommend(result["data"])
        assert rec["recommendation"] in ("yes", "maybe", "no")
        assert 0.0 <= rec["confidence"] <= 1.0
