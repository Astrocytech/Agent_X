from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

__all__ = ["WeatherFixtureProvider", "FIXTURES", "FIXTURE_DATE_UTC", "ALERT_CONDITIONS", "HIGH_PROB_CONDITIONS"]

logger = logging.getLogger(__name__)

FIXTURES: dict[str, dict] = {
    "london": {"precipitation_probability": 60, "condition": "rain", "temperature_c": 15},
    "tokyo": {"precipitation_probability": 80, "condition": "rain", "temperature_c": 22},
    "paris": {"precipitation_probability": 10, "condition": "clear", "temperature_c": 28},
    "berlin": {"precipitation_probability": 45, "condition": "cloudy", "temperature_c": 18},
    "sydney": {"precipitation_probability": 5, "condition": "clear", "temperature_c": 30},
    "mumbai": {"precipitation_probability": 70, "condition": "rain", "temperature_c": 32},
    "cairo": {"precipitation_probability": 0, "condition": "clear", "temperature_c": 35},
    "oslo": {"precipitation_probability": 55, "condition": "cloudy", "temperature_c": 10},
    "dubai": {"precipitation_probability": 0, "condition": "clear", "temperature_c": 40},
    "moscow": {"precipitation_probability": 35, "condition": "cloudy", "temperature_c": 5},
    "vancouver": {"precipitation_probability": 35, "condition": "drizzle", "temperature_c": 12},
    "reykjavik": {"precipitation_probability": 65, "condition": "snow", "temperature_c": -2},
    "anchorage": {"precipitation_probability": 25, "condition": "snow", "temperature_c": -5},
    "new york": {"precipitation_probability": 50, "condition": "thunderstorm", "temperature_c": 25},
    "miami": {"precipitation_probability": 75, "condition": "heavy rain", "temperature_c": 28},
    "seattle": {"precipitation_probability": 40, "condition": "shower", "temperature_c": 14},
    "chicago": {"precipitation_probability": 30, "condition": "sleet", "temperature_c": 1},
    "denver": {"precipitation_probability": 20, "condition": "freezing rain", "temperature_c": -3},
    "houston": {"precipitation_probability": 85, "condition": "storm", "temperature_c": 26},
    "phoenix": {"precipitation_probability": 0, "condition": "clear", "temperature_c": 42},
}

ALERT_CONDITIONS = {"storm", "heavy rain", "freezing rain", "sleet", "hail"}
HIGH_PROB_CONDITIONS = {"rain", "shower", "thunderstorm"}
FIXTURE_DATE_UTC = "2026-06-10"
VAGUE_TERMS = {"today", "tomorrow", "now"}


class WeatherFixtureProvider:
    """Deterministic weather fixture provider.

    Returns fixture data as if fetched from a remote weather service.
    This is NOT a real API call.
    """

    def __init__(self, simulate_delay: bool = True):
        self._simulate_delay = simulate_delay

    def fetch(self, location: str, date: str | None = None) -> dict:
        if not location or not isinstance(location, str):
            return {"success": False, "error": "location is required"}
        loc = location.strip().lower()
        if loc not in FIXTURES:
            return {"success": False, "error": f"unknown location: {location}"}

        if date is None or date.strip().lower() in VAGUE_TERMS:
            resolved_date = FIXTURE_DATE_UTC
            date_source = "fixture_default"
        else:
            resolved_date = date.strip()
            date_source = "explicit"

        if self._simulate_delay:
            time.sleep(0.05)

        now = datetime.now(timezone.utc).isoformat()
        data = dict(FIXTURES[loc])
        data["location"] = location
        data["date"] = resolved_date
        data["date_source"] = date_source
        data["source"] = "fixture"
        data["provider"] = "weather_fixture_provider"
        data["queried_at"] = now
        return {"success": True, "data": data}
