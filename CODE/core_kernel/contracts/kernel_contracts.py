"""Internal runtime IO types — KernelInput/KernelOutput/KernelTurnStatus.

Use KernelTurnRequestV1 / KernelTurnResponseV1 for public contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any



class KernelTurnStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    FAILED = "failed"
    ERROR = "error"
    RECOVERY_REQUIRED = "recovery_required"


@dataclass(frozen=True)
class KernelInput:
    user_goal: str
    profile_id: str
    context: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KernelOutput:
    run_id: str
    profile_id: str
    status: str
    primary_result: str
    trace_id: str
    checkpoint_id: str
    memory_writes: list[str]
    evaluation_score: float | None = None
    evaluation_status: str = ""
    pending_approvals: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    verdict_id: str = ""
    selected_move_id: str = ""
    governance_decision_id: str = ""
    evaluation_verdict_id: str = ""
    tool_result_id: str = ""
    config_hash: str = ""
    rejected_alternatives: list[str] = field(default_factory=list)

    @classmethod
    def from_kernel_result(
        cls,
        result: Any,
        profile_id: str,
        context_metadata: dict[str, Any] | None = None,
    ) -> KernelOutput:
        result_meta = dict(result.metadata or {})
        context_meta = dict(context_metadata or {})
        pending_approvals = list(context_meta.get("pending_approvals", []))
        blocked_actions = (
            ["awaiting_approval"]
            if result.status == "waiting_for_human" and pending_approvals
            else []
        )
        eval_score = result_meta.get("last_evaluation_score")
        return cls(
            run_id=result.run_id,
            profile_id=profile_id,
            status=result.status,
            primary_result=str(result_meta.get("primary_result", result.summary)),
            trace_id=str(result_meta.get("trace_id", "")),
            checkpoint_id=str(result_meta.get("checkpoint_id", "")),
            memory_writes=list(result_meta.get("memory_writes", [])),
            evaluation_score=float(eval_score) if eval_score is not None else None,
            evaluation_status=str(result_meta.get("evaluation_status", "")),
            selected_move_id=str(result_meta.get("selected_move_id", "")),
            governance_decision_id=str(result_meta.get("governance_decision_id", "")),
            evaluation_verdict_id=str(result_meta.get("evaluation_verdict_id", "")),
            tool_result_id=str(result_meta.get("tool_result_id", "")),
            config_hash=str(result_meta.get("config_hash", "")),
            rejected_alternatives=list(result_meta.get("rejected_alternatives", [])),
            pending_approvals=pending_approvals,
            blocked_actions=blocked_actions,
            metadata=dict(result_meta),
        )


__all__ = [
    "KernelTurnStatus",
    "KernelInput",
    "KernelOutput",
]
