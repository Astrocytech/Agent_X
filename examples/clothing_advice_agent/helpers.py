"""Constants and helper utilities for clothing advice decisions."""

def get_recommendation_label(temp_c: float) -> str:
    """Return a recommendation label based on temperature in Celsius."""
    if temp_c < 0:
        return "heavy_winter"
    elif temp_c <= 9:
        return "winter"
    elif temp_c <= 18:
        return "cool"
    elif temp_c <= 27:
        return "mild"
    else:
        return "hot"


def is_valid_temperature(temp: float) -> bool:
    """Check if a temperature value is valid (between -10°C and 50°C inclusive)."""
    return -10.0 <= temp <= 50.0

def clamp_temperature(temp: float, min_val: float, max_val: float) -> float:
    """Clamp a temperature value between min_val and max_val."""
    return max(min_val, min(max_val, temp))

RECOMMENDATION_LABELS = {
    "warm": "Wear warm clothes",
    "cool": "Wear a jacket",
    "moderate": "Light layers work",
    "light": "T-shirt weather",
    "hot": "Stay cool",
    "rain_gear": "Bring rain gear",
    "snow_gear": "Snow gear needed",
    "wind_block": "Wind protection needed",
    "shelter": "Stay indoors",
    "unknown": "Check weather",
}

CONDITION_DESCRIPTIONS = {
    "clear": "Clear skies",
    "cloudy": "Cloudy",
    "overcast": "Overcast",
    "rain": "Rainy",
    "snow": "Snowy",
    "fog": "Foggy",
    "windy": "Windy",
    "severe thunderstorm": "Severe thunderstorm",
}
