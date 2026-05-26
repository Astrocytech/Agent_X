"""Canonical seed phase order — single source of truth for all phase definitions.

Required phases must be emitted exactly once per seed turn.
Tool outcome phases are the only valid execution outcomes.
Diagnostic phases are finer-grained sub-phases for observability.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# === Phase spec contract (merged from seed_phase_contract_v1) ===


@dataclass(frozen=True)
class SeedPhaseSpec:
    name: str
    group: str
    required: bool = False
    repeatable: bool = False
    terminal_outcome: bool = False
    allows_group_started: bool = False
    marks_group_completed: bool = False
    marks_group_failed: bool = False
    marks_group_skipped: bool = False
    allowed_after: tuple[str, ...] = ()


SEED_PHASE_CONTRACT_V1: tuple[SeedPhaseSpec, ...] = (
    SeedPhaseSpec(name="input_received", group="input", required=True, allows_group_started=True, allowed_after=()),
    SeedPhaseSpec(name="empty_input_detected", group="input", required=False, marks_group_completed=True, allowed_after=("input_received",)),
    SeedPhaseSpec(name="goal_normalized", group="interpretation", required=True, allows_group_started=True, marks_group_completed=True, allowed_after=("input_received",)),
    SeedPhaseSpec(name="profile_loaded", group="profile_policy", required=True, allows_group_started=True, allowed_after=("goal_normalized",)),
    SeedPhaseSpec(name="profile_load_failed", group="profile_policy", required=False, marks_group_failed=True, allowed_after=("goal_normalized",)),
    SeedPhaseSpec(name="task_created", group="profile_policy", required=True, allowed_after=("profile_loaded",)),
    SeedPhaseSpec(name="task_classification_failed", group="profile_policy", required=False, marks_group_failed=True, allowed_after=("profile_loaded",)),
    SeedPhaseSpec(name="policy_computed", group="profile_policy", required=True, allowed_after=("task_created",)),
    SeedPhaseSpec(name="policy_failed", group="profile_policy", required=False, marks_group_failed=True, allowed_after=("task_created",)),
    SeedPhaseSpec(name="capability_selected", group="profile_policy", required=True, repeatable=True, marks_group_completed=True, allowed_after=("policy_computed",)),
    SeedPhaseSpec(name="memory_recall_completed", group="planning", required=False, allows_group_started=True, marks_group_completed=True, allowed_after=("capability_selected",)),
    SeedPhaseSpec(name="memory_recall_failed", group="planning", required=False, marks_group_failed=True, allowed_after=("capability_selected",)),
    SeedPhaseSpec(name="memory_recall_skipped", group="planning", required=False, marks_group_skipped=True, allowed_after=("capability_selected",)),
    SeedPhaseSpec(name="planner_decision_made", group="planning", required=True, allows_group_started=True, marks_group_completed=True, allowed_after=("capability_selected", "memory_recall_completed")),
    SeedPhaseSpec(name="planner_failed", group="planning", required=False, marks_group_failed=True, allowed_after=("capability_selected",)),
    SeedPhaseSpec(name="governance_checked", group="governance", required=True, allows_group_started=True, marks_group_completed=True, allowed_after=("planner_decision_made",)),
    SeedPhaseSpec(name="governance_failed", group="governance", required=False, marks_group_failed=True, allowed_after=("planner_decision_made",)),
    SeedPhaseSpec(name="governance_pending_approval", group="governance", required=False, marks_group_skipped=True, allowed_after=("governance_checked",)),
    SeedPhaseSpec(name="governance_denied", group="governance", required=False, marks_group_failed=True, allowed_after=("governance_checked",)),
    SeedPhaseSpec(name="approval_continuation_resolved", group="approval", required=False, allows_group_started=True, marks_group_completed=True, allowed_after=("governance_checked", "governance_pending_approval", "governance_denied")),
    SeedPhaseSpec(name="approval_continuation_failed", group="approval", required=False, marks_group_failed=True, marks_group_completed=True, allowed_after=("approval_continuation_resolved",)),
    SeedPhaseSpec(name="tool_requested", group="execution", required=True, allows_group_started=True, allowed_after=("governance_checked", "governance_pending_approval", "governance_denied", "approval_continuation_resolved", "approval_continuation_failed")),
    SeedPhaseSpec(name="tool_gateway_called", group="execution", required=False, allowed_after=("tool_requested",)),
    SeedPhaseSpec(name="tool_succeeded", group="execution", required=False, terminal_outcome=True, marks_group_completed=True, allowed_after=("tool_gateway_called",)),
    SeedPhaseSpec(name="tool_failed", group="execution", required=False, terminal_outcome=True, marks_group_failed=True, marks_group_completed=True, allowed_after=("tool_gateway_called",)),
    SeedPhaseSpec(name="tool_blocked", group="execution", required=False, terminal_outcome=True, marks_group_failed=True, marks_group_completed=True, allowed_after=("tool_gateway_called", "governance_checked", "governance_denied")),
    SeedPhaseSpec(name="tool_pending_approval", group="execution", required=False, terminal_outcome=True, marks_group_skipped=True, marks_group_completed=True, allowed_after=("tool_gateway_called", "governance_pending_approval")),
    SeedPhaseSpec(name="gateway_failed", group="execution", required=False, terminal_outcome=True, marks_group_failed=True, marks_group_completed=True, allowed_after=("tool_gateway_called",)),
    SeedPhaseSpec(name="memory_written_or_skipped_with_reason", group="memory", required=True, allows_group_started=True, marks_group_completed=True, allowed_after=("evaluation_completed", "evaluation_failed")),
    SeedPhaseSpec(name="checkpoint_write_started", group="persistence", required=True, allows_group_started=True, allowed_after=("memory_written_or_skipped_with_reason",)),
    SeedPhaseSpec(name="checkpoint_write_completed", group="persistence", required=True, marks_group_completed=True, allowed_after=("checkpoint_write_started",)),
    SeedPhaseSpec(name="checkpoint_write_failed", group="persistence", required=False, marks_group_failed=True, marks_group_completed=True, allowed_after=("checkpoint_write_started",)),
    SeedPhaseSpec(name="trace_write_started", group="persistence", required=True, allowed_after=("tool_succeeded", "tool_failed", "tool_blocked", "tool_pending_approval", "gateway_failed", "governance_checked", "governance_pending_approval", "governance_denied", "governance_failed", "empty_input_detected", "profile_load_failed", "task_classification_failed", "policy_failed")),
    SeedPhaseSpec(name="trace_write_completed", group="persistence", required=True, marks_group_completed=True, allowed_after=("trace_write_started",)),
    SeedPhaseSpec(name="trace_write_failed", group="persistence", required=False, marks_group_failed=True, marks_group_completed=True, allowed_after=("trace_write_started",)),
    SeedPhaseSpec(name="evaluation_completed", group="evaluation", required=True, allows_group_started=True, marks_group_completed=True, allowed_after=("trace_write_completed", "trace_write_failed")),
    SeedPhaseSpec(name="evaluation_failed", group="evaluation", required=False, marks_group_failed=True, allowed_after=("trace_write_started",)),
    SeedPhaseSpec(name="output_returned", group="output", required=True, allows_group_started=True, marks_group_completed=True, terminal_outcome=True, allowed_after=("evaluation_completed", "evaluation_failed", "trace_write_completed", "trace_write_failed", "checkpoint_write_completed")),
    SeedPhaseSpec(name="degraded_operation", group="output", required=False, repeatable=True, allowed_after=("input_received", "goal_normalized", "profile_loaded", "task_created", "policy_computed", "capability_selected", "planner_decision_made", "governance_checked", "tool_requested", "tool_gateway_called", "evaluation_completed")),
)

REQUIRED_PHASES: tuple[str, ...] = tuple(s.name for s in SEED_PHASE_CONTRACT_V1 if s.required)
PHASE_GROUPS: dict[str, list[str]] = {}
for _spec in SEED_PHASE_CONTRACT_V1:
    PHASE_GROUPS.setdefault(_spec.group, []).append(_spec.name)
REQUIRED_GROUPS: tuple[str, ...] = tuple(sorted(set(s.group for s in SEED_PHASE_CONTRACT_V1 if s.required)))
PHASE_COMPLETION_MAP: dict[str, dict[str, Any]] = {}
for _spec in SEED_PHASE_CONTRACT_V1:
    PHASE_COMPLETION_MAP[_spec.name] = {
        "marks_group_completed": _spec.marks_group_completed,
        "marks_group_failed": _spec.marks_group_failed,
        "marks_group_skipped": _spec.marks_group_skipped,
        "terminal_outcome": _spec.terminal_outcome,
    }

# === Derived constants ===

REQUIRED_SEED_PORTS: frozenset[str] = frozenset({
    "profile_port", "policy_port", "tool_gateway_port", "memory_port",
    "evaluation_port", "trace_port", "checkpoint_port", "governance_port", "planner_port",
})

SEED_PORT_SURFACE: frozenset[str] = frozenset({
    "config_port", "path_resolver_port", "risk_policy_port", "evidence_writer_port",
})

TOOL_OUTCOME_PHASES: set[str] = {
    "tool_succeeded", "tool_failed", "tool_blocked",
    "tool_pending_approval", "gateway_failed",
}

DIAGNOSTIC_PHASES: list[str] = [
    "tool_succeeded",
    "tool_failed",
    "tool_blocked",
    "tool_pending_approval",
    "gateway_failed",
    "empty_input_detected",
    "trace_write_failed",
    "checkpoint_write_failed",
    "profile_load_failed",
    "task_classification_failed",
    "policy_failed",
    "memory_recall_completed",
    "memory_recall_failed",
    "memory_recall_skipped",
    "planner_failed",
    "governance_failed",
    "governance_pending_approval",
    "governance_denied",
    "evaluation_failed",
]

CANONICAL_ORDER: list[str] = [
    "input_received",
    "empty_input_detected",
    "goal_normalized",
    "profile_loaded",
    "profile_load_failed",
    "task_created",
    "task_classification_failed",
    "policy_computed",
    "policy_failed",
    "capability_selected",
    "memory_recall_completed",
    "memory_recall_failed",
    "memory_recall_skipped",
    "planner_decision_made",
    "planner_failed",
    "governance_checked",
    "governance_failed",
    "governance_pending_approval",
    "governance_denied",
    "approval_continuation_resolved",
    "approval_continuation_failed",
    "tool_requested",
    "tool_gateway_called",
    "tool_succeeded",
    "tool_failed",
    "tool_blocked",
    "tool_pending_approval",
    "gateway_failed",
    "trace_write_started",
    "trace_write_completed",
    "trace_write_failed",
    "evaluation_completed",
    "evaluation_failed",
    "memory_written_or_skipped_with_reason",
    "checkpoint_write_started",
    "checkpoint_write_completed",
    "checkpoint_write_failed",
    "output_returned",
    "degraded_operation",
]

ALL_PHASES: set[str] = set(CANONICAL_ORDER)


class SeedPhase(str, Enum):
    INPUT_RECEIVED = "input_received"
    EMPTY_INPUT_DETECTED = "empty_input_detected"
    GOAL_NORMALIZED = "goal_normalized"
    PROFILE_LOADED = "profile_loaded"
    PROFILE_LOAD_FAILED = "profile_load_failed"
    TASK_CREATED = "task_created"
    TASK_CLASSIFICATION_FAILED = "task_classification_failed"
    POLICY_COMPUTED = "policy_computed"
    POLICY_FAILED = "policy_failed"
    CAPABILITY_SELECTED = "capability_selected"
    MEMORY_RECALL_COMPLETED = "memory_recall_completed"
    MEMORY_RECALL_FAILED = "memory_recall_failed"
    MEMORY_RECALL_SKIPPED = "memory_recall_skipped"
    PLANNER_DECISION_MADE = "planner_decision_made"
    PLANNER_FAILED = "planner_failed"
    GOVERNANCE_CHECKED = "governance_checked"
    GOVERNANCE_FAILED = "governance_failed"
    GOVERNANCE_PENDING_APPROVAL = "governance_pending_approval"
    GOVERNANCE_DENIED = "governance_denied"
    APPROVAL_CONTINUATION_RESOLVED = "approval_continuation_resolved"
    APPROVAL_CONTINUATION_FAILED = "approval_continuation_failed"
    TOOL_REQUESTED = "tool_requested"
    TOOL_GATEWAY_CALLED = "tool_gateway_called"
    TOOL_SUCCEEDED = "tool_succeeded"
    TOOL_FAILED = "tool_failed"
    TOOL_BLOCKED = "tool_blocked"
    TOOL_PENDING_APPROVAL = "tool_pending_approval"
    GATEWAY_FAILED = "gateway_failed"
    MEMORY_WRITTEN_OR_SKIPPED = "memory_written_or_skipped_with_reason"
    EVALUATION_COMPLETED = "evaluation_completed"
    EVALUATION_FAILED = "evaluation_failed"
    CHECKPOINT_WRITE_STARTED = "checkpoint_write_started"
    CHECKPOINT_WRITE_COMPLETED = "checkpoint_write_completed"
    CHECKPOINT_WRITE_FAILED = "checkpoint_write_failed"
    TRACE_WRITE_STARTED = "trace_write_started"
    TRACE_WRITE_COMPLETED = "trace_write_completed"
    TRACE_WRITE_FAILED = "trace_write_failed"
    OUTPUT_RETURNED = "output_returned"
    DEGRADED_OPERATION = "degraded_operation"

    @classmethod
    def required_phases(cls) -> list[SeedPhase]:
        return [cls(p) for p in REQUIRED_PHASES]

    @classmethod
    def tool_outcome_group(cls) -> set[SeedPhase]:
        return {cls(p) for p in TOOL_OUTCOME_PHASES}

    @classmethod
    def optional_phases(cls) -> list[SeedPhase]:
        return [cls(p) for p in DIAGNOSTIC_PHASES]


ALL_SEED_PHASES: list[str] = [p.value for p in SeedPhase]


FINAL_SEED_PHASE_ORDER = [
    "input",
    "goal",
    "profile",
    "policy",
    "memory_recall",
    "planning",
    "governance",
    "approval",
    "execution",
    "memory_record",
    "evaluation",
    "trace",
    "checkpoint",
    "finale",
]

REQUIRED_SEED_PHASES: frozenset[str] = frozenset(FINAL_SEED_PHASE_ORDER)
CANONICAL_SEED_PHASES = CANONICAL_ORDER

PHASE_REQUIRED_PORTS = {
    "profile": ["profile_port"],
    "policy": ["policy_port"],
    "memory_recall": ["memory_port"],
    "planning": ["planner_port"],
    "governance": ["governance_port"],
    "execution": ["tool_gateway_port"],
    "memory_record": ["memory_port"],
    "evaluation": ["evaluation_port"],
    "trace": ["trace_port"],
    "checkpoint": ["checkpoint_port"],
}

PHASE_ALLOWED_WRITES = {
    "memory_record": ["memory"],
    "evaluation": ["evaluation"],
    "trace": ["trace"],
    "checkpoint": ["checkpoint"],
}
