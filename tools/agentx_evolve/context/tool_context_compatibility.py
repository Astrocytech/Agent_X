from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import TaskInput, ContextPack


def check_tool_context_compatibility(
    task_input: TaskInput,
    context_pack: ContextPack,
    tool_registry: dict | None = None,
    policy_context: dict | None = None,
) -> dict[str, Any]:
    if tool_registry is None:
        tool_registry = {}
    if policy_context is None:
        policy_context = {}

    allowed: list[str] = []
    blocked: list[str] = []
    results: list[dict] = []

    for tool_name in task_input.requested_tools:
        tool_def = tool_registry.get(tool_name, {})
        if not tool_def:
            results.append({
                "tool_name": tool_name,
                "allowed": False,
                "reason": "unknown tool — not in registry",
            })
            blocked.append(tool_name)
            continue

        tool_type = tool_def.get("tool_type", "UNKNOWN")
        if tool_type == "MUTATING" and not tool_def.get("governance_approved", False):
            results.append({
                "tool_name": tool_name,
                "allowed": False,
                "reason": "mutating tool requires governance approval",
            })
            blocked.append(tool_name)
            continue

        if tool_def.get("requires_human_approval", False) and not tool_def.get("approval_id"):
            results.append({
                "tool_name": tool_name,
                "allowed": False,
                "reason": "tool requires human approval but no approval_id provided",
            })
            blocked.append(tool_name)
            continue

        results.append({
            "tool_name": tool_name,
            "allowed": True,
            "reason": "tool is allowed",
        })
        allowed.append(tool_name)

    return {
        "allowed_tools": allowed,
        "blocked_tools": blocked,
        "results": results,
        "tool_registry_available": bool(tool_registry),
    }
