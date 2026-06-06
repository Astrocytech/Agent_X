from __future__ import annotations

from typing import Any

__all__ = [
    "ApprovalValidator",
]


class ApprovalValidator:
    def validate(self, approval: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not approval.get("approval_id"):
            errors.append("Missing approval_id")
        if not approval.get("status"):
            errors.append("Missing status")
        if not approval.get("reviewer"):
            errors.append("Missing reviewer")
        if not approval.get("scope"):
            errors.append("Missing scope")
        return errors
