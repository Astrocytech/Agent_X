from __future__ import annotations

from pathlib import Path
from umbrella_agent.recommendation_engine import recommend
from agentx_evolve.fixtures.weather_fixture_provider import WeatherFixtureProvider


class UmbrellaAgentRuntime:
    def __init__(self, provider: WeatherFixtureProvider | None = None) -> None:
        self._provider = provider or WeatherFixtureProvider()

    def answer(self, location: str, date: str = "today") -> dict:
        if not location or not isinstance(location, str):
            return {
                "recommendation": "unknown",
                "confidence": 0.0,
                "answer": "A location is required.",
                "condition": None,
                "precipitation_probability": None,
                "temperature_c": None,
                "location": location,
                "date": date,
                "weather_source": "",
                "reason": "No location provided.",
            }

        weather_result = self._provider.fetch(location, date)
        if not weather_result.get("success"):
            weather_data = weather_result
        else:
            weather_data = weather_result["data"]

        rec = recommend(weather_data)

        return {
            "recommendation": rec["recommendation"],
            "answer": rec["answer"],
            "reason": rec["reason"],
            "weather_source": rec["weather_source"],
            "confidence": rec["confidence"],
            "condition": weather_data.get("condition") if isinstance(weather_data, dict) else None,
            "precipitation_probability": weather_data.get("precipitation_probability") if isinstance(weather_data, dict) else None,
            "temperature_c": weather_data.get("temperature_c") if isinstance(weather_data, dict) else None,
            "location": location,
            "date": weather_data.get("date", date) if isinstance(weather_data, dict) else date,
        }
