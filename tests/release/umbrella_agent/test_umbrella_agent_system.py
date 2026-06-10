from __future__ import annotations

from tool_gateway.seed_tools.weather_fixture_read import FIXTURES
from umbrella_agent import ask_umbrella


def test_full_pipeline_london() -> None:
    """End-to-end: user question → KernelService → LLM calls weather.fixture.read
    → LLM applies §3 rules → seed.emit_answer → structured JSON output."""
    result = ask_umbrella("London", "today")
    assert result["recommendation"] in ("yes", "maybe", "no")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 0


def test_full_pipeline_paris() -> None:
    result = ask_umbrella("Paris", "today")
    assert result["recommendation"] in ("yes", "maybe", "no")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 0


def test_full_pipeline_berlin() -> None:
    result = ask_umbrella("Berlin", "today")
    assert result["recommendation"] in ("yes", "maybe", "no")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 0


def test_pipeline_weather_data_present() -> None:
    """The weather data from the tool should be accessible in the output."""
    result = ask_umbrella("London", "today")
    assert result["precipitation_probability"] is not None
    assert result["condition"] is not None
    assert result["temperature_c"] is not None


def test_pipeline_unknown_location() -> None:
    result = ask_umbrella("Atlantis", "today")
    assert result["recommendation"] == "unknown"


def test_pipeline_all_fixtures() -> None:
    for location in FIXTURES:
        result = ask_umbrella(location, "today")
        assert result["recommendation"] in ("yes", "maybe", "no", "unknown")
        assert isinstance(result["answer"], str) and len(result["answer"]) > 0
