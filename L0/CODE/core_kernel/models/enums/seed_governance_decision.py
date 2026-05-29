from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SeedGovernanceDecision:
    allowed: bool = False
    requires_approval: bool = False
    reason: str = ""
    decision_id: str = ""
    risk_level: str = "unknown"
    allowed_by_policy: bool = False
    executable_now: bool = False
    approval_token_required: bool = False
    approval_token_id: str | None = None

    @staticmethod
    def _compute(
        allowed: bool,
        requires_approval: bool,
        reason: str = "",
        decision_id: str = "",
        risk_level: str = "unknown",
        **kwargs: Any,
    ) -> SeedGovernanceDecision:
        """Compute executable_now from allowed and requires_approval."""
        executable_now = allowed and not requires_approval
        return SeedGovernanceDecision(
            allowed=allowed,
            allowed_by_policy=allowed,
            requires_approval=requires_approval,
            executable_now=executable_now,
            approval_token_required=requires_approval,
            reason=reason,
            decision_id=decision_id,
            risk_level=risk_level,
        )
