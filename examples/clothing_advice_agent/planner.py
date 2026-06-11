from __future__ import annotations

import json
import logging
import re
from typing import Any
from uuid import uuid4

from core_kernel.models.kernel_atoms import Goal
from core_kernel.models.planner_decision import PlannerDecision
from kernel_composition.local_seed_ports.local_planner_port import (
    LocalPlannerPort,
    SEED_EMIT_ANSWER,
)
from tool_gateway.seed_tools.clothing_fixture_read import (
    FIXTURES,
    ClothingFixtureReadTool,
)

from umbrella_agent.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = """\
You are a clothing recommendation agent. Your job is to look at weather data and suggest appropriate clothing.

Apply these deterministic rules:

1. Temperature bands:
   - Below 0°C -> "warm"
   - 0°C to 9°C -> "cool"
   - 10°C to 18°C -> "moderate"
   - 19°C to 27°C -> "light"
   - 28°C and above -> "hot"

2. Condition overrides (take priority over temperature bands):
   - If `severe_weather_flag` is true -> "shelter"
   - If condition contains "snow" -> "snow_gear"
   - If condition contains "rain" -> "rain_gear"
   - If wind_speed_kph >= 40 -> "wind_block"

3. If temperature data is missing, malformed, or invalid -> set safe_failure to true

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{"recommendation": "warm|cool|moderate|light|hot|rain_gear|snow_gear|wind_block|shelter|unknown", "reason": "<natural language explanation>", "confidence": "high|medium|low", "data_source": "fixture|unavailable", "safe_failure": false}
"""


def _extract_location(text: str) -> str | None:
    lower = text.lower().strip()
    for loc in FIXTURES:
        if loc in lower:
            return loc
    m = re.search(r"\bin\s+(\w+(?:\s+\w+)*?)(?:\s*\?|$)", lower)
    if m:
        candidate = m.group(1).strip()
        if candidate in FIXTURES:
            return candidate
    return None


