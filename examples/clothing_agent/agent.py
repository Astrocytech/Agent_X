from __future__ import annotations

from typing import Any

from clothing_agent.fixtures import FIXTURES


COLD_ITEMS = ["heavy coat", "scarf", "gloves", "warm hat", "thermals"]
HOT_ITEMS = ["t-shirt", "shorts", "sunscreen", "sunglasses", "sun hat"]
RAIN_ITEMS = ["raincoat", "waterproof boots", "umbrella"]
WIND_ITEMS = ["windbreaker", "closed-toe shoes"]
FORMAL_ITEMS = ["suit", "dress shirt", "dress shoes", "tie"]
CASUAL_ITEMS = ["jeans", "t-shirt", "sneakers"]
UNKNOWN_ITEMS = ["check weather before dressing"]


class ClothingAgent:
    def recommend(self, location: str) -> dict[str, Any]:
        if not location or not isinstance(location, str):
            return {
                "recommendation": "unknown",
                "items": [],
                "reason": "No location provided",
                "source": "fixture",
                "confidence": "unknown",
            }

        loc = location.strip().lower()
        data = FIXTURES.get(loc)

        if data is None:
            return {
                "recommendation": "unknown",
                "items": [],
                "reason": f"Unknown location: {location}",
                "source": "fixture",
                "confidence": "unknown",
            }

        temp = data.get("temperature_c")
        condition = data.get("condition", "")
        event_type = data.get("event_type")
        wind = data.get("wind_speed_kph")

        if temp is None and condition is None:
            return {
                "recommendation": "unknown",
                "items": UNKNOWN_ITEMS,
                "reason": "Weather data unavailable for this location",
                "source": "fixture",
                "confidence": "low",
            }

        if not isinstance(temp, (int, float)):
            return {
                "recommendation": "unknown",
                "items": UNKNOWN_ITEMS,
                "reason": f"Malformed temperature data: {temp}",
                "source": "fixture",
                "confidence": "low",
            }

        if event_type == "formal":
            return {
                "recommendation": "formal_wear",
                "items": FORMAL_ITEMS,
                "reason": f"Formal event scheduled with {condition} weather at {temp}°C",
                "source": "fixture",
                "confidence": "high",
            }

        if isinstance(wind, (int, float)) and wind >= 35:
            return {
                "recommendation": "wind_protection",
                "items": WIND_ITEMS,
                "reason": f"Windy conditions detected at {wind} kph",
                "source": "fixture",
                "confidence": "high",
            }

        if isinstance(condition, str) and "rain" in condition.lower():
            return {
                "recommendation": "rain_gear",
                "items": RAIN_ITEMS,
                "reason": f"Rain expected with {condition} conditions at {temp}°C",
                "source": "fixture",
                "confidence": "high",
            }

        if temp < 5:
            return {
                "recommendation": "warm_clothing",
                "items": COLD_ITEMS,
                "reason": f"Cold temperature of {temp}°C requires warm layers",
                "source": "fixture",
                "confidence": "high",
            }

        if temp > 30:
            return {
                "recommendation": "light_clothing",
                "items": HOT_ITEMS,
                "reason": f"Hot temperature of {temp}°C requires light clothing",
                "source": "fixture",
                "confidence": "high",
            }

        if event_type == "casual":
            return {
                "recommendation": "casual_wear",
                "items": CASUAL_ITEMS,
                "reason": f"Casual day with {condition} weather at {temp}°C",
                "source": "fixture",
                "confidence": "high",
            }

        return {
            "recommendation": "casual_wear",
            "items": CASUAL_ITEMS,
            "reason": f"Mild weather at {temp}°C — casual clothing suitable",
            "source": "fixture",
            "confidence": "medium",
        }
