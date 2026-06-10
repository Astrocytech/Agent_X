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
from tool_gateway.seed_tools.planning_fixture_read import (
    FIXTURES,
    PlanningFixtureReadTool,
)

from umbrella_agent.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = """\
You are a daily planning agent. Your job is to look at a list of tasks and prioritise them.

Apply these deterministic rules:

1. Prioritisation order: urgency (high > medium > low), then effort (low > medium > high), then deadline (earlier first)
2. Completed tasks should appear at the end of the ordered list in their original relative order
3. Tasks whose dependencies are not yet met should be listed in blocked_tasks
4. If the task list is empty, set safe_failure to true with reason "Task list is empty."
5. If duplicate task IDs are found, set safe_failure to true
6. If a task has a malformed entry (missing title, invalid urgency/effort), set safe_failure to true
7. If circular dependencies are detected, set safe_failure to true and list affected task IDs in blocked_tasks
8. If a task depends on a non-existent task, set safe_failure to true

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{"top_priority": "<task_id or null>", "ordered_tasks": ["<task_id>", ...], "reason": "<explanation>", "blocked_tasks": ["<task_id>", ...], "safe_failure": false}
"""


def _extract_scenario(text: str) -> str | None:
    lower = text.lower().strip()
    for sid in FIXTURES:
        if sid in lower:
            return sid
    m = re.search(r"scenario\s+(\w+)", lower)
    if m:
        candidate = m.group(1).strip()
        if candidate in FIXTURES:
            return candidate
    return None


class DailyPlanningPlannerPort:
    """Custom planner for the daily planning agent.

    For the ``daily-planning-agent`` profile the planner:
    1. Calls ``planning.fixture.read`` to get deterministic fixture data
    2. Calls the LLM provider with the task data and prioritisation rules
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
        self._planning_tool = PlanningFixtureReadTool()
        self._llm = llm_provider or LLMProvider()

    def _is_planning_profile(self, profile: Any) -> bool:
        pid = profile.id if not isinstance(profile, dict) else profile.get("id", "")
        return pid == "daily-planning-agent"

    def make_decision(
        self,
        goal: Goal,
        profile: Any,
        context: dict[str, Any],
        problem_model: Any = None,
        memory_refs: list[str] | None = None,
    ) -> PlannerDecision:
        if not self._is_planning_profile(profile):
            return self._local_planner.make_decision(
                goal, profile, context, problem_model, memory_refs
            )

        text = goal.text or ""
        scenario_id = _extract_scenario(text)
        fixture_result = self._planning_tool(scenario_id=scenario_id) if scenario_id else {}

        if fixture_result.get("success"):
            tasks = fixture_result["data"].get("tasks", [])
        else:
            tasks = []

        output = self._build_output(tasks)
        return PlannerDecision(
            task_id=context.get("run_id", uuid4().hex[:12]),
            action_type="execute",
            tool_name=SEED_EMIT_ANSWER,
            arguments={"answer": json.dumps(output)},
            reasoning="daily_planning_agent:llm_prioritisation",
        )

    def _build_output(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        response = self._llm.complete(
            system_prompt=LLM_SYSTEM_PROMPT,
            user_text=(
                f"Task list for daily planning:\n{json.dumps(tasks, indent=2)}\n\n"
                "Prioritise these tasks."
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
            "LLM prioritisation: top_priority=%s safe_failure=%s",
            parsed.get("top_priority"),
            parsed.get("safe_failure"),
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
            return data
        except (json.JSONDecodeError, TypeError):
            return None
