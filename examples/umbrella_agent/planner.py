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
from agentx_evolve.providers.weather_fixture import FIXTURES, WeatherFixtureProvider
from umbrella_agent.recommendation_engine import recommend

logger = logging.getLogger(__name__)


def _extract_location(text: str) -> str | None:
    lower = text.lower().strip()
    for loc in FIXTURES:
        if loc in lower:
            return loc
    m = re.search(r"\bin\s+(\w+(?:\s+\w+)*?)(?:\s+on\s+|\s+for\s+|\s*\?|$)", lower)
    if m:
        candidate = m.group(1).strip()
        if candidate in FIXTURES:
            return candidate
    return None


class UmbrellaPlannerPort:
    """Custom planner for the umbrella agent.

    For the ``umbrella-agent`` profile the planner:
    1. Calls the weather fixture provider to get deterministic fixture data
    2. Applies deterministic recommendation rules
    3. Returns a ``seed.emit_answer`` decision with structured JSON output

    For all other profiles it delegates to ``LocalPlannerPort``.
    """

    runtime_safety_class = "production_seed_port"

    def __init__(
        self,
        policy_port: Any = None,
    ) -> None:
        self._local_planner = LocalPlannerPort(policy_port=policy_port)
        self._weather_tool = WeatherFixtureProvider()

    def _is_umbrella_profile(self, profile: Any) -> bool:
        pid = profile.id if not isinstance(profile, dict) else profile.get("id", "")
        return pid == "umbrella-agent"

    def make_decision(
        self,
        goal: Goal,
        profile: Any,
        context: dict[str, Any],
        problem_model: Any = None,
        memory_refs: list[str] | None = None,
    ) -> PlannerDecision:
        if not self._is_umbrella_profile(profile):
            return self._local_planner.make_decision(
                goal, profile, context, problem_model, memory_refs
            )

        text = goal.text or ""
        location = _extract_location(text)
        weather_result = self._weather_tool.fetch(location=location, date="today") if location else {}

        if weather_result.get("success"):
            weather_data = weather_result["data"]
        else:
            weather_data = None

        output = self._build_output(weather_data)
        return PlannerDecision(
            task_id=context.get("run_id", uuid4().hex[:12]),
            action_type="execute",
            tool_name=SEED_EMIT_ANSWER,
            arguments={"answer": json.dumps(output)},
            reasoning="umbrella_agent:deterministic_recommendation",
        )

    def _build_output(self, weather_data: dict[str, Any] | None) -> dict[str, Any]:
        if weather_data is None:
            return {
                "recommendation": "unknown",
                "confidence": 0.0,
                "precipitation_probability": None,
                "condition": None,
                "temperature_c": None,
                "explanation": "Unknown location — weather data unavailable",
            }

        rec = recommend(weather_data)
        return {
            "recommendation": rec["recommendation"],
            "answer": rec.get("answer", ""),
            "reason": rec.get("reason", ""),
            "weather_source": rec.get("weather_source", ""),
            "confidence": rec["confidence"],
            "precipitation_probability": weather_data.get("precipitation_probability"),
            "condition": weather_data.get("condition"),
            "temperature_c": weather_data.get("temperature_c"),
            "explanation": rec.get("answer", ""),
        }
