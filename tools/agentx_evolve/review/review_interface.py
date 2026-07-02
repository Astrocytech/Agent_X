"""MvpReviewInterface — alongside existing HumanReviewInterface."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.models.model_models import new_id, to_dict

AD_PENDING = "PENDING"
AD_APPROVED = "APPROVED"
AD_REJECTED = "REJECTED"
ALL_APPROVAL_DECISIONS = [AD_PENDING, AD_APPROVED, AD_REJECTED]


@dataclass
class ApprovalRecord:
    approval_id: str = ""
    session_id: str = ""
    decision: str = AD_PENDING
    reviewer: str = ""
    reason: str = ""
    created_at: str = ""
    decided_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    conditions: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_decided(self) -> bool:
        return self.decision in (AD_APPROVED, AD_REJECTED)


@dataclass
class ReviewReport:
    session_id: str = ""
    task: str = ""
    proposal: str = ""
    governance_decision: str = ""
    risk_assessment: str = ""
    files_changed: list[str] = field(default_factory=list)
    diff_summary: str = ""
    validation_result: str = ""
    rollback_available: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    conditions: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class ApprovalHistory:
    def __init__(self):
        self._records: dict[str, ApprovalRecord] = {}

    def add(self, record: ApprovalRecord) -> None:
        self._records[record.approval_id] = record

    def get(self, approval_id: str) -> ApprovalRecord | None:
        return self._records.get(approval_id)

    def get_by_session(self, session_id: str) -> list[ApprovalRecord]:
        return [r for r in self._records.values() if r.session_id == session_id]

    def list_all(self) -> list[ApprovalRecord]:
        return list(self._records.values())

    def is_session_approved(self, session_id: str) -> bool:
        return any(
            r.session_id == session_id and r.decision == AD_APPROVED
            for r in self._records.values()
        )


class HumanReviewInterface:
    def __init__(self, history: ApprovalHistory | None = None):
        self._history = history or ApprovalHistory()

    @property
    def history(self) -> ApprovalHistory:
        return self._history

    def review(self, session_id: str, report: ReviewReport | None = None) -> ReviewReport:
        return report or ReviewReport(session_id=session_id)

    def approve(self, session_id: str, reviewer: str = "",
                reason: str = "") -> ApprovalRecord:
        record = ApprovalRecord(
            approval_id=new_id("apr"),
            session_id=session_id,
            decision=AD_APPROVED,
            reviewer=reviewer,
            reason=reason,
            created_at=datetime.now(timezone.utc).isoformat(),
            decided_at=datetime.now(timezone.utc).isoformat(),
        )
        self._history.add(record)
        return record

    def reject(self, session_id: str, reviewer: str = "",
               reason: str = "") -> ApprovalRecord:
        record = ApprovalRecord(
            approval_id=new_id("apr"),
            session_id=session_id,
            decision=AD_REJECTED,
            reviewer=reviewer,
            reason=reason,
            created_at=datetime.now(timezone.utc).isoformat(),
            decided_at=datetime.now(timezone.utc).isoformat(),
        )
        self._history.add(record)
        return record

    def is_approved(self, session_id: str) -> bool:
        return self._history.is_session_approved(session_id)


RCT_APPROVED = "APPROVED"
RCT_REJECTED = "REJECTED"
RCT_CHANGES_REQUESTED = "CHANGES_REQUESTED"


@dataclass
class MvpReviewPacket:
    review_id: str = ""
    action_id: str = ""
    run_id: str = ""
    reviewer_identity: str = ""
    decision: str = ""
    decision_reason: str = ""
    evidence_refs: list[dict] = field(default_factory=list)
    created_at: str = ""
    decided_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "action_id": self.action_id,
            "run_id": self.run_id,
            "reviewer_identity": self.reviewer_identity,
            "decision": self.decision,
            "decision_reason": self.decision_reason,
            "evidence_refs": self.evidence_refs,
            "created_at": self.created_at,
            "decided_at": self.decided_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MvpReviewPacket:
        return cls(
            review_id=data.get("review_id", ""),
            action_id=data.get("action_id", ""),
            run_id=data.get("run_id", ""),
            reviewer_identity=data.get("reviewer_identity", ""),
            decision=data.get("decision", ""),
            decision_reason=data.get("decision_reason", ""),
            evidence_refs=data.get("evidence_refs", []),
            created_at=data.get("created_at", ""),
            decided_at=data.get("decided_at", ""),
        )


    @staticmethod
    def _sha256_file(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _verify_evidence_hash(ref: dict) -> list[str]:
        path_str = ref.get("path", ref.get("ref", ""))
        expected_hash = ref.get("sha256", ref.get("hash", ""))
        if not path_str:
            return ["evidence_ref missing path"]
        p = Path(path_str)
        if not p.exists():
            return [f"evidence path {path_str} does not exist"]
        if expected_hash:
            actual = hashlib.sha256(p.read_bytes()).hexdigest()
            if actual != expected_hash:
                return [f"evidence hash mismatch for {path_str}: expected {expected_hash}, got {actual}"]
        return []


class MvpReviewInterface:
    def __init__(self) -> None:
        self._packets: dict[str, MvpReviewPacket] = {}

    def create_packet(self, packet: MvpReviewPacket) -> MvpReviewPacket:
        self._packets[packet.review_id] = packet
        return packet

    def record_decision(self, review_id: str, decision: str, reason: str,
                        reviewer: str, decided_at: str) -> MvpReviewPacket | None:
        packet = self._packets.get(review_id)
        if packet is None:
            return None
        if decision not in (RCT_APPROVED, RCT_REJECTED, RCT_CHANGES_REQUESTED):
            raise ValueError(f"Invalid decision: {decision}")
        # Verify evidence hashes before allowing approval
        if decision == RCT_APPROVED and packet.evidence_refs:
            hash_errors: list[str] = []
            for ref in packet.evidence_refs:
                hash_errors.extend(self._verify_evidence_hash(ref))
            if hash_errors:
                packet.decision = RCT_REJECTED
                packet.decision_reason = f"evidence hash verification failed: {'; '.join(hash_errors)}"
                packet.reviewer_identity = reviewer
                packet.decided_at = decided_at
                return packet
        packet.decision = decision
        packet.decision_reason = reason
        packet.reviewer_identity = reviewer
        packet.decided_at = decided_at
        return packet

    def get_packet(self, review_id: str) -> MvpReviewPacket | None:
        return self._packets.get(review_id)

    def is_finalized(self, review_id: str) -> bool:
        p = self._packets.get(review_id)
        return p is not None and p.decision in (RCT_APPROVED, RCT_REJECTED)

    def list_by_run(self, run_id: str) -> list[MvpReviewPacket]:
        return [p for p in self._packets.values() if p.run_id == run_id]

    def verify_evidence_binding(self, review_id: str) -> list[str]:
        packet = self._packets.get(review_id)
        if packet is None:
            return [f"review packet {review_id} not found"]
        errors: list[str] = []
        for ref in packet.evidence_refs:
            errors.extend(self._verify_evidence_hash(ref))
        return errors
