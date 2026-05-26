from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PhaseResult:
    phase_name: str = ""
    success: bool = False
    skipped: bool = False
    skip_reason: str = ""
    failure_reason: str = ""
    events: list[dict] = field(default_factory=list)
    produced_fields: dict[str, Any] = field(default_factory=dict)


REQUIRED_PHASE_OUTPUT: dict[str, list[str]] = {
    "input_validated": ["ctx.input_ok"],
    "goal_normalized": ["ctx.goal"],
    "profile_loaded": ["ctx.profile"],
    "task_created": ["ctx.task"],
    "policy_computed": ["ctx.policy_id"],
    "capability_resolved": ["ctx.capability_id"],
    "recall_completed": ["ctx.recalled_memory_refs"],
    "planning_completed": ["ctx.planner_decision"],
    "governance_checked": ["ctx.governance_decision"],
    "tool_executed_or_blocked": ["ctx.tool_output"],
    "trace_write_completed": ["ctx.trace_id"],
    "evaluation_completed": ["ctx.evaluation_score"],
    "memory_written_or_skipped_with_reason": ["ctx.written_memory_refs"],
    "checkpoint_write_completed": ["ctx.checkpoint_id"],
    "lesson_extracted": [],
    "output_returned": [],
}
