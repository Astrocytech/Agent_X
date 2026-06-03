from __future__ import annotations

from agentx_evolve.recovery.failure_models import (
    FailureRecord,
    SafeModeTrigger,
    SEVERITY_CRITICAL,
    TRIGGER_ROLLBACK_FAILED,
    TRIGGER_SOURCE_GUARD_FAILED,
    TRIGGER_UNEXPECTED_FILE_MUTATION,
    TRIGGER_POLICY_MISSING,
    TRIGGER_CAPABILITY_REGISTRY_MISSING,
    TRIGGER_SCHEMA_REPEATED_FAILURE,
    TRIGGER_LOCK_CORRUPTION,
    TRIGGER_GOVERNANCE_ARTIFACT_MISSING,
    TRIGGER_UNKNOWN_CRITICAL_FAILURE,
    make_safe_mode_trigger,
)

SAFE_MODE_TRIGGER_MAP: dict[str, str] = {
    "ROLLBACK_FAILED": TRIGGER_ROLLBACK_FAILED,
    "SOURCE_GUARD_FAILED": TRIGGER_SOURCE_GUARD_FAILED,
    "UNEXPECTED_FILE_MUTATION": TRIGGER_UNEXPECTED_FILE_MUTATION,
    "PATH_TRAVERSAL": TRIGGER_UNKNOWN_CRITICAL_FAILURE,
    "SYMLINK_ESCAPE": TRIGGER_UNKNOWN_CRITICAL_FAILURE,
    "L0_WRITE_BLOCKED": TRIGGER_UNKNOWN_CRITICAL_FAILURE,
}

REQUIRED_SAFE_MODE_CLASSES: set[str] = {
    "ROLLBACK_FAILED",
    "SOURCE_GUARD_FAILED",
    "UNEXPECTED_FILE_MUTATION",
    "POLICY_MISSING",
    "CAPABILITY_REGISTRY_MISSING",
    "LOCK_CORRUPTION",
    "GOVERNANCE_ARTIFACT_MISSING",
    "UNKNOWN_CRITICAL_FAILURE",
}


def requires_safe_mode(failure: FailureRecord, context: dict | None = None) -> bool:
    if failure.failure_class in SAFE_MODE_TRIGGER_MAP:
        return True

    if failure.failure_class == "UNKNOWN_FAILURE" and failure.severity == SEVERITY_CRITICAL:
        return True

    ctx = context or {}
    if failure.failure_class == "POLICY_MISSING":
        return True
    if failure.failure_class == "CAPABILITY_REGISTRY_MISSING":
        return True
    if failure.failure_class == "LOCK_CORRUPTION":
        return True
    if failure.failure_class == "GOVERNANCE_ARTIFACT_MISSING":
        return True
    if (
        failure.failure_class == "SCHEMA_VALIDATION_FAILED"
        and ctx.get("schema_repeated_failure")
    ):
        return True

    if failure.requires_safe_mode:
        return True

    return False


def get_safe_mode_trigger_type(failure: FailureRecord, context: dict | None = None) -> str | None:
    if not requires_safe_mode(failure, context):
        return None

    if failure.failure_class in SAFE_MODE_TRIGGER_MAP:
        return SAFE_MODE_TRIGGER_MAP[failure.failure_class]

    if failure.failure_class == "UNKNOWN_FAILURE" and failure.severity == SEVERITY_CRITICAL:
        return TRIGGER_UNKNOWN_CRITICAL_FAILURE

    if failure.failure_class == "POLICY_MISSING":
        return TRIGGER_POLICY_MISSING
    if failure.failure_class == "CAPABILITY_REGISTRY_MISSING":
        return TRIGGER_CAPABILITY_REGISTRY_MISSING
    if failure.failure_class == "LOCK_CORRUPTION":
        return TRIGGER_LOCK_CORRUPTION
    if failure.failure_class == "GOVERNANCE_ARTIFACT_MISSING":
        return TRIGGER_GOVERNANCE_ARTIFACT_MISSING

    ctx = context or {}
    if failure.failure_class == "SCHEMA_VALIDATION_FAILED" and ctx.get("schema_repeated_failure"):
        return TRIGGER_SCHEMA_REPEATED_FAILURE

    return TRIGGER_UNKNOWN_CRITICAL_FAILURE


def build_safe_mode_trigger(failure: FailureRecord, reason: str) -> SafeModeTrigger:
    trigger_type = get_safe_mode_trigger_type(failure) or TRIGGER_UNKNOWN_CRITICAL_FAILURE
    return make_safe_mode_trigger(
        failure_id=failure.failure_id,
        trigger_type=trigger_type,
        reason=reason,
    )
