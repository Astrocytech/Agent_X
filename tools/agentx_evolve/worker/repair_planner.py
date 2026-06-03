from __future__ import annotations

from typing import Any

__all__ = [
    "plan_repair",
]


def plan_repair(failure_info: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_id": "",
        "failure_type": failure_info.get("failure_type", "UNKNOWN"),
        "description": failure_info.get("message", ""),
        "repair_steps": [],
        "status": "planned",
    }
