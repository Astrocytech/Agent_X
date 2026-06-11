from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

__all__ = ["WeatherFixtureReadTool"]

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
}

API_BASE_URL = "https://api.weather.example.com/v1"


class WeatherFixtureReadTool:
    """Simulated weather API tool — returns deterministic fixture data
    as if fetched from a remote weather service.

    This is NOT a real API call. It mocks the network round-trip with
    a small delay and logs the simulated request for audit transparency.
    """

    FIXTURE_DATE_UTC = "2026-06-10"
    VAGUE_TERMS = {"today", "tomorrow", "now"}

    def __call__(self, location: str, date: str | None = None) -> dict:
        if not location or not isinstance(location, str):
            return {"success": False, "error": "location is required"}
        loc = location.strip().lower()
        if loc not in FIXTURES:
            return {"success": False, "error": f"unknown location: {location}"}

        raw_date = date
        if date is None or date.strip().lower() in self.VAGUE_TERMS:
            resolved_date = self.FIXTURE_DATE_UTC
            date_source = "fixture_default"
        else:
            resolved_date = date.strip()
            date_source = "explicit"

        simulated_url = f"{API_BASE_URL}/current?location={location}&date={resolved_date}"
        logger.info("[weather.fixture.read] Simulating HTTP GET %s", simulated_url)
        time.sleep(0.05)

        now = datetime.now(timezone.utc).isoformat()
        data = dict(FIXTURES[loc])
        data["location"] = location
        data["date"] = resolved_date
        data["date_source"] = date_source
        data["source"] = "fixture"
        data["queried_at"] = now
        data["api_endpoint"] = simulated_url
        data["api_status"] = 200
        return {"success": True, "data": data}
