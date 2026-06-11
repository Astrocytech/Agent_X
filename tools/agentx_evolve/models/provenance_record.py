from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

ORIGIN_PRE_EXISTING = "pre_existing"
ORIGIN_STAGE_A = "stage_a_infrastructure"
ORIGIN_STAGE_B = "stage_b_generated"
ORIGIN_MANUAL = "manual"
ORIGIN_UNKNOWN = "unknown"
ALL_ORIGINS = {ORIGIN_PRE_EXISTING, ORIGIN_STAGE_A, ORIGIN_STAGE_B, ORIGIN_MANUAL, ORIGIN_UNKNOWN}

PERSISTENCE_PERMANENT = "permanent"
PERSISTENCE_EPHEMERAL = "ephemeral"
ALL_PERSISTENCE = {PERSISTENCE_PERMANENT, PERSISTENCE_EPHEMERAL}

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_UNKNOWN = "UNKNOWN"
ALL_STATUSES = {STATUS_PASS, STATUS_FAIL, STATUS_UNKNOWN}

SCHEMA_VERSION = "1.0"
SCHEMA_ID = "provenance_record.schema.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_id(prefix: str = "PR") -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


@dataclass
class ProvenanceRecord:
    path: str
    sha256: str
    origin: str = ORIGIN_UNKNOWN
    status: str = STATUS_PASS
    stage: str = ""
    persistence: str = PERSISTENCE_PERMANENT
    provenance_id: str = ""
    schema_version: str = SCHEMA_VERSION
    schema_id: str = SCHEMA_ID
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.provenance_id:
            self.provenance_id = _new_id("PR")
        if not self.created_at:
            self.created_at = _utc_now_iso()
        if self.origin not in ALL_ORIGINS:
            raise ValueError(f"Invalid origin: {self.origin!r}. Must be one of {ALL_ORIGINS}")
        if self.persistence not in ALL_PERSISTENCE:
            raise ValueError(f"Invalid persistence: {self.persistence!r}. Must be one of {ALL_PERSISTENCE}")
        if self.status not in ALL_STATUSES:
            raise ValueError(f"Invalid status: {self.status!r}. Must be one of {ALL_STATUSES}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceRecord:
        return cls(**data)


@dataclass
class ProvenanceChain:
    records: list[ProvenanceRecord] = field(default_factory=list)
    chain_id: str = ""
    source_diff_ref: str = ""
    rollback_plan_ref: str = ""
    governance_artifact_refs: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.chain_id:
            self.chain_id = _new_id("CHAIN")

    def append(self, record: ProvenanceRecord) -> None:
        self.records.append(record)

    def extend(self, records: list[ProvenanceRecord]) -> None:
        self.records.extend(records)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "record_count": len(self.records),
            "records": [r.to_dict() for r in self.records],
            "source_diff_ref": self.source_diff_ref,
            "rollback_plan_ref": self.rollback_plan_ref,
            "governance_artifact_refs": self.governance_artifact_refs,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceChain:
        records = [ProvenanceRecord.from_dict(r) for r in data.get("records", [])]
        return cls(
            records=records,
            chain_id=data.get("chain_id", ""),
            source_diff_ref=data.get("source_diff_ref", ""),
            rollback_plan_ref=data.get("rollback_plan_ref", ""),
            governance_artifact_refs=data.get("governance_artifact_refs", {}),
        )
