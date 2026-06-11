from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RollbackResult:
    action_id: str = ""
    run_id: str = ""
    rollback_id: str = ""
    status: str = "recorded"
    evidence: list[dict] = field(default_factory=list)
    original_failure: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "run_id": self.run_id,
            "rollback_id": self.rollback_id,
            "status": self.status,
            "evidence": list(self.evidence),
            "original_failure": self.original_failure,
        }


class MvpRollbackController:
    def __init__(self) -> None:
        self._history: list[RollbackResult] = []

    def record_rollback(self, action_id: str, run_id: str, rollback_id: str,
                        original_failure: str = "") -> RollbackResult:
        result = RollbackResult(
            action_id=action_id,
            run_id=run_id,
            rollback_id=rollback_id,
            status="recorded",
            evidence=[{
                "event": "rollback_recorded",
                "action_id": action_id,
                "rollback_id": rollback_id,
            }],
            original_failure=original_failure,
        )
        self._history.append(result)
        return result

    def finalize(self, rollback_id: str, status: str = "completed",
                 evidence: list[dict] | None = None) -> RollbackResult | None:
        for r in self._history:
            if r.rollback_id == rollback_id:
                r.status = status
                if evidence:
                    r.evidence.extend(evidence)
                return r
        return None

    @property
    def history(self) -> list[RollbackResult]:
        return list(self._history)
