"""Record phases — memory write, trace write, checkpoint save, evaluation."""

import logging

from core_kernel.models.kernel_io import KernelInput
from core_kernel.models.enums.seed_failure_reason import SeedFailureReason
from core_kernel.runtime.seed_turn_record import _RunContext

logger = logging.getLogger(__name__)


def run_memory_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    memory_facade = ports.get("memory_facade")
    if memory_facade is None:
        emit("memory_written_or_skipped_with_reason", skipped="no_memory_facade")
        return ctx
    ctx_dict = {
        "run_id": ctx.run_id,
        "profile_id": inp.profile_id,
        "policy_id": ctx.policy_id,
    }
    try:
        tool_name = getattr(ctx.planner_decision, "tool_name", "") if ctx.planner_decision else ""
        record_type = "tool_result" if tool_name else "turn_observation"
        refs = memory_facade.store(record_type, ctx.tool_output, ctx_dict)
        ctx.written_memory_refs = refs
        ctx.memory_refs = list(set(ctx.recalled_memory_refs + refs))
        episode = _build_episode(ctx, inp)
        if episode:
            memory_facade.store("episode", str(episode), {"run_id": ctx.run_id})
            try:
                _promote_to_skill_if_repeatable(ctx, episode, memory_facade, emit)
            except Exception:
                logger.warning("skill promotion failed", exc_info=True)
    except Exception:
        ctx.memory_write_error = True
        ctx.memory_error = True
        ctx.memory_skipped_reason = SeedFailureReason.MEMORY_FAILED.value
        emit("memory_written_or_skipped_with_reason", skipped="memory_write_failed")
        return ctx
    emit("memory_written_or_skipped_with_reason", refs=ctx.written_memory_refs)
    return ctx


def _build_episode(ctx: _RunContext, inp: KernelInput) -> dict | None:
    return {
        "type": "episode",
        "episode": {
            "episode_id": ctx.run_id,
            "run_id": ctx.run_id,
            "problem": inp.user_goal,
            "context": inp.profile_id,
            "attempted_moves": (
                [{"tool_name": getattr(ctx.planner_decision, "tool_name", ""), "output": ctx.tool_output}]
                if ctx.planner_decision else []
            ),
            "outcome": ctx.tool_output or "no_action",
            "failure_modes": list(ctx.blocked_actions) + (
                [ctx.evaluation_skipped_reason] if ctx.evaluation_skipped_reason else []
            ),
            "lesson": "",
            "reusable_strategy": "",
            "evaluation_score": ctx.evaluation_score,
            "trace_id": ctx.trace_id or "",
            "checkpoint_id": ctx.checkpoint_id or "",
            "evidence_refs": list(ctx.recalled_memory_refs),
        },
    }


def _promote_to_skill_if_repeatable(
    ctx: _RunContext, episode: dict, memory_facade, emit
) -> None:
    tool_name = ""
    if ctx.planner_decision is not None:
        tool_name = getattr(ctx.planner_decision, "tool_name", "") or ""
    if not tool_name:
        return
    profile_id = getattr(ctx, "profile_id", "")
    similar = memory_facade.retrieve_relevant(
        tool_name,
        profile_id=profile_id,
        record_types=["episode"],
    ) if profile_id else []
    prior_count = sum(
        1 for r in similar
        if isinstance(r, dict) and r.get("ctx", {}).get("record_type") == "episode"
    )
    if prior_count >= 2:
        emit("skill_promoted", skill_id=f"sk-{ctx.run_id}", tool_name=tool_name)


def run_trace_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    trace_port = ports["trace_port"]
    emit("trace_write_started")
    try:
        trace_id = trace_port.write(ctx.run_id, ctx.events)
        ctx.trace_id = trace_id
        emit("trace_write_completed", id=f"trace-{ctx.run_id}")
    except Exception as exc:
        emit("trace_write_failed", error=str(exc))
        ctx.trace_error = True
        ctx.trace_skipped_reason = str(exc)
        ctx.trace_id = ""
    return ctx