class ClothingPlannerPort:
    """Custom planner for the clothing advice agent.

    For the ``clothing-advice-agent`` profile the planner:
    1. Calls ``clothing.fixture.read`` to get deterministic fixture data
    2. Calls the LLM provider with the weather data and clothing rules
    3. Returns a ``seed.emit_answer`` decision with structured JSON output

    For all other profiles it delegates to ``LocalPlannerPort``.
    """

    runtime_safety_class = "production_seed_port"

    def __init__(
        self,
        policy_port: Any = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self._local_planner = LocalPlannerPort(policy_port=policy_port)
        self._clothing_tool = ClothingFixtureReadTool()
        self._llm = llm_provider or LLMProvider()

    def _is_clothing_profile(self, profile: Any) -> bool:
        pid = profile.id if not isinstance(profile, dict) else profile.get("id", "")
        return pid == "clothing-advice-agent"

    def make_decision(
        self,
        goal: Goal,
        profile: Any,
        context: dict[str, Any],
        problem_model: Any = None,
        memory_refs: list[str] | None = None,
    ) -> PlannerDecision:
        if not self._is_clothing_profile(profile):
            return self._local_planner.make_decision(
                goal, profile, context, problem_model, memory_refs
            )

        text = goal.text or ""
        location = _extract_location(text)
        clothing_result = self._clothing_tool(location=location) if location else {}

        if clothing_result.get("success"):
            weather_data = clothing_result["data"]
        else:
            weather_data = None

        output = self._build_output(weather_data)
        return PlannerDecision(
            task_id=context.get("run_id", uuid4().hex[:12]),
            action_type="execute",
            tool_name=SEED_EMIT_ANSWER,
            arguments={"answer": json.dumps(output)},
            reasoning="clothing_advice_agent:llm_interpretation",
        )

    def _build_output(self, weather_data: dict[str, Any] | None) -> dict[str, Any]:
        if weather_data is None:
            return {
                "recommendation": "unknown",
                "reason": "Weather data unavailable",
                "confidence": "low",
                "data_source": "unavailable",
                "safe_failure": True,
            }

        if self._llm_available():
            try:
                response = self._llm.complete(
                    system_prompt=LLM_SYSTEM_PROMPT,
                    user_text=(
                        f"Weather data for {weather_data.get('location', 'unknown')}:\n"
                        f"- Temperature: {weather_data.get('temperature_c')}\n"
                        f"- Condition: {weather_data.get('condition')}\n"
                        f"- Precipitation probability: {weather_data.get('precipitation_probability')}%\n"
                        f"- Wind speed: {weather_data.get('wind_speed_kph')} kph\n"
                        f"- Severe weather: {weather_data.get('severe_weather_flag')}\n\n"
                        "What clothing should I wear?"
                    ),
                    temperature=0.0,
                )
                content = response.get("content", "")
                parsed = self._parse_llm_json(content)
                if parsed is not None:
                    logger.info(
                        "LLM interpretation: recommendation=%s confidence=%s",
                        parsed.get("recommendation"),
                        parsed.get("confidence"),
                    )
                    return parsed
            except Exception:
                logger.info("LLM unavailable, using deterministic fallback")
        else:
            logger.info("LLM not reachable (health check failed), using deterministic fallback")

        return self._deterministic_build_output(weather_data)

    @staticmethod
    def _llm_available() -> bool:
        try:
            return LLMProvider()._health_check()
        except Exception:
            return False

    @staticmethod
    def _deterministic_build_output(weather_data: dict) -> dict[str, Any]:
        temp = weather_data.get("temperature_c")
        condition = (weather_data.get("condition") or "").lower()
        wind = weather_data.get("wind_speed_kph", 0)
        severe = weather_data.get("severe_weather_flag", False)
        location = weather_data.get("location", "unknown")

        if severe:
            return {"recommendation": "shelter",
                    "reason": f"Severe weather in {location}, stay indoors",
                    "confidence": "high", "data_source": "fixture",
                    "safe_failure": False, "location": location}
        if "snow" in condition:
            return {"recommendation": "snow_gear",
                    "reason": f"Snow expected in {location}, snow gear needed",
                    "confidence": "high", "data_source": "fixture",
                    "safe_failure": False, "location": location}
        if "rain" in condition:
            return {"recommendation": "rain_gear",
                    "reason": f"Rain expected in {location}, bring rain gear",
                    "confidence": "high", "data_source": "fixture",
                    "safe_failure": False, "location": location}
        if wind >= 40:
            return {"recommendation": "wind_block",
                    "reason": f"High wind ({wind} kph) in {location}, wind protection needed",
                    "confidence": "high", "data_source": "fixture",
                    "safe_failure": False, "location": location}

        if temp is None or not isinstance(temp, (int, float)):
            return {"recommendation": "unknown",
                    "reason": f"Temperature data missing for {location}",
                    "confidence": "low", "data_source": "unavailable",
                    "safe_failure": True, "location": location}

        if temp < 0:
            rec, reason = "warm", f"Below freezing ({temp}°C) in {location}"
        elif temp <= 9:
            rec, reason = "cool", f"Cold ({temp}°C) in {location}"
        elif temp <= 18:
            rec, reason = "moderate", f"Mild ({temp}°C) in {location}"
        elif temp <= 27:
            rec, reason = "light", f"Warm ({temp}°C) in {location}"
        else:
            rec, reason = "hot", f"Hot ({temp}°C) in {location}"

        return {"recommendation": rec, "reason": reason,
                "confidence": "high", "data_source": "fixture",
                "safe_failure": False, "location": location}

    @staticmethod
    def _parse_llm_json(content: str) -> dict[str, Any] | None:
        content = content.strip()
        idx = content.find("{")
        if idx != -1:
            content = content[idx:]
        end = content.rfind("}")
        if end != -1:
            content = content[: end + 1]
        if content.startswith("```"):
            content = content[content.find("\n") + 1 : content.rfind("```")]
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                return None
            return data
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def get_recommendation_label(recommendation: str) -> str:
        labels = {
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
        return labels.get(recommendation, "No recommendation")
