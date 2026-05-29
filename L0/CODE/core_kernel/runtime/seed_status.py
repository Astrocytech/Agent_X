"""Standalone status computation for seed runtime turns."""

from core_kernel.models.state_model import RunState
from core_kernel.runtime.seed_turn_record import _RunContext


def compute_seed_status(ctx: _RunContext) -> str:
    if ctx.invalid_input:
        return RunState.INVALID_INPUT.value
    if ctx.planner_error:
        return RunState.PLANNER_FAILED.value
    if ctx.governance_error:
        return RunState.FAILED.value
    if ctx.gateway_error:
        return RunState.GATEWAY_FAILED.value
    if ctx.tool_error:
        return RunState.TOOL_FAILED.value
    if ctx.profile_error:
        return RunState.FAILED.value
    if ctx.trace_error:
        return RunState.FAILED.value
    if ctx.checkpoint_error:
        return RunState.FAILED.value
    if ctx.blocked_actions:
        return RunState.POLICY_BLOCKED.value
    if ctx.pending_approvals:
        return RunState.WAITING_FOR_HUMAN.value
    if not ctx.planner_decision:
        return RunState.FAILED.value
    if not ctx.policy_id:
        return RunState.FAILED.value
    if not ctx.governance_decision:
        return RunState.FAILED.value
    if not ctx.tool_output:
        return RunState.FAILED.value
    if ctx.memory_write_error:
        return RunState.FAILED.value
    if ctx.trace_error or not ctx.trace_id:
        return RunState.FAILED.value
    if ctx.checkpoint_error or not ctx.checkpoint_id:
        return RunState.FAILED.value
    return RunState.COMPLETED.value
