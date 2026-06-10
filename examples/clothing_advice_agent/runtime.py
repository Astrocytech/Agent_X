from __future__ import annotations

import ast
import json

from core_kernel.public import KernelService, KernelTurnRequest
from kernel_composition.seed_runtime_factory import build_seed_kernel_runtime

from clothing_advice_agent.planner import ClothingPlannerPort


class ClothingAdviceRuntime:
    """Agent_X-based clothing advice agent with rule-driven planning.

    The question flows through KernelService (all 8 phases):

    *Planning phase* (``ClothingPlannerPort``):
      1. Calls ``clothing.fixture.read`` to fetch deterministic fixture data
      2. Applies temperature/condition rules to determine recommendation
      3. Optionally calls the LLM provider for an explanation
      4. Returns a ``seed.emit_answer`` decision with structured JSON output

    *Execution phase*:
      - The tool gateway emits the JSON output as the kernel's primary result
    """

    def __init__(self) -> None:
        runtime = build_seed_kernel_runtime(
            planner_port=ClothingPlannerPort(),
        )
        self._service = KernelService(
            kernel_runtime=runtime,
            default_profile_id="clothing-advice-agent",
        )

    def answer(self, location: str) -> dict:
        if not location or not isinstance(location, str):
            return {
                "recommendation": "unknown",
                "reason": "A location is required.",
                "confidence": "low",
                "data_source": "unavailable",
                "safe_failure": True,
            }

        question = f"What clothing should I wear in {location}?"

        response = self._service.run_turn(
            KernelTurnRequest(
                user_input=question,
                session_id=f"clothing-{location}",
                profile_id="clothing-advice-agent",
            )
        )

        raw_answer = response.answer
        return self._parse_answer(raw_answer, location)

    @staticmethod
    def _parse_answer(raw: str, location: str) -> dict:
        data = _try_decode(raw)

        rec = data.get("recommendation", "unknown") if isinstance(data, dict) else "unknown"
        reason = data.get("reason", raw) if isinstance(data, dict) else raw
        confidence = data.get("confidence", "low") if isinstance(data, dict) else "low"
        data_source = data.get("data_source", "unavailable") if isinstance(data, dict) else "unavailable"
        safe_failure = data.get("safe_failure", True) if isinstance(data, dict) else True

        return {
            "recommendation": rec,
            "reason": reason,
            "confidence": confidence,
            "data_source": data_source,
            "safe_failure": safe_failure,
            "location": location,
        }


def _try_decode(raw: str) -> dict:
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
