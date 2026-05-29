"""L0 local planner.

The L0 seed planner has exactly one executable seed tool:
seed.emit_answer.

It may choose one of three L0 capabilities:
- answer_user
- ask_user
- stop

All three capabilities are expressed through seed.emit_answer because L0 has no
direct shell, network, filesystem, promotion, orchestration, or self-mutation
capability.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from core_kernel.models.kernel_atoms import Goal
from core_kernel.models.planner_decision import PlannerDecision


SEED_EMIT_ANSWER = "seed.emit_answer"

SEED_CAPABILITY_RULES: list[dict[str, Any]] = [
    {
        "capability_id": "answer_user",
        "keywords": [
            "answer",
            "respond",
            "reply",
            "what is",
            "who is",
            "tell me",
            "explain",
        ],
        "tool": SEED_EMIT_ANSWER,
        "success_criteria": "user received a direct text answer",
        "constraints": ["no side effects", "no file access"],
    },
    {
        "capability_id": "ask_user",
        "keywords": [
            "ask user",
            "clarify",
            "missing info",
            "need input",
            "what should i",
            "what do you want",
        ],
        "tool": SEED_EMIT_ANSWER,
        "success_criteria": "user received a clarification request",
        "constraints": ["no side effects", "no file access"],
    },
    {
        "capability_id": "stop",
        "keywords": [
            "stop",
            "done",
            "finished",
            "complete",
            "exit",
            "that is all",
            "no more",
            "enough",
        ],
        "tool": SEED_EMIT_ANSWER,
        "success_criteria": "seed turn stopped cleanly",
        "constraints": ["no side effects", "no file access"],
    },
]


def _detect_capability(text: str) -> dict[str, Any]:
    lower = text.lower()
    best: dict[str, Any] | None = None
    best_score = 0

    for cap in SEED_CAPABILITY_RULES:
        score = sum(1 for kw in cap["keywords"] if kw in lower)
        if score > best_score:
            best_score = score
            best = cap

    if best is not None:
        return best

    return {
        "capability_id": "answer_user",
        "keywords": [],
        "tool": SEED_EMIT_ANSWER,
        "success_criteria": "user received a direct text answer",
        "constraints": ["no side effects", "no file access"],
    }


class LocalPlannerPort:
    runtime_safety_class = "production_seed_port"

    def __init__(self, policy_port: Any = None) -> None:
        self._policy_port = policy_port

    def _is_tool_allowed_for_profile(self, tool_name: str, profile: Any) -> bool:
        if self._policy_port is not None:
            from core_kernel.models.kernel_atoms import Task

            task = Task(
                id="planner-check",
                goal="",
                profile_id=getattr(profile, "id", ""),
            )
            decision = self._policy_port.compute(profile, task)
            allowed = decision.metadata.get("allowed_tool_classes", [])
            forbidden = decision.metadata.get("forbidden_tool_classes", [])

            if allowed:
                return tool_name in allowed or tool_name.split(".")[-1] in allowed

            if forbidden:
                return not (
                    tool_name in forbidden or tool_name.split(".")[-1] in forbidden
                )

            return True

        allowed = (
            getattr(profile, "allowed_tools", None)
            if not isinstance(profile, dict)
            else profile.get("allowed_tools")
        )
        forbidden = (
            getattr(profile, "forbidden_tools", None)
            if not isinstance(profile, dict)
            else profile.get("forbidden_tools")
        )

        if allowed:
            return tool_name in allowed or tool_name.split(".")[-1] in allowed

        if forbidden:
            return not (tool_name in forbidden or tool_name.split(".")[-1] in forbidden)

        return True

    def make_decision(
        self,
        goal: Goal,
        profile: Any,
        context: dict,
        problem_model: Any = None,
        memory_refs: list[str] | None = None,
    ) -> PlannerDecision:
        text = goal.text or ""
        capability = _detect_capability(text)
        tool_name = capability["tool"]

        if not self._is_tool_allowed_for_profile(tool_name, profile):
            return PlannerDecision(
                task_id=context.get("run_id", uuid4().hex[:12]),
                action_type="execute",
                tool_name=SEED_EMIT_ANSWER,
                arguments={
                    "answer": (
                        "The requested action is not available under this seed profile."
                    )
                },
                reasoning=(
                    "capability:answer_user | "
                    "constraints:no_side_effects,no_file_access | "
                    "note:requested_tool_not_allowed_by_profile"
                ),
            )

        return PlannerDecision(
            task_id=context.get("run_id", uuid4().hex[:12]),
            action_type="execute",
            tool_name=tool_name,
            arguments=self._build_args(tool_name, text),
            reasoning=(
                f"capability:{capability['capability_id']} | "
                f"constraints:{','.join(capability['constraints'])}"
            ),
        )

    @staticmethod
    def _build_args(tool_name: str, text: str) -> dict:
        if tool_name == SEED_EMIT_ANSWER:
            return {"answer": text}
        return {}
