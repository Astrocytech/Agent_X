from __future__ import annotations

import ast
import json

from core_kernel.public import KernelService, KernelTurnRequest
from kernel_composition.seed_runtime_factory import build_seed_kernel_runtime

from daily_planning_agent.planner import DailyPlanningPlannerPort


class DailyPlanningRuntime:
    """Agent_X-based daily planning agent with rule-driven prioritisation.

    The question flows through KernelService (all 8 phases):

    *Planning phase* (``DailyPlanningPlannerPort``):
      1. Calls ``planning.fixture.read`` to fetch deterministic fixture data
      2. Applies prioritisation rules (urgency > effort > deadline)
      3. Returns a ``seed.emit_answer`` decision with structured JSON output

    *Execution phase*:
      - The tool gateway emits the JSON output as the kernel's primary result
    """

    def __init__(self) -> None:
        runtime = build_seed_kernel_runtime(
            planner_port=DailyPlanningPlannerPort(),
        )
        self._service = KernelService(
            kernel_runtime=runtime,
            default_profile_id="daily-planning-agent",
        )

    def answer(self, scenario_id: str) -> dict:
        if not scenario_id or not isinstance(scenario_id, str):
            return {
                "top_priority": None,
                "ordered_tasks": [],
                "reason": "A scenario ID is required.",
                "blocked_tasks": [],
                "safe_failure": True,
            }

        question = f"Plan the daily tasks for scenario {scenario_id}."

        response = self._service.run_turn(
            KernelTurnRequest(
                user_input=question,
                session_id=f"planning-{scenario_id}",
                profile_id="daily-planning-agent",
            )
        )

        raw_answer = response.answer
        return self._parse_answer(raw_answer, scenario_id)

    @staticmethod
    def _parse_answer(raw: str, scenario_id: str) -> dict:
        data = _try_decode(raw)

        top_priority = data.get("top_priority") if isinstance(data, dict) else None
        ordered_tasks = data.get("ordered_tasks", []) if isinstance(data, dict) else []
        reason = data.get("reason", raw) if isinstance(data, dict) else raw
        blocked_tasks = data.get("blocked_tasks", []) if isinstance(data, dict) else []
        safe_failure = data.get("safe_failure", True) if isinstance(data, dict) else True

        return {
            "top_priority": top_priority,
            "ordered_tasks": ordered_tasks,
            "reason": reason,
            "blocked_tasks": blocked_tasks,
            "safe_failure": safe_failure,
            "scenario_id": scenario_id,
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
