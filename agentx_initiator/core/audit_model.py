from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class AuditEvent:
    schema_version: str = "1.0"
    event_id: str = ""
    timestamp: str = ""
    category: str = "SYSTEM"
    component: str = ""
    event_type: str = ""
    status: str = "INFO"
    summary: str = ""
    input_refs: list[str] = field(default_factory=list)
    output_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    previous_event_hash: Optional[str] = None
    event_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> AuditEvent:
        return cls(
            schema_version=d.get("schema_version", "1.0"),
            event_id=d.get("event_id", ""),
            timestamp=d.get("timestamp", ""),
            category=d.get("category", "SYSTEM"),
            component=d.get("component", ""),
            event_type=d.get("event_type", ""),
            status=d.get("status", "INFO"),
            summary=d.get("summary", d.get("detail", "")),
            input_refs=d.get("input_refs", []),
            output_refs=d.get("output_refs", []),
            artifact_refs=d.get("artifact_refs", []),
            evidence_ids=d.get("evidence_ids", []),
            previous_event_hash=d.get("previous_event_hash"),
            event_hash=d.get("event_hash"),
        )


@dataclass
class AuditEvidence:
    evidence_id: str = ""
    source_path: str = ""
    source_artifact: str = ""
    detection_rule: str = ""
    supports: str = ""
    confidence: str = "HIGH"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditAppendResult:
    status: str = "SUCCESS"
    event_id: str = ""
    event_hash: Optional[str] = None
    warning: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
