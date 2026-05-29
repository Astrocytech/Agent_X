"""Prelude phases — input validation, goal normalization, profile loading, task creation, policy computation."""

import uuid

from core_kernel.models.kernel_atoms import Goal, Task
from core_kernel.models.kernel_io import KernelInput
from core_kernel.models.enums.seed_failure_reason import SeedFailureReason
from core_kernel.runtime.seed_turn_record import _RunContext


def run_input_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    emit("input_received", goal=inp.user_goal[:80] if inp.user_goal else "")
    if not inp.user_goal or not inp.user_goal.strip():
        ctx.tool_output = SeedFailureReason.EMPTY_INPUT.value
        ctx.invalid_input = True
        emit("empty_input_detected")
        ctx.goal = Goal(
            id=f"g-{uuid.uuid4().hex[:8]}",
            text="",
            constraints=[],
            success_criteria=[],
        )
    return ctx


def run_goal_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    if ctx.invalid_input:
        return ctx
    try:
        goal = Goal(
            id=f"g-{uuid.uuid4().hex[:8]}",
            text=inp.user_goal,
            constraints=["safe"],
            success_criteria=["completed"],
        )
        ctx.goal = goal
        emit("goal_normalized", id=goal.id)
    except Exception as exc:
        ctx.planner_error = True
        ctx.planner_error_type = type(exc).__name__
        ctx.planner_error_message = str(exc)
    return ctx


def run_profile_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    if ctx.invalid_input:
        return ctx
    profile_port = ports["profile_port"]
    try:
        profile = profile_port.load(inp.profile_id)
    except Exception as exc:
        ctx.profile_error = True
        ctx.profile_error_type = type(exc).__name__
        ctx.profile_error_message = str(exc)
        emit("profile_load_failed", profile_id=inp.profile_id, error=str(exc))
        return ctx
    ctx.profile = profile
    emit("profile_loaded", id=inp.profile_id)
    return ctx


def run_task_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    if ctx.invalid_input or ctx.profile_error:
        return ctx
    try:
        task_type = "direct_answer"
        profile = ctx.profile
        if isinstance(profile, dict):
            profile_task_type = profile.get("task_type") or profile.get("default_task_type")
        else:
            profile_task_type = getattr(profile, "task_type", None) or getattr(
                profile, "default_task_type", None
            )
        effective_task_type = profile_task_type or task_type
        task = Task(
            id=f"t-{uuid.uuid4().hex[:8]}",
            goal_id=ctx.goal.id or "",
            title="seed_task",
            description=ctx.goal.text[:100],
            status="created",
            task_type=effective_task_type,
        )
        ctx.task = task
        emit("task_created", task_id=task.id, task_type=effective_task_type)
    except Exception as exc:
        emit("task_classification_failed", error=str(exc))
        ctx.planner_error = True
        ctx.planner_error_type = type(exc).__name__
        ctx.planner_error_message = str(exc)
    return ctx


def run_policy_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    if ctx.invalid_input or ctx.profile_error:
        return ctx
    try:
        policy_port = ports["policy_port"]
        policy_decision = policy_port.compute(ctx.profile, ctx.task)
        if policy_decision is None:
            ctx.policy_error = True
            ctx.policy_error_type = "policy_returned_none"
            ctx.policy_error_message = "Policy port returned None"
            emit("policy_failed", error="policy_port_returned_none")
            return ctx
        policy_id = getattr(policy_decision, "target_id", None)
        if not policy_id:
            ctx.policy_error = True
            ctx.policy_error_type = "missing_target_id"
            ctx.policy_error_message = "Policy decision missing target_id"
            emit("policy_failed", error="missing_target_id")
            return ctx
        ctx.policy_id = policy_id
        emit("policy_computed", policy_id=policy_id)
        emit("capability_selected", policy_id=policy_id)
    except Exception as exc:
        ctx.policy_error = True
        ctx.policy_error_type = type(exc).__name__
        ctx.policy_error_message = str(exc)
        emit("policy_failed", error=str(exc))
    return ctx