def run_checkpoint_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    checkpoint_port = ports["checkpoint_port"]
    emit("checkpoint_write_started")
    state = {
        "run_id": ctx.run_id,
        "goal_id": ctx.goal.id if ctx.goal else "",
        "task_id": ctx.task.id if ctx.task else "",
        "policy_id": ctx.policy_id,
        "trace_id": ctx.trace_id,
        "checkpoint_id": ctx.checkpoint_id,
        "evaluation_score": ctx.evaluation_score,
        "verdict_id": ctx.verdict_id,
        "evaluation_criteria": ctx.evaluation_criteria,
        "tool_output": ctx.tool_output,
        "output_returned": True,
        "events": list(ctx.events),
    }
    try:
        checkpoint_id = checkpoint_port.save(ctx.run_id, state)
        ctx.checkpoint_id = checkpoint_id
        emit("checkpoint_write_completed", id=checkpoint_id)
    except Exception as exc:
        emit("checkpoint_write_failed", error=str(exc))
        ctx.checkpoint_error = True
        ctx.checkpoint_skipped_reason = str(exc)
        ctx.checkpoint_id = ""
    return ctx


def run_evaluation_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    evaluation_port = ports["evaluation_port"]
    memory_facade = ports.get("memory_facade")
    recorder = ports.get("phase_recorder")
    try:
        from core_kernel.models.kernel_results import SeedTurnResult

        turn = SeedTurnResult(
            run_id=ctx.run_id or "",
            status=(
                str(ctx.tool_output) if not isinstance(ctx.tool_output, str) else ctx.tool_output
            ),
            goal_text=ctx.goal.text or "",
            tool_output=(
                str(ctx.tool_output) if not isinstance(ctx.tool_output, str) else ctx.tool_output
            ),
            trace_id=ctx.trace_id or "",
            checkpoint_id=ctx.checkpoint_id or "",
            blocked_actions=list(ctx.blocked_actions),
            pending_approvals=list(ctx.pending_approvals),
            memory_writes=list(ctx.written_memory_refs),
            profile_id=inp.profile_id,
            policy_id=ctx.policy_id or "",
            planner_decision_id=getattr(ctx.planner_decision, "task_id", ""),
            governance_decision_id=getattr(ctx.governance_decision, "decision_id", ""),
        )
        try:
            result = evaluation_port.evaluate_turn(turn)
        except AttributeError:
            result = evaluation_port.evaluate(
                ctx.goal,
                ctx.tool_output,
                ctx={
                    "run_id": ctx.run_id,
                    "policy_id": ctx.policy_id or "",
                    "tool_name": getattr(ctx.planner_decision, "tool_name", ""),
                    "blocked": bool(ctx.blocked_actions),
                    "pending_approval": bool(ctx.pending_approvals),
                },
            )
        ctx.evaluation_score = result.score
        ctx.verdict_id = getattr(result, "verdict_id", "")
        ctx.evaluation_status = "completed"
        if memory_facade is not None:
            memory_facade.store_evaluation_result(
                result.score,
                ctx.verdict_id,
                {"run_id": ctx.run_id},
            )


    except Exception as exc:
        ctx.evaluation_status = "failed"
        ctx.evaluation_error_type = type(exc).__name__
        ctx.evaluation_error_message = str(exc)
        ctx.evaluation_skipped_reason = SeedFailureReason.EVALUATION_FAILED.value
        if recorder:
            recorder.start_phase("evaluation_failed")
        emit("evaluation_failed", error=str(exc), error_type=type(exc).__name__)
        if recorder:
            recorder.end_phase(success=False, error=str(exc))
        return ctx

    if recorder:
        recorder.start_phase("evaluation_completed")
    emit(
        "evaluation_completed",
        score=result.score,
        verdict_id=ctx.verdict_id,
        failure_reason=getattr(result, "failure_reason", "") or "",
    )
    if recorder:
        recorder.end_phase(success=True)
    return ctx
