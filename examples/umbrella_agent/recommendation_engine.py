from __future__ import annotations


def recommend(weather: dict) -> dict:
    if not isinstance(weather, dict):
        return {"recommendation": "unknown", "confidence": 0.0}

    precip = weather.get("precipitation_probability")
    condition = weather.get("condition", "")

    if precip is None or not isinstance(precip, (int, float)):
        return {"recommendation": "unknown", "confidence": 0.0}

    # Snow at low probability still warrants umbrella
    if condition == "snow" and precip >= 20:
        return {"recommendation": "yes", "confidence": 0.6}

    # Drizzle at moderate probability
    if condition == "drizzle" and 10 <= precip < 40:
        return {"recommendation": "maybe", "confidence": 0.4}

    if precip >= 60:
        return {"recommendation": "yes", "confidence": 0.7}
    elif precip >= 30:
        return {"recommendation": "maybe", "confidence": 0.4}
    else:
        return {"recommendation": "no", "confidence": 0.8}
