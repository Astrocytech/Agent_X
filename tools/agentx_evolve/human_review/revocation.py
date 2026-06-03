from __future__ import annotations

from typing import Any

from agentx_evolve.human_review.approval_revocation import revoke_approval as _revoke_approval

__all__ = [
    "revoke_approval",
]


def revoke_approval(approval_id: str, reason: str) -> dict[str, Any]:
    result = _revoke_approval(
        approval_decision_id=approval_id,
        revoked_by=None,
        reason=reason,
        repo_root=None,
    )
    return {
        "approval_id": approval_id,
        "reason": reason,
        "revocation_id": getattr(result, "revocation_id", ""),
        "status": "revoked",
    }
