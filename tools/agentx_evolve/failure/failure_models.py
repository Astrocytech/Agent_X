from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

CAT_PATH_BOUNDARY = "PATH_BOUNDARY_VIOLATION"
CAT_GOVERNANCE_BLOCKED = "GOVERNANCE_BLOCKED"
CAT_VALIDATION_FAILED = "VALIDATION_FAILED"
CAT_SUBPROCESS_BLOCKED = "SUBPROCESS_BLOCKED"
CAT_NETWORK_BLOCKED = "NETWORK_BLOCKED"
CAT_SANDBOX_VIOLATION = "SANDBOX_VIOLATION"
CAT_POLICY_BLOCKED = "POLICY_BLOCKED"
CAT_PATCH_APPLY_FAILED = "PATCH_APPLY_FAILED"
CAT_ROLLBACK_FAILED = "ROLLBACK_FAILED"
CAT_INTERNAL_ERROR = "INTERNAL_ERROR"

SEV_LOW = "low"
SEV_MEDIUM = "medium"
SEV_HIGH = "high"
SEV_CRITICAL = "critical"

ACTION_RETRY = "RETRY"
ACTION_ROLLBACK = "ROLLBACK"
ACTION_ESCALATE = "ESCALATE"
ACTION_REPROPOSE = "REPROPOSE"
ACTION_ADJUST_POLICY = "ADJUST_POLICY"
ACTION_SKIP = "SKIP"
ACTION_REVIEW = "REVIEW"

ALL_CATEGORIES = [
    CAT_PATH_BOUNDARY, CAT_GOVERNANCE_BLOCKED, CAT_VALIDATION_FAILED,
    CAT_SUBPROCESS_BLOCKED, CAT_NETWORK_BLOCKED, CAT_SANDBOX_VIOLATION,
    CAT_POLICY_BLOCKED, CAT_PATCH_APPLY_FAILED, CAT_ROLLBACK_FAILED,
    CAT_INTERNAL_ERROR,
]

ALL_SEVERITIES = [SEV_LOW, SEV_MEDIUM, SEV_HIGH, SEV_CRITICAL]

ALL_ACTIONS = [
    ACTION_RETRY, ACTION_ROLLBACK, ACTION_ESCALATE,
    ACTION_REPROPOSE, ACTION_ADJUST_POLICY, ACTION_SKIP, ACTION_REVIEW,
]


class FailureCategory(Enum):
    PATH_BOUNDARY_VIOLATION = CAT_PATH_BOUNDARY
    GOVERNANCE_BLOCKED = CAT_GOVERNANCE_BLOCKED
    VALIDATION_FAILED = CAT_VALIDATION_FAILED
    SUBPROCESS_BLOCKED = CAT_SUBPROCESS_BLOCKED
    NETWORK_BLOCKED = CAT_NETWORK_BLOCKED
    SANDBOX_VIOLATION = CAT_SANDBOX_VIOLATION
    POLICY_BLOCKED = CAT_POLICY_BLOCKED
    PATCH_APPLY_FAILED = CAT_PATCH_APPLY_FAILED
    ROLLBACK_FAILED = CAT_ROLLBACK_FAILED
    INTERNAL_ERROR = CAT_INTERNAL_ERROR


class FailureSeverity(Enum):
    LOW = SEV_LOW
    MEDIUM = SEV_MEDIUM
    HIGH = SEV_HIGH
    CRITICAL = SEV_CRITICAL


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def to_dict(obj: object) -> dict:
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if hasattr(val, "__dataclass_fields__"):
                result[f] = to_dict(val)
            elif isinstance(val, list):
                result[f] = [
                    to_dict(v) if hasattr(v, "__dataclass_fields__") else v
                    for v in val
                ]
            elif isinstance(val, dict):
                result[f] = {
                    k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v
                    for k, v in val.items()
                }
            elif isinstance(val, Enum):
                result[f] = val.value
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) for v in obj]
    return obj


@dataclass
class RecoveryAction:
    schema_version: str = "1.0"
    schema_id: str = "recovery_action.schema.json"
    action_id: str = ""
    timestamp: str = ""
    action_type: str = ACTION_RETRY
    description: str = ""
    command: list[str] = field(default_factory=list)
    requires_approval: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class RecoveryPlaybook:
    schema_version: str = "1.0"
    schema_id: str = "recovery_playbook.schema.json"
    playbook_id: str = ""
    timestamp: str = ""
    failure_category: str = ""
    severity: str = SEV_MEDIUM
    description: str = ""
    suggested_actions: list[RecoveryAction] = field(default_factory=list)
    auto_recoverable: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class FailureEvent:
    schema_version: str = "1.0"
    schema_id: str = "failure_event.schema.json"
    event_id: str = ""
    timestamp: str = ""
    session_id: str = ""
    category: str = CAT_INTERNAL_ERROR
    severity: str = SEV_MEDIUM
    source_component: str = ""
    summary: str = ""
    details: dict = field(default_factory=dict)
    suggested_action: str = ACTION_REVIEW
    recovery_action_id: str | None = None
    recovered: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class FailureReport:
    schema_version: str = "1.0"
    schema_id: str = "failure_report.schema.json"
    report_id: str = ""
    timestamp: str = ""
    session_id: str = ""
    events: list[FailureEvent] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = to_dict(self)
        d["events"] = [e.to_dict() for e in self.events]
        return d

    def add_event(self, event: FailureEvent) -> FailureEvent:
        self.events.append(event)
        return event

    def event_count(self) -> int:
        return len(self.events)

    def events_by_category(self, category: str) -> list[FailureEvent]:
        return [e for e in self.events if e.category == category]

    def events_by_severity(self, severity: str) -> list[FailureEvent]:
        return [e for e in self.events if e.severity == severity]

    def highest_severity(self) -> str:
        if not self.events:
            return SEV_LOW
        levels = {SEV_LOW: 0, SEV_MEDIUM: 1, SEV_HIGH: 2, SEV_CRITICAL: 3}
        highest = max(
            self.events, key=lambda e: levels.get(e.severity, 0)
        )
        return highest.severity

    def unrecovered_count(self) -> int:
        return sum(1 for e in self.events if not e.recovered)

    def generate_summary(self) -> dict:
        counts = {cat: 0 for cat in ALL_CATEGORIES}
        for e in self.events:
            counts[e.category] = counts.get(e.category, 0) + 1
        self.summary = {
            "total_events": self.event_count(),
            "unrecovered": self.unrecovered_count(),
            "highest_severity": self.highest_severity(),
            "by_category": {k: v for k, v in counts.items() if v > 0},
        }
        return self.summary
