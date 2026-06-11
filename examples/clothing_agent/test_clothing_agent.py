from __future__ import annotations

from clothing_agent.agent import ClothingAgent
from clothing_agent.fixtures import FIXTURES


def test_cold_weather_recommends_warm_clothing() -> None:
    result = ClothingAgent().recommend("cold_day")
    assert result["recommendation"] == "warm_clothing"
    assert "heavy coat" in result["items"]
    assert result["confidence"] == "high"
    assert result["source"] == "fixture"


def test_hot_weather_recommends_light_clothing() -> None:
    result = ClothingAgent().recommend("hot_day")
    assert result["recommendation"] == "light_clothing"
    assert "t-shirt" in result["items"]
    assert result["confidence"] == "high"


def test_rainy_weather_recommends_rain_gear() -> None:
    result = ClothingAgent().recommend("rainy_day")
    assert result["recommendation"] == "rain_gear"
    assert "raincoat" in result["items"]
    assert "umbrella" in result["items"]


def test_windy_weather_recommends_wind_protection() -> None:
    result = ClothingAgent().recommend("windy_day")
    assert result["recommendation"] == "wind_protection"
    assert "windbreaker" in result["items"]


def test_formal_event_recommends_formal_wear() -> None:
    result = ClothingAgent().recommend("formal_event")
    assert result["recommendation"] == "formal_wear"
    assert "suit" in result["items"]


def test_casual_day_recommends_casual_wear() -> None:
    result = ClothingAgent().recommend("casual_day")
    assert result["recommendation"] == "casual_wear"
    assert "jeans" in result["items"]


def test_missing_weather_returns_unknown() -> None:
    result = ClothingAgent().recommend("missing_weather")
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == "low"
    assert result["source"] == "fixture"


def test_malformed_fixture_fails_safely() -> None:
    result = ClothingAgent().recommend("malformed_fixture")
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == "low"
    assert "Malformed" in result["reason"]


def test_none_location_returns_unknown() -> None:
    result = ClothingAgent().recommend(None)
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == "unknown"
    assert result["items"] == []


def test_empty_location_returns_unknown() -> None:
    result = ClothingAgent().recommend("")
    assert result["recommendation"] == "unknown"


def test_unknown_location_returns_unknown() -> None:
    result = ClothingAgent().recommend("nonexistent_city")
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == "unknown"


def test_output_contract_has_all_required_fields() -> None:
    result = ClothingAgent().recommend("cold_day")
    assert "recommendation" in result
    assert "items" in result
    assert "reason" in result
    assert "source" in result
    assert "confidence" in result


def test_all_fixtures_produce_valid_output() -> None:
    agent = ClothingAgent()
    for location in FIXTURES:
        result = agent.recommend(location)
        assert "recommendation" in result
        assert "items" in result
        assert "reason" in result
        assert result["source"] == "fixture"
        assert result["confidence"] in ("high", "medium", "low", "unknown")


def test_cold_weather_reason_includes_temperature() -> None:
    result = ClothingAgent().recommend("cold_day")
    assert "-2" in result["reason"] or "cold" in result["reason"].lower()


def test_hot_weather_reason_includes_temperature() -> None:
    result = ClothingAgent().recommend("hot_day")
    assert "35" in result["reason"] or "hot" in result["reason"].lower()


def test_recommendation_is_string() -> None:
    result = ClothingAgent().recommend("cold_day")
    assert isinstance(result["recommendation"], str)


def test_items_is_list() -> None:
    result = ClothingAgent().recommend("cold_day")
    assert isinstance(result["items"], list)


def test_reason_is_string() -> None:
    result = ClothingAgent().recommend("cold_day")
    assert isinstance(result["reason"], str)


def test_formal_event_overrides_weather() -> None:
    result = ClothingAgent().recommend("formal_event")
    assert result["recommendation"] == "formal_wear"
    assert result["confidence"] == "high"
    assert "formal" in result["reason"].lower()


def test_windy_reason_includes_wind_speed() -> None:
    result = ClothingAgent().recommend("windy_day")
    assert "45" in result["reason"] or "wind" in result["reason"].lower()
