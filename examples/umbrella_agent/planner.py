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
from tool_gateway.seed_tools.weather_fixture_read import (
    FIXTURES,
    WeatherFixtureReadTool,
)

from umbrella_agent.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = """\
You are an umbrella recommendation agent. Your job is to look at weather data and decide if someone should bring an umbrella.

Apply these deterministic rules based on precipitation probability:
- If precipitation probability >= 60% -> recommend "yes"
- If 30% <= precipitation probability < 60% -> recommend "maybe"
- If precipitation probability < 30% -> recommend "no"

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{"recommendation": "yes|maybe|no", "confidence": 0.0-1.0, "precipitation_probability": <int or null>, "condition": "<str or null>", "temperature_c": <int or null>, "explanation": "<str>"}
"""


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
    1. Calls ``weather.fixture.read`` to get deterministic fixture data
    2. Calls the LLM provider (auto-starts opencode server if needed)
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
        self._weather_tool = WeatherFixtureReadTool()
        self._llm = llm_provider or LLMProvider()

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
        weather_result = self._weather_tool(location=location, date="today") if location else {}

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
            reasoning="umbrella_agent:llm_interpretation",
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

        response = self._llm.complete(
            system_prompt=LLM_SYSTEM_PROMPT,
            user_text=(
                f"Weather data for {weather_data.get('location', 'unknown')}:\n"
                f"- Precipitation probability: {weather_data.get('precipitation_probability')}%\n"
                f"- Condition: {weather_data.get('condition')}\n"
                f"- Temperature: {weather_data.get('temperature_c')}°C\n\n"
                "Should I bring an umbrella?"
            ),
            temperature=0.0,
        )

        content = response.get("content", "")
        parsed = self._parse_llm_json(content)
        if parsed is None:
            raise RuntimeError(
                f"LLM returned unparseable response: {content[:500]}"
            )
        logger.info(
            "LLM interpretation: recommendation=%s confidence=%s",
            parsed.get("recommendation"),
            parsed.get("confidence"),
        )
        return parsed

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
            rec = data.get("recommendation", "unknown")
            if rec not in ("yes", "maybe", "no", "unknown"):
                return None
            return data
        except (json.JSONDecodeError, TypeError):
            return None
