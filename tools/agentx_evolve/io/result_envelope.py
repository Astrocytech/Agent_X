from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALID_STATUSES = {"PASS", "FAIL", "BLOCKED", "UNKNOWN"}
VALID_RECORD_TYPES: set[str] = set()
SCHEMA_VERSION = "1.0.0"


@dataclass
class MvpResultEnvelope:
    schema_version: str = SCHEMA_VERSION
    run_id: str = ""
    producer_id: str = ""
    consumer_id: str | None = None
    record_type: str = ""
    status: str = "UNKNOWN"
    payload: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    created_at: str = ""

    def validate(self) -> list[str]:
        issues = []
        if self.schema_version != SCHEMA_VERSION:
            issues.append(f"Invalid schema_version: {self.schema_version}")
        if not self.run_id:
            issues.append("run_id is required")
        if not self.producer_id:
            issues.append("producer_id is required")
        if not self.record_type:
            issues.append("record_type is required")
        elif VALID_RECORD_TYPES and self.record_type not in VALID_RECORD_TYPES:
            issues.append(f"Unknown record_type: {self.record_type}")
        if self.status not in VALID_STATUSES:
            issues.append(f"Invalid status: {self.status}")
        if self.status == "PASS" and self.errors:
            issues.append("Cannot have PASS status with errors")
        if self.warnings and self.status == "PASS":
            issues.append("Warnings present with PASS status")
        return issues

    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "producer_id": self.producer_id,
            "consumer_id": self.consumer_id,
            "record_type": self.record_type,
            "status": self.status,
            "payload": self.payload,
            "errors": self.errors,
            "warnings": self.warnings,
            "evidence_refs": self.evidence_refs,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MvpResultEnvelope:
        return cls(
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            run_id=data.get("run_id", ""),
            producer_id=data.get("producer_id", ""),
            consumer_id=data.get("consumer_id"),
            record_type=data.get("record_type", ""),
            status=data.get("status", "UNKNOWN"),
            payload=data.get("payload", {}),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            evidence_refs=data.get("evidence_refs", []),
            created_at=data.get("created_at", ""),
        )


def register_record_type(rt: str) -> None:
    VALID_RECORD_TYPES.add(rt)


def validate_envelope(data: dict) -> tuple[bool, list[str]]:
    env = MvpResultEnvelope.from_dict(data)
    issues = env.validate()
    return len(issues) == 0, issues
