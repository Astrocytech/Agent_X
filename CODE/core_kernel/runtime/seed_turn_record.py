"""Run context dataclass for seed runtime turns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core_kernel.models.kernel_atoms import Goal, Task


@dataclass
class SeedFailureRecord:
    phase: str = ""
    component: str = ""
    error_type: str = ""
    message: str = ""
    recoverable: bool = False
    policy_effect: str = ""


@dataclass
class _RunContext:
    run_id: str = ""
    profile: Any = None
    goal: Goal | None = None
    task: Task | None = None
    policy_id: str = ""
    planner_decision: Any = None
    governance_decision: Any = None
    tool_output: str = ""
    memory_refs: list[str] = field(default_factory=list)
    recalled_memory_refs: list[str] = field(default_factory=list)
    recalled_memory_items: list[dict] = field(default_factory=list)
    written_memory_refs: list[str] = field(default_factory=list)
    memory_skipped_reason: str = ""
    memory_recall_skipped_reason: str = ""
    evaluation_score: float | None = None
    evaluation_status: str = "not_run"
    verdict_id: str = ""
    evaluation_skipped_reason: str = ""
    evaluation_error_type: str = ""
    evaluation_error_message: str = ""
    evaluation_criteria: list[dict] = field(default_factory=list)
    trace_id: str = ""
    checkpoint_id: str = ""
    checkpoint_failure_id: str = ""
    events: list[dict] = field(default_factory=list)
    pending_approvals: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    trace_error: bool = False
    checkpoint_error: bool = False
    trace_skipped_reason: str = ""
    checkpoint_skipped_reason: str = ""
    planner_error: bool = False
    planner_error_type: str = ""
    planner_error_message: str = ""
    tool_error: bool = False
    tool_request_id: str = ""
    tool_call_index: int = 0
    gateway_error: bool = False
    gateway_error_type: str = ""
    gateway_error_message: str = ""
    memory_error: bool = False
    memory_recall_error: bool = False
    memory_write_error: bool = False
    memory_recall_status: str = "ok"
    memory_recall_error_type: str = ""
    governance_error: bool = False
    governance_error_type: str = ""
    governance_error_message: str = ""
    profile_error: bool = False
    profile_error_type: str = ""
    profile_error_message: str = ""
    policy_error: bool = False
    policy_error_type: str = ""
    policy_error_message: str = ""
    invalid_input: bool = False
    approval_continuation_id: str = ""
    approval_continuation_resolved: bool = False
    approval_continuation_denied: bool = False
    failures: list[SeedFailureRecord] = field(default_factory=list)
