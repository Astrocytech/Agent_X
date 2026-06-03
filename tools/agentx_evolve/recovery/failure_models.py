from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

SPEC_SCHEMA_VERSION = "1.0"
SOURCE_COMPONENT = "FailureRecovery"

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

DECISION_RECOVERABLE = "RECOVERABLE"
DECISION_NON_RECOVERABLE = "NON_RECOVERABLE"
DECISION_BLOCKED = "BLOCKED"
DECISION_SAFE_MODE_REQUIRED = "SAFE_MODE_REQUIRED"
DECISION_HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"

ACTION_RETRY = "RETRY"
ACTION_REBUILD_CONTEXT = "REBUILD_CONTEXT"
ACTION_ROLLBACK = "ROLLBACK"
ACTION_BLOCK_SESSION = "BLOCK_SESSION"
ACTION_ENTER_SAFE_MODE = "ENTER_SAFE_MODE"
ACTION_REQUEST_HUMAN_REVIEW = "REQUEST_HUMAN_REVIEW"
ACTION_REJECT_OUTPUT = "REJECT_OUTPUT"
ACTION_REVALIDATE = "REVALIDATE"
ACTION_NO_ACTION = "NO_ACTION"

ACTION_STATUS_PROPOSED = "PROPOSED"
ACTION_STATUS_STARTED = "STARTED"
ACTION_STATUS_COMPLETED = "COMPLETED"
ACTION_STATUS_FAILED = "FAILED"
ACTION_STATUS_BLOCKED = "BLOCKED"

TRIGGER_ROLLBACK_FAILED = "ROLLBACK_FAILED"
TRIGGER_SOURCE_GUARD_FAILED = "SOURCE_GUARD_FAILED"
TRIGGER_UNEXPECTED_FILE_MUTATION = "UNEXPECTED_FILE_MUTATION"
TRIGGER_POLICY_MISSING = "POLICY_MISSING"
TRIGGER_CAPABILITY_REGISTRY_MISSING = "CAPABILITY_REGISTRY_MISSING"
TRIGGER_SCHEMA_REPEATED_FAILURE = "SCHEMA_REPEATED_FAILURE"
TRIGGER_LOCK_CORRUPTION = "LOCK_CORRUPTION"
TRIGGER_GOVERNANCE_ARTIFACT_MISSING = "GOVERNANCE_ARTIFACT_MISSING"
TRIGGER_UNKNOWN_CRITICAL_FAILURE = "UNKNOWN_CRITICAL_FAILURE"

RECOVERY_EVENT_TYPES = [
    "FAILURE_CLASSIFIED",
    "RECOVERY_DECIDED",
    "RECOVERY_ACTION_PROPOSED",
    "SAFE_MODE_TRIGGERED",
    "RECOVERY_COMPLETED",
    "RECOVERY_FAILED",
    "RECOVERY_BLOCKED",
]

CONTEXT_DEFAULTS = {
    "mutation_started": False,
    "validation_failed_after_mutation": False,
    "mutation_state_unknown": False,
    "retry_count": 0,
    "max_retries": 1,
    "rollback_available": False,
    "policy_registry_available": False,
    "governed_patch_execution_available": False,
    "initiator_artifacts_available": False,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, Path):
                result[f] = str(val)
            elif isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


@dataclass
class FailureRecord:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "failure_record.schema.json"
    failure_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    source_layer: str = ""
    session_id: str | None = None
    operation: str | None = None
    failure_class: str = ""
    severity: str = SEVERITY_MEDIUM
    message: str = ""
    details: dict = field(default_factory=dict)
    input_artifact_refs: list[str] = field(default_factory=list)
    related_artifact_refs: list[str] = field(default_factory=list)
    requires_recovery: bool = True
    requires_safe_mode: bool = False
    requires_human_review: bool = False
    retryable: bool = False
    rollback_required: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RecoveryAction:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "recovery_action.schema.json"
    recovery_action_id: str = ""
    timestamp: str = ""
    failure_id: str = ""
    action_type: str = ACTION_NO_ACTION
    action_status: str = ACTION_STATUS_PROPOSED
    reason: str = ""
    executor_component: str | None = None
    max_attempts: int = 1
    attempt_number: int = 0
    preconditions: list[str] = field(default_factory=list)
    expected_result: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RecoveryDecision:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "recovery_decision.schema.json"
    recovery_decision_id: str = ""
    timestamp: str = ""
    failure_id: str = ""
    decision: str = DECISION_BLOCKED
    selected_actions: list[dict] = field(default_factory=list)
    reason: str = ""
    policy_rule_ids: list[str] = field(default_factory=list)
    safe_mode_required: bool = False
    human_review_required: bool = False
    rollback_required: bool = False
    retry_allowed: bool = False
    continue_session_allowed: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class SafeModeTrigger:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "safe_mode_trigger.schema.json"
    safe_mode_trigger_id: str = ""
    timestamp: str = ""
    failure_id: str = ""
    trigger_type: str = TRIGGER_UNKNOWN_CRITICAL_FAILURE
    reason: str = ""
    required_actions: list[str] = field(default_factory=list)
    system_state: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def make_failure_record(
    failure_class: str,
    message: str = "",
    source_component: str = SOURCE_COMPONENT,
    source_layer: str = "",
    session_id: str | None = None,
    operation: str | None = None,
    severity: str = SEVERITY_MEDIUM,
    details: dict | None = None,
) -> FailureRecord:
    return FailureRecord(
        failure_id=new_id("fail_"),
        timestamp=utc_now_iso(),
        source_component=source_component,
        source_layer=source_layer,
        session_id=session_id,
        operation=operation,
        failure_class=failure_class,
        severity=severity,
        message=message or f"Failure: {failure_class}",
        details=details or {},
    )


def make_recovery_action(
    failure_id: str,
    action_type: str,
    reason: str = "",
    executor_component: str | None = None,
    max_attempts: int = 1,
) -> RecoveryAction:
    return RecoveryAction(
        recovery_action_id=new_id("recact_"),
        timestamp=utc_now_iso(),
        failure_id=failure_id,
        action_type=action_type,
        action_status=ACTION_STATUS_PROPOSED,
        reason=reason,
        executor_component=executor_component,
        max_attempts=max_attempts,
    )


def make_recovery_decision(
    failure_id: str,
    decision: str = DECISION_BLOCKED,
    reason: str = "",
) -> RecoveryDecision:
    return RecoveryDecision(
        recovery_decision_id=new_id("recdec_"),
        timestamp=utc_now_iso(),
        failure_id=failure_id,
        decision=decision,
        reason=reason,
    )


def make_safe_mode_trigger(
    failure_id: str,
    trigger_type: str,
    reason: str = "",
) -> SafeModeTrigger:
    return SafeModeTrigger(
        safe_mode_trigger_id=new_id("safemode_"),
        timestamp=utc_now_iso(),
        failure_id=failure_id,
        trigger_type=trigger_type,
        reason=reason,
    )
