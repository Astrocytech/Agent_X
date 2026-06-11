from __future__ import annotations

RAIN_LIKE = {"rain", "shower", "thunderstorm"}
ALERT_CONDITIONS = {"storm", "heavy rain", "freezing rain", "sleet", "hail"}


def recommend(weather: dict) -> dict:
    result = {
        "recommendation": "unknown",
        "answer": "",
        "reason": "",
        "weather_source": "",
        "confidence": 0.0,
    }

    if not isinstance(weather, dict):
        result["answer"] = "No weather data provided."
        result["reason"] = "Input was not a dictionary."
        return result

    condition = weather.get("condition")
    precip = weather.get("precipitation_probability")
    source = weather.get("source") or weather.get("provider") or "unknown"
    result["weather_source"] = source

    if weather.get("success") is False:
        result["answer"] = weather.get("error", "Weather provider returned an error.")
        result["reason"] = "Provider returned failure status."
        return result

    if condition is None:
        result["answer"] = "Weather data is incomplete — condition field missing."
        result["reason"] = "Missing condition in weather payload."
        return result

    if not isinstance(condition, str):
        result["answer"] = "Weather data is malformed — condition is not a string."
        result["reason"] = "Condition field had unexpected type."
        return result

    cond_lower = condition.strip().lower()

    if precip is None or not isinstance(precip, (int, float)):
        result["answer"] = f"Weather data is incomplete — probability missing for condition '{condition}'."
        result["reason"] = "Missing or invalid precipitation_probability."
        return result

    if cond_lower in ALERT_CONDITIONS:
        result["recommendation"] = "alert"
        result["answer"] = f"{condition.title()} conditions detected. Stay indoors and avoid travel."
        result["reason"] = f"High-severity weather condition: {condition}."
        result["confidence"] = 0.9
        return result

    if cond_lower == "drizzle":
        result["recommendation"] = "maybe"
        result["answer"] = "Light drizzle possible. A light jacket or small umbrella recommended."
        result["reason"] = f"Drizzle with {precip}% probability."
        result["confidence"] = 0.4
        return result

    if cond_lower in RAIN_LIKE:
        if precip >= 70:
            result["recommendation"] = "yes"
            result["answer"] = f"{condition.title()} very likely ({precip}%). Definitely bring an umbrella."
            result["reason"] = f"High-probability {condition}."
            result["confidence"] = 0.8
        elif precip >= 40:
            result["recommendation"] = "yes"
            result["answer"] = f"{condition.title()} probable ({precip}%). Bring an umbrella to be safe."
            result["reason"] = f"Moderate-probability {condition}."
            result["confidence"] = 0.6
        else:
            result["recommendation"] = "maybe"
            result["answer"] = f"{condition.title()} possible ({precip}%). Consider bringing an umbrella."
            result["reason"] = f"Low-probability {condition} but condition warrants caution."
            result["confidence"] = 0.4
        return result

    if cond_lower == "snow":
        if precip >= 30:
            result["recommendation"] = "yes"
            result["answer"] = f"Snow expected ({precip}%). Bring an umbrella and warm clothing."
            result["reason"] = f"Significant snow probability: {precip}%."
            result["confidence"] = 0.7
        elif precip >= 10:
            result["recommendation"] = "maybe"
            result["answer"] = f"Light snow possible ({precip}%). A hat or umbrella may help."
            result["reason"] = f"Low snow probability: {precip}%."
            result["confidence"] = 0.4
        else:
            result["recommendation"] = "no"
            result["answer"] = f"Snow unlikely ({precip}%). No umbrella needed."
            result["reason"] = f"Very low snow probability: {precip}%."
            result["confidence"] = 0.8
        return result

    if cond_lower in ("cloudy", "overcast", "fog", "mist"):
        if precip >= 50:
            result["recommendation"] = "maybe"
            result["answer"] = f"{condition.title()} with {precip}% chance of precipitation. Consider an umbrella."
            result["reason"] = f"Overcast with moderate precipitation risk."
            result["confidence"] = 0.4
        else:
            result["recommendation"] = "no"
            result["answer"] = f"{condition.title()} but precipitation unlikely ({precip}%). No umbrella needed."
            result["reason"] = f"Low precipitation risk under overcast skies."
            result["confidence"] = 0.7
        return result

    if cond_lower == "clear":
        if precip > 0:
            result["recommendation"] = "no"
            result["answer"] = f"Clear skies but slight precipitation chance ({precip}%). Umbrella probably not needed."
            result["reason"] = f"Clear skies with minimal precipitation risk."
            result["confidence"] = 0.8
        else:
            result["recommendation"] = "no"
            result["answer"] = "Clear skies, no precipitation expected. No umbrella needed."
            result["reason"] = "Clear weather with zero precipitation probability."
            result["confidence"] = 0.9
        return result

    if precip >= 60:
        result["recommendation"] = "yes"
        result["answer"] = f"High precipitation probability ({precip}%) despite '{condition}' conditions. Bring an umbrella."
        result["reason"] = f"Fallback: high precipitation probability ({precip}%) with condition '{condition}'."
        result["confidence"] = 0.5
        return result

    if precip >= 30:
        result["recommendation"] = "maybe"
        result["answer"] = f"Moderate precipitation probability ({precip}%) with '{condition}' conditions. Consider an umbrella."
        result["reason"] = f"Fallback: moderate precipitation probability ({precip}%) with unknown condition '{condition}'."
        result["confidence"] = 0.3
        return result

    result["recommendation"] = "no"
    result["answer"] = f"Low precipitation probability ({precip}%) with '{condition}' conditions. No umbrella needed."
    result["reason"] = f"Fallback: low precipitation probability ({precip}%) with condition '{condition}'."
    result["confidence"] = 0.6
    return result
