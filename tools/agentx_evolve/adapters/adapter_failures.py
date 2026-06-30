from __future__ import annotations

FAILURE_CLASSES = [
    "model_timeout",
    "model_refusal",
    "model_schema_error",
    "model_provider_error",
    "tool_timeout",
    "tool_denied",
    "tool_schema_error",
    "tool_execution_error",
    "mcp_descriptor_error",
    "mcp_transport_error",
    "evidence_normalization_error",
    "live_provider_disabled",
    "secret_missing",
    "replay_artifact_missing",
    "adapter_not_registered",
    "capability_mismatch",
    "context_contamination",
    "prompt_injection_detected",
    "budget_exceeded",
]

ADAPTER_FAILURE_CLASSES = set(FAILURE_CLASSES)

OUTCOME_BLOCKED = "BLOCKED"
OUTCOME_RETRYABLE = "RETRYABLE_FAILURE"
OUTCOME_DENIED = "DENIED"
OUTCOME_ESCALATE = "ESCALATE"


def failure_outcome(failure_class: str) -> str:
    mapping = {
        "model_timeout": OUTCOME_RETRYABLE,
        "model_refusal": OUTCOME_BLOCKED,
        "model_schema_error": OUTCOME_DENIED,
        "model_provider_error": OUTCOME_RETRYABLE,
        "tool_timeout": OUTCOME_RETRYABLE,
        "tool_denied": OUTCOME_DENIED,
        "tool_schema_error": OUTCOME_DENIED,
        "tool_execution_error": OUTCOME_BLOCKED,
        "mcp_descriptor_error": OUTCOME_DENIED,
        "mcp_transport_error": OUTCOME_DENIED,
        "evidence_normalization_error": OUTCOME_BLOCKED,
        "live_provider_disabled": OUTCOME_BLOCKED,
        "secret_missing": OUTCOME_BLOCKED,
        "replay_artifact_missing": OUTCOME_DENIED,
        "adapter_not_registered": OUTCOME_DENIED,
        "capability_mismatch": OUTCOME_DENIED,
        "context_contamination": OUTCOME_ESCALATE,
        "prompt_injection_detected": OUTCOME_ESCALATE,
        "budget_exceeded": OUTCOME_DENIED,
    }
    return mapping.get(failure_class, OUTCOME_BLOCKED)


class FailureClass:
    def __init__(self, failure_class: str, reason: str = ""):
        if failure_class not in ADAPTER_FAILURE_CLASSES:
            raise ValueError(f"unknown failure class: {failure_class}")
        self.failure_class = failure_class
        self.reason = reason
        self.outcome = failure_outcome(failure_class)

    def to_dict(self) -> dict[str, str]:
        return {"failure_class": self.failure_class, "reason": self.reason, "outcome": self.outcome}
