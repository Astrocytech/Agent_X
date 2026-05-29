"""ResponseBuilder — Central response assembly with field validation."""

from __future__ import annotations

from core_kernel.models.kernel_results import KernelTurnResponse
from core_kernel.contracts.kernel_turn_response_v1 import PUBLIC_STATUS_MAP
from core_kernel.runtime.seed_turn_record import _RunContext


REQUIRED_RESPONSE_FIELDS = frozenset({
    "run_id",
    "status",
    "profile_id",
    "trace_id",
    "checkpoint_id",
    "evaluation_score",
    "memory_refs",
})


def validate_final_turn_artifacts(ctx):
    if not ctx.trace_id:
        raise RuntimeError("Final turn missing trace_id")
    if not ctx.checkpoint_id:
        raise RuntimeError("Final turn missing checkpoint_id")
    if ctx.evaluation_status != "completed":
        raise RuntimeError("Final turn missing completed evaluation")


def build_turn_response(ctx: _RunContext, output_status: str, answer: str) -> KernelTurnResponse:
    validate_final_turn_artifacts(ctx)

    public_status = PUBLIC_STATUS_MAP.get(output_status, "failed")

    return KernelTurnResponse(
        schema_version="seed.response.v1",
        run_id=ctx.run_id,
        status=public_status,
        answer=answer,
        profile_id=ctx.profile_id or "",
        trace_id=ctx.trace_id or "",
        checkpoint_id=ctx.checkpoint_id or "",
        policy_decision_id=getattr(ctx, "policy_decision_id", ""),
        governance_decision_id=getattr(ctx.governance_decision, "decision_id", ""),
        evaluation_verdict_id=ctx.verdict_id or "",
        evaluation_score=ctx.evaluation_score,
        memory_refs=list(getattr(ctx, "written_memory_refs", [])),
        metadata={
            "policy_id": ctx.policy_id or "",
            "evaluation_status": getattr(ctx, "evaluation_status", ""),
            "blocked_actions": list(getattr(ctx, "blocked_actions", [])),
            "pending_approvals": list(getattr(ctx, "pending_approvals", [])),
        },
    )
