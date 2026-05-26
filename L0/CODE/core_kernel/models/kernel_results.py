from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from core_kernel.contracts.kernel_contracts import KernelTurnStatus
from core_kernel.contracts.trace_contracts import EvaluationVerdict


def _build_status_map() -> dict[str, KernelTurnStatus]:
    from core_kernel.state.kernel_state import RunState

    return {
        RunState.COMPLETED.value: KernelTurnStatus.SUCCESS,
        RunState.INVALID_INPUT.value: KernelTurnStatus.PARTIAL,
        RunState.WAITING_FOR_HUMAN.value: KernelTurnStatus.PARTIAL,
        RunState.FAILED.value: KernelTurnStatus.FAILED,
        RunState.POLICY_BLOCKED.value: KernelTurnStatus.BLOCKED,
        RunState.PLANNER_FAILED.value: KernelTurnStatus.FAILED,
        RunState.GATEWAY_FAILED.value: KernelTurnStatus.FAILED,
        RunState.TOOL_FAILED.value: KernelTurnStatus.FAILED,
        RunState.RECOVERY_PLANNING.value: KernelTurnStatus.RECOVERY_REQUIRED,
        RunState.DEGRADED_MODE.value: KernelTurnStatus.RECOVERY_REQUIRED,
        "error": KernelTurnStatus.ERROR,
    }


_STATUS_MAP: dict[str, KernelTurnStatus] | None = None


def _get_status_map() -> dict[str, KernelTurnStatus]:
    global _STATUS_MAP
    if _STATUS_MAP is None:
        _STATUS_MAP = _build_status_map()
    return _STATUS_MAP


@dataclass
class SeedTurnResult:
    run_id: str = ""
    status: str = ""
    goal_text: str = ""
    tool_output: str = ""
    evaluation: EvaluationVerdict | None = None
    trace_id: str = ""
    checkpoint_id: str = ""
    memory_writes: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    pending_approvals: list[str] = field(default_factory=list)
    profile_id: str = ""
    policy_id: str = ""
    planner_decision_id: str = ""
    governance_decision_id: str = ""
    tool_request_id: str = ""
    tool_result_id: str = ""
    error: str = ""

    def to_kernel_output(self) -> Any:
        from core_kernel.models.kernel_io import KernelOutput as _KernelOutput
        eval_score = self.evaluation.score if self.evaluation else None
        return _KernelOutput(
            run_id=self.run_id,
            profile_id=self.profile_id,
            status=self.status,
            primary_result=self.tool_output,
            trace_id=self.trace_id,
            checkpoint_id=self.checkpoint_id,
            memory_writes=list(self.memory_writes),
            evaluation_score=eval_score,
            evaluation_status="completed" if self.evaluation else "not_run",
            verdict_id=self.evaluation.verdict_id if self.evaluation else "",
            pending_approvals=list(self.pending_approvals),
            blocked_actions=list(self.blocked_actions),
            metadata={
                "profile_id": self.profile_id,
                "policy_id": self.policy_id,
                "planner_decision_id": self.planner_decision_id,
                "governance_decision_id": self.governance_decision_id,
                "tool_request_id": self.tool_request_id,
                "tool_result_id": self.tool_result_id,
            },
        )


@dataclass(frozen=True)
class KernelTurnResponse:
    answer: str
    status: KernelTurnStatus
    run_id: str
    profile_id: str
    trace_id: str
    policy_decision_id: str
    evaluation_score: float | None = None
    evaluation_status: str = ""
    memory_refs: list[str] = field(default_factory=list)
    selected_move_id: str = ""
    governance_decision_id: str = ""
    evaluation_verdict_id: str = ""
    checkpoint_id: str = ""
    tool_result_id: str = ""
    config_hash: str = ""
    rejected_alternatives: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _generate_id() -> str:
    return uuid.uuid4().hex[:12]
