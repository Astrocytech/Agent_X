from __future__ import annotations


def recommend(weather: dict) -> dict:
    precip = weather.get("precipitation_probability")

    if precip is None or not isinstance(precip, (int, float)):
        return {"recommendation": "unknown", "confidence": 0.0}

    if precip >= 60:
        return {"recommendation": "yes", "confidence": 0.7}
    elif precip >= 30:
        return {"recommendation": "maybe", "confidence": 0.4}
    else:
        return {"recommendation": "no", "confidence": 0.8}
