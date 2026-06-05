from __future__ import annotations

from agentx_evolve.recovery.failure_models import (
    FailureRecord,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
    make_failure_record,
    utc_now_iso,
)

REQUIRED_FAILURE_CLASSES: set[str] = {
    "MODEL_INVALID_OUTPUT",
    "MODEL_INSUFFICIENT_CONTEXT",
    "PATCH_APPLY_FAILED",
    "VALIDATION_FAILED",
    "GOVERNANCE_BLOCKED",
    "RISK_TOO_HIGH",
    "SOURCE_GUARD_FAILED",
    "ROLLBACK_FAILED",
    "SCHEMA_VALIDATION_FAILED",
    "TOOL_FAILURE",
    "LOCK_CONFLICT",
    "ATOMIC_WRITE_FAILED",
    "PROMPT_CONTRACT_FAILED",
    "POLICY_DENIED",
    "CAPABILITY_MISSING",
    "ROLE_NOT_AUTHORIZED",
    "TOOL_NOT_ALLOWED",
    "MODEL_NOT_ALLOWED",
    "PATH_NOT_ALLOWED",
    "NETWORK_MODE_DENIED",
    "APPROVAL_REQUIRED",
    "PATH_TRAVERSAL",
    "PATH_OUTSIDE_REPO",
    "SYMLINK_ESCAPE",
    "L0_WRITE_BLOCKED",
    "PROTECTED_PATH_BLOCKED",
    "SOURCE_WRITE_DISABLED",
    "RUNTIME_WRITE_BOUNDARY_VIOLATION",
    "SUBPROCESS_BLOCKED",
    "COMMAND_NOT_ALLOWLISTED",
    "NETWORK_BLOCKED",
    "SECRET_REDACTION_FAILED",
    "UNEXPECTED_FILE_MUTATION",
    "IMPLEMENTATION_SESSION_FAILED",
    "UNKNOWN_FAILURE",
}

DEFAULT_SEVERITY_BY_FAILURE_CLASS: dict[str, str] = {
    "MODEL_INVALID_OUTPUT": SEVERITY_LOW,
    "MODEL_INSUFFICIENT_CONTEXT": SEVERITY_LOW,
    "PATCH_APPLY_FAILED": SEVERITY_HIGH,
    "VALIDATION_FAILED": SEVERITY_MEDIUM,
    "GOVERNANCE_BLOCKED": SEVERITY_HIGH,
    "RISK_TOO_HIGH": SEVERITY_HIGH,
    "SOURCE_GUARD_FAILED": SEVERITY_CRITICAL,
    "ROLLBACK_FAILED": SEVERITY_CRITICAL,
    "SCHEMA_VALIDATION_FAILED": SEVERITY_MEDIUM,
    "TOOL_FAILURE": SEVERITY_MEDIUM,
    "LOCK_CONFLICT": SEVERITY_MEDIUM,
    "ATOMIC_WRITE_FAILED": SEVERITY_HIGH,
    "PROMPT_CONTRACT_FAILED": SEVERITY_MEDIUM,
    "POLICY_DENIED": SEVERITY_HIGH,
    "CAPABILITY_MISSING": SEVERITY_HIGH,
    "ROLE_NOT_AUTHORIZED": SEVERITY_HIGH,
    "TOOL_NOT_ALLOWED": SEVERITY_MEDIUM,
    "MODEL_NOT_ALLOWED": SEVERITY_MEDIUM,
    "PATH_NOT_ALLOWED": SEVERITY_MEDIUM,
    "NETWORK_MODE_DENIED": SEVERITY_HIGH,
    "APPROVAL_REQUIRED": SEVERITY_MEDIUM,
    "PATH_TRAVERSAL": SEVERITY_CRITICAL,
    "PATH_OUTSIDE_REPO": SEVERITY_CRITICAL,
    "SYMLINK_ESCAPE": SEVERITY_CRITICAL,
    "L0_WRITE_BLOCKED": SEVERITY_CRITICAL,
    "PROTECTED_PATH_BLOCKED": SEVERITY_CRITICAL,
    "SOURCE_WRITE_DISABLED": SEVERITY_HIGH,
    "RUNTIME_WRITE_BOUNDARY_VIOLATION": SEVERITY_HIGH,
    "SUBPROCESS_BLOCKED": SEVERITY_HIGH,
    "COMMAND_NOT_ALLOWLISTED": SEVERITY_MEDIUM,
    "NETWORK_BLOCKED": SEVERITY_HIGH,
    "SECRET_REDACTION_FAILED": SEVERITY_CRITICAL,
    "UNEXPECTED_FILE_MUTATION": SEVERITY_CRITICAL,
    "IMPLEMENTATION_SESSION_FAILED": SEVERITY_HIGH,
    "UNKNOWN_FAILURE": SEVERITY_HIGH,
}

