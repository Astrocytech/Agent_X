from __future__ import annotations

import pytest
from umbrella_agent.recommendation_engine import recommend


def test_rain_high_prob_yes():
    r = recommend({"condition": "rain", "precipitation_probability": 80})
    assert r["recommendation"] == "yes"
    assert r["confidence"] >= 0.6


def test_rain_moderate_yes():
    r = recommend({"condition": "rain", "precipitation_probability": 50})
    assert r["recommendation"] == "yes"


def test_rain_low_prob_maybe():
    r = recommend({"condition": "rain", "precipitation_probability": 20})
    assert r["recommendation"] == "maybe"


def test_shower_yes():
    r = recommend({"condition": "shower", "precipitation_probability": 60})
    assert r["recommendation"] == "yes"


def test_thunderstorm_yes():
    r = recommend({"condition": "thunderstorm", "precipitation_probability": 50})
    assert r["recommendation"] == "yes"


def test_drizzle_maybe():
    r = recommend({"condition": "drizzle", "precipitation_probability": 35})
    assert r["recommendation"] == "maybe"


def test_storm_alert():
    r = recommend({"condition": "storm", "precipitation_probability": 90})
    assert r["recommendation"] == "alert"
    assert r["confidence"] == 0.9


def test_heavy_rain_alert():
    r = recommend({"condition": "heavy rain", "precipitation_probability": 80})
    assert r["recommendation"] == "alert"


def test_freezing_rain_alert():
    r = recommend({"condition": "freezing rain", "precipitation_probability": 70})
    assert r["recommendation"] == "alert"


def test_sleet_alert():
    r = recommend({"condition": "sleet", "precipitation_probability": 60})
    assert r["recommendation"] == "alert"


def test_hail_alert():
    r = recommend({"condition": "hail", "precipitation_probability": 50})
    assert r["recommendation"] == "alert"


def test_clear_no():
    r = recommend({"condition": "clear", "precipitation_probability": 0})
    assert r["recommendation"] == "no"
    assert r["confidence"] >= 0.8


def test_clear_low_precip_no():
    r = recommend({"condition": "clear", "precipitation_probability": 5})
    assert r["recommendation"] == "no"


def test_cloudy_low_precip_no():
    r = recommend({"condition": "cloudy", "precipitation_probability": 10})
    assert r["recommendation"] == "no"


def test_cloudy_high_precip_maybe():
    r = recommend({"condition": "cloudy", "precipitation_probability": 60})
    assert r["recommendation"] == "maybe"


def test_snow_high_precip_yes():
    r = recommend({"condition": "snow", "precipitation_probability": 50})
    assert r["recommendation"] == "yes"


def test_snow_low_precip_no():
    r = recommend({"condition": "snow", "precipitation_probability": 5})
    assert r["recommendation"] == "no"


def test_malformed_non_string_condition():
    r = recommend({"condition": 42, "precipitation_probability": 50})
    assert r["recommendation"] == "unknown"


def test_malformed_missing_condition():
    r = recommend({"precipitation_probability": 50})
    assert r["recommendation"] == "unknown"


def test_missing_precip():
    r = recommend({"condition": "rain"})
    assert r["recommendation"] == "unknown"


def test_none_input():
    r = recommend(None)
    assert r["recommendation"] == "unknown"


def test_empty_dict():
    r = recommend({})
    assert r["recommendation"] == "unknown"


def test_provider_failure():
    r = recommend({"success": False, "error": "provider timeout"})
    assert r["recommendation"] == "unknown"


def test_output_has_all_fields():
    r = recommend({"condition": "rain", "precipitation_probability": 80})
    for field in ("recommendation", "answer", "reason", "weather_source", "confidence"):
        assert field in r


def test_deterministic():
    data = {"condition": "rain", "precipitation_probability": 75}
    r1 = recommend(data)
    r2 = recommend(data)
    assert r1 == r2


def test_weather_source_propagated():
    r = recommend({"condition": "rain", "precipitation_probability": 60, "source": "fixture"})
    assert r["weather_source"] == "fixture"


def test_weather_source_fallback():
    r = recommend({"condition": "rain", "precipitation_probability": 60, "provider": "test_prov"})
    assert r["weather_source"] == "test_prov"


def test_edge_precip_boundary_59():
    r = recommend({"condition": "rain", "precipitation_probability": 59})
    assert r["recommendation"] == "yes"


def test_edge_precip_boundary_60():
    r = recommend({"condition": "rain", "precipitation_probability": 60})
    assert r["recommendation"] == "yes"


def test_oslo_fixture():
    r = recommend({"condition": "cloudy", "precipitation_probability": 55, "source": "fixture"})
    assert r["recommendation"] in ("maybe", "no")


def test_unknown_condition_high_precip():
    r = recommend({"condition": "monsoon", "precipitation_probability": 80})
    assert r["recommendation"] == "yes"


def test_unknown_condition_low_precip():
    r = recommend({"condition": "monsoon", "precipitation_probability": 10})
    assert r["recommendation"] == "no"
