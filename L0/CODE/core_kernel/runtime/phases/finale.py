from core_kernel.models.kernel_io import KernelOutput, KernelInput
from core_kernel.models.enums.seed_failure_reason import SeedFailureReason
from core_kernel.models.state_model import RunState
from core_kernel.runtime.seed_status import compute_seed_status
from core_kernel.runtime.seed_turn_record import _RunContext
from core_kernel.evidence.evidence_ledger import record_evidence


def run_output_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> KernelOutput:
    pre_status = compute_seed_status(ctx)

    record_evidence({
        "run_id": ctx.run_id,
        "status": pre_status,
        "evaluation_score": ctx.evaluation_score,
        "evaluation_status": ctx.evaluation_status,
        "profile_id": inp.profile_id,
        "goal_id": ctx.goal.id if ctx.goal else "",
    })

    trace_id = ctx.trace_id if ctx.trace_id else ""
    checkpoint_id = ctx.checkpoint_id if ctx.checkpoint_id else ""

    emit(
        "output_returned",
        status=pre_status,
        trace_id=trace_id,
        checkpoint_id=checkpoint_id,
    )

    missing_phases = ports["phase_recorder"].validate_all_phases_completed()

    if missing_phases:
        final_status = RunState.FAILED.value
    else:
        final_status = pre_status

    event_count = len(ctx.events)
    last_event = ctx.events[-1] if ctx.events else {}
    last_event_hash = str(hash(frozenset(last_event.items()))) if last_event else ""

    return KernelOutput(
        run_id=ctx.run_id,
        profile_id=inp.profile_id,
        status=final_status,
        primary_result=ctx.tool_output or SeedFailureReason.NO_ACTION.value,
        trace_id=trace_id,
        checkpoint_id=checkpoint_id,
        memory_writes=list(ctx.written_memory_refs),
        evaluation_score=ctx.evaluation_score,
        evaluation_status=ctx.evaluation_status,
        verdict_id=ctx.verdict_id,
        pending_approvals=list(ctx.pending_approvals),
        blocked_actions=list(ctx.blocked_actions),
        metadata={
            "runtime_authority": "seed",
            "runtime_class": "SeedKernelRuntime",
            "policy_id": ctx.policy_id,
            "policy_decision_id": getattr(ctx.governance_decision, "decision_id", ""),
            "governance_decision_id": getattr(ctx.governance_decision, "decision_id", ""),
            "goal_id": ctx.goal.id if ctx.goal else "",
            "task_id": ctx.task.id if ctx.task else "",
            "missing_phases": missing_phases,
            "events": ctx.events,
            "event_count": event_count,
            "last_event_hash": last_event_hash,
            "total_recorded_phases": event_count,
            "invalid_input": getattr(ctx, "invalid_input", False),
            "memory_recall_status": getattr(ctx, "memory_recall_status", "ok"),
            "memory_recall_error_type": getattr(ctx, "memory_recall_error_type", ""),
            "evaluation_status": ctx.evaluation_status,
        },
    )
