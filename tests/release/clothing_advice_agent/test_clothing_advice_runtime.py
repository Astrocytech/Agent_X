from __future__ import annotations

from clothing_advice_agent import ask_clothing
from tool_gateway.seed_tools.clothing_fixture_read import ClothingFixtureReadTool


_VALID_RECOMMENDATIONS = frozenset({
    "warm", "cool", "moderate", "light", "hot", "rain_gear",
    "snow_gear", "wind_block", "shelter", "unknown",
})


def _assert_valid_output(result: dict, *, safe_failure: bool | None = None) -> None:
    required = {"recommendation", "reason", "confidence", "data_source", "safe_failure", "location"}
    assert required.issubset(result.keys())
    assert result["recommendation"] in _VALID_RECOMMENDATIONS
    assert isinstance(result["reason"], str)
    assert len(result["reason"]) > 0
    if safe_failure is not None:
        assert result["safe_failure"] is safe_failure


# ── 1. Unknown location ──────────────────────────────────────────────────────

def test_ask_unknown_location_returns_unknown() -> None:
    result = ask_clothing("Atlantis")
    assert result["recommendation"] == "unknown"
    assert result["safe_failure"] is True


# ── 2–3. Temperature band: below_0_deg ──────────────────────────────────────

def test_output_contains_all_required_fields() -> None:
    _assert_valid_output(ask_clothing("below_0_deg"))


def test_recommendation_is_valid_for_known_location() -> None:
    _assert_valid_output(ask_clothing("below_0_deg"), safe_failure=False)


# ── 4. Missing data (null fields) ────────────────────────────────────────────

def test_safe_failure_is_true_for_missing_data() -> None:
    result = ask_clothing("missing_data")
    assert result["safe_failure"] is True


# ── 5. Malformed temperature ─────────────────────────────────────────────────

def test_safe_failure_is_true_for_malformed_temp() -> None:
    result = ask_clothing("malformed_temp")
    assert result["safe_failure"] is True


# ── 6. Tool gateway: known location ──────────────────────────────────────────

def test_tool_gateway_registered() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="below_0_deg")
    assert result["success"]
    assert result["data"]["temperature_c"] == -5
    assert result["data"]["condition"] == "snow"


# ── 7. Tool gateway: unknown location ────────────────────────────────────────

def test_tool_gateway_unknown_location() -> None:
    tool = ClothingFixtureReadTool()
    result = tool(location="Atlantis")
    assert not result["success"]


# ── 8. Empty / null location ─────────────────────────────────────────────────

def test_output_runtime_null_location() -> None:
    result = ask_clothing("")
    assert result["recommendation"] == "unknown"
    assert result["safe_failure"] is True


# ── 9. Temperature band: hot ─────────────────────────────────────────────────

def test_hot_temperature_band() -> None:
    _assert_valid_output(ask_clothing("hot_32"), safe_failure=False)


# ── 10. Temperature band: chilly ─────────────────────────────────────────────

def test_chilly_temperature_band() -> None:
    _assert_valid_output(ask_clothing("chilly_5"), safe_failure=False)


# ── 11. Weather: severe storm (severe_weather_flag) ──────────────────────────

def test_severe_storm_returns_shelter_or_valid() -> None:
    _assert_valid_output(ask_clothing("severe_storm"), safe_failure=False)


# ── 12. Weather: rainy day ───────────────────────────────────────────────────

def test_rainy_day() -> None:
    _assert_valid_output(ask_clothing("rainy_day"), safe_failure=False)


# ── 13. Weather: windy day ───────────────────────────────────────────────────

def test_windy_day() -> None:
    _assert_valid_output(ask_clothing("windy_day"), safe_failure=False)


# ── 14. Weather: foggy condition ─────────────────────────────────────────────

def test_fog_condition() -> None:
    _assert_valid_output(ask_clothing("fog_condition"), safe_failure=False)


# ── 15. Contradictory data (hot + rain + 0% precip) ──────────────────────────

def test_contradictory_data() -> None:
    _assert_valid_output(ask_clothing("contradictory_data"), safe_failure=False)
