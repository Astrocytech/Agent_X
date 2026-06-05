from __future__ import annotations

from typing import Any, Callable

from agentx_evolve.orchestrator.orchestrator_models import (
    ToolInvocationBinding,
    ExecutionStep,
    utc_now_iso,
    new_id,
)


ALLOWED_TOOLS = {"source_reader", "file_lister", "diff_viewer", "search_code", "read_file"}


def _check_tool_allowed(step: ExecutionStep, tool_name: str) -> bool:
    if tool_name not in ALLOWED_TOOLS:
        return False
    if step.assigned_role and "tool" not in step.assigned_role.lower():
        return False
    return True


def invoke_tool_for_step(
    step: ExecutionStep,
    tool_name: str,
    arguments: dict,
    tool_adapter_fn: Callable | None,
    binding_context: dict,
) -> tuple[ToolInvocationBinding, dict]:
    binding = ToolInvocationBinding(
        binding_id=new_id("tb"),
        step_id=step.step_id,
        run_id=step.run_id or "",
        tool_name=tool_name,
        caller_role=step.assigned_role,
        requested_effect=arguments.get("effect", "read"),
        arguments_summary=str(arguments)[:200],
        dispatch_status="PENDING",
        idempotency_key=f"tool-{step.step_id}-{tool_name}",
    )

    if not _check_tool_allowed(step, tool_name):
        binding.dispatch_status = "BLOCKED"
        binding.errors.append(f"Tool {tool_name} not allowed for step role {step.assigned_role}")
        return binding, {"status": "BLOCKED", "error": binding.errors[-1]}

    if tool_adapter_fn is None:
        binding.dispatch_status = "BLOCKED"
        binding.errors.append("Tool adapter unavailable")
        return binding, {"status": "BLOCKED", "error": binding.errors[-1]}

    try:
        result = tool_adapter_fn(
            tool_name=tool_name,
            arguments=arguments,
            step_id=step.step_id,
            run_id=step.run_id,
        )
        binding.dispatch_status = "COMPLETED"
        return binding, result
    except Exception as e:
        binding.dispatch_status = "FAILED"
        binding.errors.append(str(e))
        return binding, {"status": "FAILED", "error": str(e)}
