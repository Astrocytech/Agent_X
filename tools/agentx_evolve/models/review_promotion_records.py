"""ReviewRecord and PromotionRecord dataclasses.

Item 7.1/7.2: Real review and promotion records with full
field sets as specified in sections 7.1 and 7.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class ReviewRecord:
    review_id: str
    reviewer_role: str
    proposal_id: str
    patch_candidate_id: str
    validation_evidence_id: str
    decision: str  # approved | rejected | needs_changes
    timestamp: str = ""
    reason: str = ""
    limits_or_conditions: list[str] = field(default_factory=list)
    rollback_reference: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PromotionRecord:
    promotion_id: str
    reviewed_candidate_id: str
    source_diff_id: str
    validation_result_ids: list[str] = field(default_factory=list)
    evidence_manifest_id: str = ""
    review_decision_id: str = ""
    promotion_decision: str = "promoted"  # promoted | rejected | deferred
    timestamp: str = ""
    reason: str = ""
    rollback_status: str = "not_needed"  # not_needed | success | failed
    remaining_known_limitations: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
