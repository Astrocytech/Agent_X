from __future__ import annotations

import ast
import json

from core_kernel.public import KernelService, KernelTurnRequest
from kernel_composition.seed_runtime_factory import build_seed_kernel_runtime

from umbrella_agent.planner import UmbrellaPlannerPort


class UmbrellaAgentRuntime:
    """Agent_X-based umbrella agent with LLM-driven planning.

    The question flows through KernelService (all 8 phases):

    *Planning phase* (``UmbrellaPlannerPort``):
      1. Calls ``weather.fixture.read`` to fetch deterministic fixture data
      2. Tries the LLM provider with weather data + §3 rules (temperature=0.0)
      3. Falls back to the rule-based recommendation engine when LLM unavailable
      4. Returns a ``seed.emit_answer`` decision with the structured JSON output

    *Execution phase*:
      - The tool gateway emits the JSON output as the kernel's primary result

    The LLM is the primary decision-maker; the rule engine is a graceful
    degradation path for when no LLM provider is reachable.
    """

    def __init__(self) -> None:
        runtime = build_seed_kernel_runtime(
            planner_port=UmbrellaPlannerPort(),
        )
        self._service = KernelService(
            kernel_runtime=runtime,
            default_profile_id="umbrella-agent",
        )

    def answer(self, location: str, date: str = "today") -> dict:
        if not location or not isinstance(location, str):
            return {
                "recommendation": "unknown",
                "confidence": 0.0,
                "answer": "A location is required.",
                "precipitation_probability": None,
                "condition": None,
                "temperature_c": None,
                "location": location,
                "date": date,
            }

        question = f"Should I bring an umbrella in {location} on {date}?"

        response = self._service.run_turn(
            KernelTurnRequest(
                user_input=question,
                session_id=f"umbrella-{location}-{date}",
                profile_id="umbrella-agent",
            )
        )

        raw_answer = response.answer
        return self._parse_answer(raw_answer, location, date)

    @staticmethod
    def _parse_answer(raw: str, location: str, date: str) -> dict:
        data = _try_decode(raw)

        rec = data.get("recommendation", "unknown") if isinstance(data, dict) else "unknown"
        confidence = data.get("confidence", 0.0) if isinstance(data, dict) else 0.0
        explanation = data.get("explanation", raw) if isinstance(data, dict) else raw
        precip = data.get("precipitation_probability") if isinstance(data, dict) else None
        condition = data.get("condition") if isinstance(data, dict) else None
        temp = data.get("temperature_c") if isinstance(data, dict) else None

        return {
            "recommendation": rec,
            "confidence": confidence,
            "precipitation_probability": precip,
            "condition": condition,
            "temperature_c": temp,
            "answer": explanation,
            "location": location,
            "date": date,
        }


def _try_decode(raw: str) -> dict:
    """Attempt to decode ``raw`` as a structured dict.

    Three strategies, in order:
    1. Direct JSON parse (backward compat)
    2. ``ast.literal_eval`` — handles Python repr of tool-result wrapper dicts
    3. If wrapper: extract ``answer`` field and JSON-parse that
    """
    if not raw:
        return {}

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        pass

    try:
        wrapper = ast.literal_eval(raw)
        if isinstance(wrapper, dict):
            answer_field = wrapper.get("answer")
            if isinstance(answer_field, str):
                try:
                    return json.loads(answer_field)
                except (json.JSONDecodeError, TypeError):
                    return {}
        return {}
    except (ValueError, SyntaxError, TypeError):
        return {}
