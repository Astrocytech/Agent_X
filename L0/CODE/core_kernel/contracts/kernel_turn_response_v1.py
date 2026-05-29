from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

KERNEL_RESPONSE_SCHEMA_VERSION = "1.0"

PUBLIC_STATUS_MAP = {
    "completed": "completed",
    "blocked_by_governance": "blocked",
    "approval_required": "needs_approval",
    "memory_failed": "completed_with_memory_warning",
    "evaluation_failed": "completed_with_evaluation_warning",
    "trace_failed": "failed",
    "checkpoint_failed": "failed",
    "invalid_input": "failed",
    "runtime_error": "failed",
}


@dataclass
class KernelTurnResponseV1:
    schema_version: str = KERNEL_RESPONSE_SCHEMA_VERSION
    request_id: str = ""
    run_id: str = ""
    status: str = ""
    primary_output: str = ""
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    governance_summary: dict[str, Any] = field(default_factory=dict)
    memory_refs: list[str] = field(default_factory=list)
    trace_ref: str = ""
    checkpoint_ref: str = ""
    evaluation_summary: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_kernel_output(cls, output, request_id: str = "") -> KernelTurnResponseV1:
        md = dict(output.metadata or {})
        return cls(
            request_id=request_id,
            run_id=output.run_id,
            status=(
                str(output.status.value) if hasattr(output.status, "value") else str(output.status)
            ),
            primary_output=output.primary_result or "",
            trace_ref=output.trace_id or "",
            checkpoint_ref=output.checkpoint_id or "",
            memory_refs=list(output.memory_writes or []),
            evaluation_summary={
                "score": output.evaluation_score,
                "verdict_id": output.verdict_id or "",
            },
            governance_summary={
                "policy_decision_id": md.get("policy_decision_id", ""),
                "governance_decision_id": md.get("governance_decision_id", ""),
            },
            errors=[
                {"phase": k, "reason": v}
                for k, v in md.items()
                if k.endswith("_error") or k.endswith("_skipped_reason")
            ],
            metadata={
                "profile_id": output.profile_id,
                "total_recorded_phases": md.get("total_recorded_phases", 0),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "status": self.status,
            "primary_output": self.primary_output,
            "trace_ref": self.trace_ref,
            "checkpoint_ref": self.checkpoint_ref,
            "memory_refs": list(self.memory_refs),
            "governance_summary": dict(self.governance_summary),
            "evaluation_summary": dict(self.evaluation_summary),
            "errors": list(self.errors),
        }
