"""Structured diagnostics module.

Item 27 (22.1): Diagnostic records explaining why governed
flows succeeded or failed.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DiagnosticSeverity(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DiagnosticCode(Enum):
    POLICY_DENIAL = "POLICY_DENIAL"
    FORBIDDEN_PATH = "FORBIDDEN_PATH"
    MALFORMED_PATCH = "MALFORMED_PATCH"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    MISSING_ARTIFACT = "MISSING_ARTIFACT"
    STALE_LOCK = "STALE_LOCK"
    COMMAND_TIMEOUT = "COMMAND_TIMEOUT"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    ROLLBACK_FAILURE = "ROLLBACK_FAILURE"
    REVIEW_REJECTION = "REVIEW_REJECTION"
    PROMOTION_REJECTION = "PROMOTION_REJECTION"
    REPLAY_MISMATCH = "REPLAY_MISMATCH"
    PLACEHOLDER_HASH = "PLACEHOLDER_HASH"
    PROVENANCE_GAP = "PROVENANCE_GAP"
    PATCH_REJECTION = "PATCH_REJECTION"
    WEAK_ARTIFACT = "WEAK_ARTIFACT"
    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    BENCHMARK_FAILURE = "BENCHMARK_FAILURE"


@dataclass
class DiagnosticRecord:
    diagnostic_code: str
    severity: str
    component: str
    related_artifact_id: str = ""
    related_event_id: str = ""
    explanation: str = ""
    recommended_recovery: str = ""
    timestamp: str = ""
    internal_detail: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_diagnostic(code: DiagnosticCode | str, component: str,
                       explanation: str = "",
                       artifact_id: str = "",
                       event_id: str = "",
                       recovery: str = "",
                       detail: str = "") -> DiagnosticRecord:
    if isinstance(code, DiagnosticCode):
        code_str = code.value
        severity = _default_severity(code)
    else:
        code_str = code
        severity = "error"

    return DiagnosticRecord(
        diagnostic_code=code_str,
        severity=severity,
        component=component,
        related_artifact_id=artifact_id,
        related_event_id=event_id,
        explanation=explanation or f"{code_str} in {component}",
        recommended_recovery=recovery,
        internal_detail=detail,
    )


def _default_severity(code: DiagnosticCode) -> str:
    mapping = {
        DiagnosticCode.POLICY_DENIAL: "warning",
        DiagnosticCode.FORBIDDEN_PATH: "error",
        DiagnosticCode.MALFORMED_PATCH: "error",
        DiagnosticCode.SCHEMA_MISMATCH: "error",
        DiagnosticCode.MISSING_ARTIFACT: "warning",
        DiagnosticCode.STALE_LOCK: "warning",
        DiagnosticCode.COMMAND_TIMEOUT: "error",
        DiagnosticCode.PROVIDER_FAILURE: "error",
        DiagnosticCode.ROLLBACK_FAILURE: "critical",
        DiagnosticCode.REVIEW_REJECTION: "info",
        DiagnosticCode.PROMOTION_REJECTION: "info",
        DiagnosticCode.REPLAY_MISMATCH: "warning",
        DiagnosticCode.PLACEHOLDER_HASH: "error",
        DiagnosticCode.PROVENANCE_GAP: "error",
        DiagnosticCode.PATCH_REJECTION: "warning",
        DiagnosticCode.WEAK_ARTIFACT: "warning",
        DiagnosticCode.MISSING_PROVENANCE: "error",
        DiagnosticCode.BENCHMARK_FAILURE: "error",
    }
    return mapping.get(code, "error")


class DiagnosticLogger:
    def __init__(self):
        self._records: list[DiagnosticRecord] = []

    def log(self, record: DiagnosticRecord) -> None:
        self._records.append(record)

    def get_all(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self._records]

    def get_by_component(self, component: str) -> list[DiagnosticRecord]:
        return [r for r in self._records if r.component == component]

    def get_by_severity(self, severity: str) -> list[DiagnosticRecord]:
        return [r for r in self._records if r.severity == severity]

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self._records:
            counts[r.diagnostic_code] = counts.get(r.diagnostic_code, 0) + 1
        return counts
