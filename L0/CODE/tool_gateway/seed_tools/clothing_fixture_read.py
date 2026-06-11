from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

__all__ = ["ClothingFixtureReadTool"]

logger = logging.getLogger(__name__)

FIXTURES: dict[str, dict] = {
    "below_0_deg": {
        "location": "below_0_deg",
        "temperature_c": -5,
        "precipitation_probability": 10,
        "condition": "snow",
        "wind_speed_kph": 15,
        "severe_weather_flag": False,
    },
    "chilly_5": {
        "location": "chilly_5",
        "temperature_c": 5,
        "precipitation_probability": 20,
        "condition": "cloudy",
        "wind_speed_kph": 10,
        "severe_weather_flag": False,
    },
    "cool_12": {
        "location": "cool_12",
        "temperature_c": 12,
        "precipitation_probability": 30,
        "condition": "overcast",
        "wind_speed_kph": 12,
        "severe_weather_flag": False,
    },
    "mild_20": {
        "location": "mild_20",
        "temperature_c": 20,
        "precipitation_probability": 15,
        "condition": "clear",
        "wind_speed_kph": 8,
        "severe_weather_flag": False,
    },
    "hot_32": {
        "location": "hot_32",
        "temperature_c": 32,
        "precipitation_probability": 5,
        "condition": "clear",
        "wind_speed_kph": 5,
        "severe_weather_flag": False,
    },
    "rainy_day": {
        "location": "rainy_day",
        "temperature_c": 18,
        "precipitation_probability": 80,
        "condition": "rain",
        "wind_speed_kph": 20,
        "severe_weather_flag": False,
    },
    "snowy_day": {
        "location": "snowy_day",
        "temperature_c": -2,
        "precipitation_probability": 90,
        "condition": "snow",
        "wind_speed_kph": 10,
        "severe_weather_flag": False,
    },
    "windy_day": {
        "location": "windy_day",
        "temperature_c": 15,
        "precipitation_probability": 10,
        "condition": "windy",
        "wind_speed_kph": 50,
        "severe_weather_flag": False,
    },
    "severe_storm": {
        "location": "severe_storm",
        "temperature_c": 25,
        "precipitation_probability": 95,
        "condition": "severe thunderstorm",
        "wind_speed_kph": 80,
        "severe_weather_flag": True,
    },
    "missing_data": {
        "location": "missing_data",
        "temperature_c": None,
        "precipitation_probability": None,
        "condition": None,
        "wind_speed_kph": None,
        "severe_weather_flag": None,
    },
    "contradictory_data": {
        "location": "contradictory_data",
        "temperature_c": 30,
        "precipitation_probability": 0,
        "condition": "rain",
        "wind_speed_kph": 5,
        "severe_weather_flag": False,
    },
    "unknown_city": {
        "location": "unknown_city",
        "temperature_c": None,
        "precipitation_probability": None,
        "condition": None,
        "wind_speed_kph": None,
        "severe_weather_flag": None,
    },
    "null_location": {
        "location": "null_location",
        "temperature_c": None,
        "precipitation_probability": None,
        "condition": None,
        "wind_speed_kph": None,
        "severe_weather_flag": None,
    },
    "malformed_temp": {
        "location": "malformed_temp",
        "temperature_c": "not-a-number",
        "precipitation_probability": 20,
        "condition": "clear",
        "wind_speed_kph": 5,
        "severe_weather_flag": False,
    },
    "bad_precip": {
        "location": "bad_precip",
        "temperature_c": 22,
        "precipitation_probability": "invalid",
        "condition": "clear",
        "wind_speed_kph": 5,
        "severe_weather_flag": False,
    },
    "out_of_range_precip": {
        "location": "out_of_range_precip",
        "temperature_c": 28,
        "precipitation_probability": 150,
        "condition": "clear",
        "wind_speed_kph": 5,
        "severe_weather_flag": False,
    },
    "fog_condition": {
        "location": "fog_condition",
        "temperature_c": 10,
        "precipitation_probability": 40,
        "condition": "fog",
        "wind_speed_kph": 5,
        "severe_weather_flag": False,
    },
}

API_BASE_URL = "https://api.clothing.example.com"


class ClothingFixtureReadTool:
    """Simulated clothing advice API tool — returns deterministic fixture data
    as if fetched from a remote clothing/weather service.
    """

    def __call__(self, location: str) -> dict:
        if not location or not isinstance(location, str):
            return {"success": False, "error": "location is required"}
        loc = location.strip().lower()
        if loc not in FIXTURES:
            return {"success": False, "error": f"unknown location: {location}"}

        simulated_url = f"{API_BASE_URL}/current?location={location}"
        logger.info("Simulating HTTP GET %s", simulated_url)
        time.sleep(0.05)

        now = datetime.now(timezone.utc).isoformat()
        data = dict(FIXTURES[loc])
        data["location"] = location
        data["source"] = "fixture"
        data["queried_at"] = now
        data["api_endpoint"] = simulated_url
        data["api_status"] = 200
        return {"success": True, "data": data}
