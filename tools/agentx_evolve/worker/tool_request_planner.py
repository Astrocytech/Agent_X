from __future__ import annotations

from typing import Any

__all__ = [
    "plan_tool_requests",
]


def plan_tool_requests(task_context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "tool": tool,
            "reason": f"Need to use {tool} for task",
        }
        for tool in task_context.get("required_tools", [])
    ]