CRITICAL_CLASSES: set[str] = {
    fc for fc, sev in DEFAULT_SEVERITY_BY_FAILURE_CLASS.items() if sev == SEVERITY_CRITICAL
}


def is_known_failure_class(failure_class: str) -> bool:
    return failure_class in REQUIRED_FAILURE_CLASSES


def normalize_failure_class(failure_class: str | None) -> str:
    if not failure_class:
        return "UNKNOWN_FAILURE"
    fc = failure_class.strip().upper().replace(" ", "_")
    if fc in REQUIRED_FAILURE_CLASSES:
        return fc
    return "UNKNOWN_FAILURE"


def get_failure_severity(failure_class: str, context: dict | None = None) -> str:
    ctx = context or {}
    normalized = normalize_failure_class(failure_class)
    severity = DEFAULT_SEVERITY_BY_FAILURE_CLASS.get(normalized, SEVERITY_HIGH)

    if normalized == "UNKNOWN_FAILURE" and ctx.get("mutation_state_unknown"):
        severity = SEVERITY_CRITICAL

    return severity


def classify_failure(raw_failure: dict) -> FailureRecord:
    if raw_failure is None or not isinstance(raw_failure, dict):
        return make_failure_record(
            failure_class="UNKNOWN_FAILURE",
            message="Malformed failure input: expected dict",
            severity=SEVERITY_HIGH,
        )

    failure_class = normalize_failure_class(raw_failure.get("failure_class"))
    context = raw_failure.get("context", {})
    if not isinstance(context, dict):
        context = {}

    severity = get_failure_severity(failure_class, context)
    message = raw_failure.get("message") or f"Failure: {failure_class}"
    source_component = raw_failure.get("source_component") or "unknown"
    source_layer = raw_failure.get("source_layer") or "unknown"
    details = raw_failure.get("details") or {}
    if not isinstance(details, dict):
        details = {}
    input_artifact_refs = raw_failure.get("input_artifact_refs") or []
    if not isinstance(input_artifact_refs, list):
        input_artifact_refs = []
    related_artifact_refs = raw_failure.get("related_artifact_refs") or []
    if not isinstance(related_artifact_refs, list):
        related_artifact_refs = []

    is_unknown = failure_class == "UNKNOWN_FAILURE"
    is_critical = severity == SEVERITY_CRITICAL

    return FailureRecord(
        failure_id=raw_failure.get("failure_id", ""),
        timestamp=utc_now_iso(),
        source_component=source_component,
        source_layer=source_layer,
        session_id=raw_failure.get("session_id"),
        operation=raw_failure.get("operation"),
        failure_class=failure_class,
        severity=severity,
        message=message,
        details=details,
        input_artifact_refs=input_artifact_refs,
        related_artifact_refs=related_artifact_refs,
        requires_recovery=True,
        requires_safe_mode=is_critical or is_unknown,
        requires_human_review=is_unknown or is_critical,
        retryable=(not is_critical and not is_unknown),
        rollback_required=(failure_class in ("PATCH_APPLY_FAILED", "SOURCE_GUARD_FAILED", "ROLLBACK_FAILED")),
    )
