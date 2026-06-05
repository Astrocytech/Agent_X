from __future__ import annotations

from agentx_evolve.recovery.failure_models import (
    FailureRecord,
    RecoveryAction,
    SEVERITY_CRITICAL,
    ACTION_RETRY,
    ACTION_REBUILD_CONTEXT,
    ACTION_ROLLBACK,
    ACTION_BLOCK_SESSION,
    ACTION_ENTER_SAFE_MODE,
    ACTION_REQUEST_HUMAN_REVIEW,
    ACTION_REJECT_OUTPUT,
    ACTION_REVALIDATE,
    make_recovery_action,
    CONTEXT_DEFAULTS,
)
from agentx_evolve.recovery.recovery_playbook import FAILURE_TO_RULE_MAP


def _get_context_value(context: dict | None, key: str) -> bool | int:
    if context is None:
        return CONTEXT_DEFAULTS.get(key, False)
    return context.get(key, CONTEXT_DEFAULTS.get(key, False))


def select_recovery_actions(
    failure: FailureRecord,
    context: dict | None = None,
) -> list[RecoveryAction]:
    fc = failure.failure_class
    mutation_started = _get_context_value(context, "mutation_started")
    retry_count = _get_context_value(context, "retry_count")
    max_retries = _get_context_value(context, "max_retries")
    rollback_available = _get_context_value(context, "rollback_available")
    is_critical = failure.severity == SEVERITY_CRITICAL

    if is_critical:
        actions: list[RecoveryAction] = []
        sm = make_recovery_action(failure.failure_id, ACTION_ENTER_SAFE_MODE, reason="Critical failure requires safe mode")
        actions.append(sm)
        hr = make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason="Critical failure requires human review")
        actions.append(hr)
        bs = make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Critical failure blocks session")
        actions.append(bs)
        return actions

    if fc == "MODEL_INVALID_OUTPUT":
        return [
            make_recovery_action(failure.failure_id, ACTION_REJECT_OUTPUT, reason="Model output invalid"),
            make_recovery_action(failure.failure_id, ACTION_RETRY, reason="Retry model call", max_attempts=max_retries),
        ]

    if fc == "MODEL_INSUFFICIENT_CONTEXT":
        return [
            make_recovery_action(failure.failure_id, ACTION_REBUILD_CONTEXT, reason="Model context insufficient"),
        ]

    if fc == "PATCH_APPLY_FAILED":
        if mutation_started:
            if rollback_available:
                return [make_recovery_action(failure.failure_id, ACTION_ROLLBACK, reason="Patch apply failed after mutation")]


        return [make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Patch apply failed")]

    if fc == "VALIDATION_FAILED":
        if _get_context_value(context, "validation_failed_after_mutation"):
            if rollback_available:
                return [make_recovery_action(failure.failure_id, ACTION_ROLLBACK, reason="Validation failed after mutation")]
        return [make_recovery_action(failure.failure_id, ACTION_REVALIDATE, reason="Validation failed")]

    if fc == "GOVERNANCE_BLOCKED":
        return [make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Governance blocked")]

    if fc == "RISK_TOO_HIGH":
        return [
            make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason="Risk too high"),
            make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Risk too high blocks session"),
        ]

    if fc == "SOURCE_GUARD_FAILED":
        actions = [make_recovery_action(failure.failure_id, ACTION_ROLLBACK, reason="Source guard failed")]
        actions.append(make_recovery_action(failure.failure_id, ACTION_ENTER_SAFE_MODE, reason="Source guard failed requires safe mode"))
        actions.append(make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason="Source guard failed requires review"))
        return actions

    if fc == "ROLLBACK_FAILED":
        return [
            make_recovery_action(failure.failure_id, ACTION_ENTER_SAFE_MODE, reason="Rollback failed"),
            make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason="Rollback failed requires review"),
        ]

    if fc == "SCHEMA_VALIDATION_FAILED":
        return [
            make_recovery_action(failure.failure_id, ACTION_REJECT_OUTPUT, reason="Schema validation failed"),
            make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Schema validation blocks session"),
        ]

    if fc == "TOOL_FAILURE":
        if retry_count < max_retries:
            return [make_recovery_action(failure.failure_id, ACTION_RETRY, reason="Retry tool call", max_attempts=max_retries)]
        return [make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Tool failure max retries exceeded")]

    if fc == "LOCK_CONFLICT":
        return [make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Lock conflict")]

    if fc == "ATOMIC_WRITE_FAILED":
        actions = [make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Atomic write failed")]
        actions.append(make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason="Atomic write failed may need review"))
        return actions

    if fc == "PROMPT_CONTRACT_FAILED":
        return [make_recovery_action(failure.failure_id, ACTION_REJECT_OUTPUT, reason="Prompt contract failed")]

    if fc in ("POLICY_DENIED", "CAPABILITY_MISSING", "ROLE_NOT_AUTHORIZED", "PATH_NOT_ALLOWED", "NETWORK_MODE_DENIED", "APPROVAL_REQUIRED"):
        return [make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason=f"{fc}: policy blocks session")]

    if fc in ("PATH_TRAVERSAL", "PATH_OUTSIDE_REPO", "SYMLINK_ESCAPE", "L0_WRITE_BLOCKED", "PROTECTED_PATH_BLOCKED",
              "SOURCE_WRITE_DISABLED", "RUNTIME_WRITE_BOUNDARY_VIOLATION", "SUBPROCESS_BLOCKED",
              "COMMAND_NOT_ALLOWLISTED", "NETWORK_BLOCKED", "UNEXPECTED_FILE_MUTATION"):
        return [
            make_recovery_action(failure.failure_id, ACTION_ENTER_SAFE_MODE, reason=f"{fc}: requires safe mode"),
            make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason=f"{fc}: requires human review"),
        ]

    if fc == "SECRET_REDACTION_FAILED":
        return [
            make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Secret redaction failed"),
            make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason="Secret redaction requires review"),
        ]

    if fc == "IMPLEMENTATION_SESSION_FAILED":
        return [make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason="Implementation session failed")]

    return [
        make_recovery_action(failure.failure_id, ACTION_REQUEST_HUMAN_REVIEW, reason=f"Unknown failure: {fc}"),
        make_recovery_action(failure.failure_id, ACTION_BLOCK_SESSION, reason=f"Unknown failure blocks session: {fc}"),
    ]
