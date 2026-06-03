from __future__ import annotations
from agentx_evolve.failure.failure_models import (
    FailureEvent, FailureCategory, FailureSeverity,
    CAT_PATH_BOUNDARY, CAT_GOVERNANCE_BLOCKED, CAT_VALIDATION_FAILED,
    CAT_SUBPROCESS_BLOCKED, CAT_NETWORK_BLOCKED, CAT_SANDBOX_VIOLATION,
    CAT_POLICY_BLOCKED, CAT_PATCH_APPLY_FAILED, CAT_ROLLBACK_FAILED,
    CAT_INTERNAL_ERROR,
    SEV_LOW, SEV_MEDIUM, SEV_HIGH, SEV_CRITICAL,
    ACTION_RETRY, ACTION_ROLLBACK, ACTION_ESCALATE, ACTION_REPROPOSE,
    ACTION_ADJUST_POLICY, ACTION_SKIP, ACTION_REVIEW,
    new_id, utc_now_iso,
)


_CLASSIFIER_RULES: list[tuple[list[str], str, str, str]] = [
    # (patterns, category, suggested_action, severity)
    # Ordered most-specific first — first match wins to avoid generic overrides
    (["L0", "l0", "L0_BLOCK", "protected path", "path boundary"], CAT_PATH_BOUNDARY, ACTION_SKIP, SEV_MEDIUM),
    (["PATH_ESCAPE", "outside repository", "symlink escape"], CAT_PATH_BOUNDARY, ACTION_SKIP, SEV_HIGH),
    (["governance decision", "governance check", "Governance decision ID", "SOURCE_WRITE_DISABLED"], CAT_GOVERNANCE_BLOCKED, ACTION_REPROPOSE, SEV_MEDIUM),
    (["session ID", "implementation session ID", "Implementation session"], CAT_GOVERNANCE_BLOCKED, ACTION_REPROPOSE, SEV_MEDIUM),
    (["validation fail", "VALIDATION_FAILED", "Validation failed", "validation command"], CAT_VALIDATION_FAILED, ACTION_RETRY, SEV_MEDIUM),
    (["subprocess", "SUBPROCESS_BLOCKED", "Command not allowlisted", "blocked command"], CAT_SUBPROCESS_BLOCKED, ACTION_ADJUST_POLICY, SEV_HIGH),
    (["network", "NETWORK_BLOCKED", "Network not allowed", "Network not allowed by"], CAT_NETWORK_BLOCKED, ACTION_ADJUST_POLICY, SEV_LOW),
    (["sandbox", "SANDBOX_VIOLATION", "blocked by sandbox"], CAT_SANDBOX_VIOLATION, ACTION_ESCALATE, SEV_CRITICAL),
    (["not registered", "capability registry", "PolicyEnforcer"], CAT_POLICY_BLOCKED, ACTION_ADJUST_POLICY, SEV_HIGH),
    (["OLD_TEXT_NOT_FOUND", "MULTIPLE_MATCHES", "patch apply", "APPLYING"], CAT_PATCH_APPLY_FAILED, ACTION_REPROPOSE, SEV_MEDIUM),
    (["write error", "Write error", "Delete error", "File not found for deletion"], CAT_PATCH_APPLY_FAILED, ACTION_ROLLBACK, SEV_MEDIUM),
    (["rollback", "ROLLBACK_FAILED", "snapshot not found", "restore fail"], CAT_ROLLBACK_FAILED, ACTION_ESCALATE, SEV_CRITICAL),
    (["internal", "INTERNAL_ERROR", "unexpected"], CAT_INTERNAL_ERROR, ACTION_ESCALATE, SEV_CRITICAL),
]


class FailureClassifier:
    def classify(self, reason: str, source_component: str = "", session_id: str = "") -> FailureEvent:
        reason_lower = reason.lower()

        for patterns, category, suggested_action, severity in _CLASSIFIER_RULES:
            for pattern in patterns:
                if pattern.lower() in reason_lower:
                    break
            else:
                continue
            break
        else:
            category, suggested_action, severity = CAT_INTERNAL_ERROR, ACTION_ESCALATE, SEV_CRITICAL
        return FailureEvent(
            event_id=new_id("fail"),
            timestamp=utc_now_iso(),
            session_id=session_id,
            category=category,
            severity=severity,
            source_component=source_component or "FailureClassifier",
            summary=reason[:200],
            details={"original_reason": reason},
            suggested_action=suggested_action,
        )

    def classify_sandbox_decision(self, reason: str, session_id: str = "") -> FailureEvent:
        return self.classify(reason, "SecuritySandbox", session_id)

    def classify_governance_block(self, reason: str, session_id: str = "") -> FailureEvent:
        return self.classify(reason, "FileChangeGuard", session_id)

    def classify_validation_failure(self, reason: str, session_id: str = "") -> FailureEvent:
        return self.classify(reason, "ImplementationValidationGate", session_id)

    def classify_patch_failure(self, reason: str, session_id: str = "") -> FailureEvent:
        return self.classify(reason, "PatchApplier", session_id)

    def classify_rollback_failure(self, reason: str, session_id: str = "") -> FailureEvent:
        return self.classify(reason, "RollbackManager", session_id)

    def classify_policy_block(self, reason: str, session_id: str = "") -> FailureEvent:
        return self.classify(reason, "PolicyEnforcer", session_id)
