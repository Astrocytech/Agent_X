from __future__ import annotations

from umbrella_agent.recommendation_engine import recommend


class TestUmbrellaBorderlineWeather:
    """Test borderline-weather scenarios that the original engine missed."""

    def test_drizzle_at_35_recommends_maybe(self) -> None:
        result = recommend({"precipitation_probability": 35, "condition": "drizzle"})
        assert result["recommendation"] == "maybe"
        assert result["confidence"] == 0.4

    def test_drizzle_at_25_recommends_maybe(self) -> None:
        result = recommend({"precipitation_probability": 25, "condition": "drizzle"})
        assert result["recommendation"] == "maybe"
        assert result["confidence"] == 0.4

    def test_drizzle_at_5_recommends_no(self) -> None:
        result = recommend({"precipitation_probability": 5, "condition": "drizzle"})
        assert result["recommendation"] == "no"

    def test_drizzle_at_45_recommends_maybe(self) -> None:
        result = recommend({"precipitation_probability": 45, "condition": "drizzle"})
        # Should fall through to standard logic (>=30)
        assert result["recommendation"] == "maybe"

    def test_snow_at_25_recommends_yes(self) -> None:
        result = recommend({"precipitation_probability": 25, "condition": "snow"})
        assert result["recommendation"] == "yes"
        assert result["confidence"] == 0.6

    def test_snow_at_65_recommends_yes(self) -> None:
        result = recommend({"precipitation_probability": 65, "condition": "snow"})
        assert result["recommendation"] == "yes"

    def test_snow_at_10_recommends_no(self) -> None:
        result = recommend({"precipitation_probability": 10, "condition": "snow"})
        assert result["recommendation"] == "no"

    def test_rain_at_60_still_yes(self) -> None:
        result = recommend({"precipitation_probability": 60, "condition": "rain"})
        assert result["recommendation"] == "yes"
        assert result["confidence"] == 0.7

    def test_missing_data_failsafe(self) -> None:
        result = recommend({})
        assert result["recommendation"] == "unknown"
        assert result["confidence"] == 0.0

    def test_non_dict_failsafe(self) -> None:
        result = recommend(None)  # type: ignore
        assert result["recommendation"] == "unknown"
        assert result["confidence"] == 0.0

    def test_vancouver_fixture_borderline(self) -> None:
        from tool_gateway.seed_tools.weather_fixture_read import WeatherFixtureReadTool
        tool = WeatherFixtureReadTool()
        result = tool(location="vancouver", date=WeatherFixtureReadTool.FIXTURE_DATE_UTC)
        assert result["success"]
        assert result["data"]["condition"] == "drizzle"
        rec = recommend(result["data"])
        assert rec["recommendation"] == "maybe"

    def test_reykjavik_fixture_snow(self) -> None:
        from tool_gateway.seed_tools.weather_fixture_read import WeatherFixtureReadTool
        tool = WeatherFixtureReadTool()
        result = tool(location="reykjavik", date=WeatherFixtureReadTool.FIXTURE_DATE_UTC)
        assert result["success"]
        assert result["data"]["condition"] == "snow"
        rec = recommend(result["data"])
        assert rec["recommendation"] == "yes"

    def test_existing_tests_still_pass(self) -> None:
        """Verify original test cases still produce correct results."""
        assert recommend({"precipitation_probability": 60})["recommendation"] == "yes"
        assert recommend({"precipitation_probability": 30})["recommendation"] == "maybe"
        assert recommend({"precipitation_probability": 10})["recommendation"] == "no"
        assert recommend({"precipitation_probability": None})["recommendation"] == "unknown"
        assert recommend({})["recommendation"] == "unknown"
