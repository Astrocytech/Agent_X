"""Planner decision — frozen dataclass for planner tool dispatch decisions.

Consumed by UniversalExecutor. A degraded=True decision indicates
the planner used a symbolic/fallback path instead of a real tool.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core_kernel.memory.memory_recall_result import MemoryRecallResult


@dataclass
class PlannerContext:
    run_id: str = ""
    profile_id: str = ""
    past_lessons: list[dict[str, Any]] = field(default_factory=list)
    memory_recall: MemoryRecallResult = field(default_factory=MemoryRecallResult)
    goal_text: str = ""
    policy_id: str = ""
    task_type: str = ""
    trace_id: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlannerDecision:
    """Frozen dataclass representing a planner's decision about what to do next.

    Consumed by UniversalExecutor for tool dispatch. A degraded=True decision
    indicates the planner used a symbolic/fallback path instead of a real tool.
    """

    task_id: str = ""
    action_type: str = ""
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    risk_level: str = "none"
    requires_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    degraded: bool = False

    def __post_init__(self) -> None:
        if not self.tool_name:
            raise ValueError("PlannerDecision requires non-empty tool_name")
