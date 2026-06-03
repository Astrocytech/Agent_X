from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict

PR_IMPLEMENTED_UNVALIDATED = "IMPLEMENTED_UNVALIDATED"
PR_VALIDATED_LOCAL = "VALIDATED_LOCAL"
PR_REVIEWED = "REVIEWED"
PR_PROMOTION_READY = "PROMOTION_READY"
PR_PROMOTED = "PROMOTED"
PR_REJECTED = "REJECTED"
PR_ROLLED_BACK = "ROLLED_BACK"
ALL_PROMOTION_STATUSES = [
    PR_IMPLEMENTED_UNVALIDATED, PR_VALIDATED_LOCAL, PR_REVIEWED,
    PR_PROMOTION_READY, PR_PROMOTED, PR_REJECTED, PR_ROLLED_BACK,
]

PC_PROMOTE_READY = "PROMOTE_READY"
PC_PROMOTE_BLOCKED = "PROMOTE_BLOCKED"
PC_PROMOTE_NEEDS_REVIEW = "PROMOTE_NEEDS_REVIEW"
ALL_PROMOTION_CHECK_RESULTS = [PC_PROMOTE_READY, PC_PROMOTE_BLOCKED, PC_PROMOTE_NEEDS_REVIEW]


@dataclass
class PromotionCheckResult:
    decision: str = PC_PROMOTE_BLOCKED
    reason: str = ""
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PromotionRecord:
    promotion_id: str = ""
    session_id: str = ""
    status: str = PR_IMPLEMENTED_UNVALIDATED
    check_result: PromotionCheckResult | None = None
    promoted_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class PromotionGate:
    def __init__(self):
        self._records: dict[str, PromotionRecord] = {}

    def check(self, session_id: str,
              governance_allowed: bool = True,
              risk_acceptable: bool = True,
              validation_passed: bool = True,
              source_guard_passed: bool = True,
              no_forbidden_paths: bool = True,
              completion_evidence_exists: bool = True,
              rollback_available: bool = True,
              human_approval_present: bool = True,
              ) -> PromotionCheckResult:
        result = PromotionCheckResult()
        checks = {
            "governance_allowed": governance_allowed,
            "risk_acceptable": risk_acceptable,
            "validation_passed": validation_passed,
            "source_guard_passed": source_guard_passed,
            "no_forbidden_paths": no_forbidden_paths,
            "completion_evidence_exists": completion_evidence_exists,
            "rollback_available": rollback_available,
            "human_approval_present": human_approval_present,
        }
        for name, passed in checks.items():
            if passed:
                result.checks_passed.append(name)
            else:
                result.checks_failed.append(name)

        if not result.checks_failed:
            result.decision = PC_PROMOTE_READY
            result.reason = "All checks passed"
        elif any(not checks.get(c, True) for c in
                 ("governance_allowed", "source_guard_passed", "completion_evidence_exists")):
            result.decision = PC_PROMOTE_BLOCKED
            result.reason = "Critical checks failed"
        else:
            result.decision = PC_PROMOTE_NEEDS_REVIEW
            result.reason = "Non-critical checks failed, review required"

        record = PromotionRecord(
            promotion_id=new_id("promo"),
            session_id=session_id,
            check_result=result,
        )
        self._records[session_id] = record
        return result

    def get_record(self, session_id: str) -> PromotionRecord | None:
        return self._records.get(session_id)

    def list_records(self) -> list[PromotionRecord]:
        return list(self._records.values())
