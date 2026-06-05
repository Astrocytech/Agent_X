from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

SPEC_SCHEMA_VERSION = "1.0"
SOURCE_COMPONENT = "ModelAdapter"
POLICY_SOURCE_COMPONENT = "ModelPolicy"
REGISTRY_SOURCE_COMPONENT = "ModelRegistry"

TASK_IMPLEMENT_PATCH = "IMPLEMENT_PATCH"
TASK_FIX_VALIDATION = "FIX_VALIDATION"
TASK_WRITE_TEST = "WRITE_TEST"
TASK_EXPLAIN_FAILURE = "EXPLAIN_FAILURE"
TASK_SUMMARIZE_CONTEXT = "SUMMARIZE_CONTEXT"
TASK_CLASSIFY_FAILURE = "CLASSIFY_FAILURE"
TASK_GENERATE_PLAN = "GENERATE_PLAN"
TASK_REVIEW_OUTPUT = "REVIEW_OUTPUT"
TASK_DRY_RUN = "DRY_RUN"
TASK_REPAIR_JSON = "REPAIR_JSON"

PROVIDER_FAKE = "FAKE"
PROVIDER_LOCAL = "LOCAL"
PROVIDER_OLLAMA = "OLLAMA"
PROVIDER_LMSTUDIO = "LMSTUDIO"
PROVIDER_OPENAI_COMPATIBLE = "OPENAI_COMPATIBLE"
PROVIDER_OPENCODE_COMPATIBLE = "OPENCODE_COMPATIBLE"
PROVIDER_HOSTED = "HOSTED"
PROVIDER_DISABLED = "DISABLED"

MODEL_STATUS_SUCCESS = "SUCCESS"
MODEL_STATUS_PARTIAL = "PARTIAL"
MODEL_STATUS_BLOCKED = "BLOCKED"
MODEL_STATUS_FAILED = "FAILED"
MODEL_STATUS_INVALID = "INVALID"
MODEL_STATUS_RETRYABLE = "RETRYABLE"

POLICY_ALLOW = "ALLOW"
POLICY_BLOCK = "BLOCK"
POLICY_NEEDS_REDACTION = "NEEDS_REDACTION"
POLICY_NEEDS_SMALLER_CONTEXT = "NEEDS_SMALLER_CONTEXT"
POLICY_NEEDS_LOCAL_RUNTIME = "NEEDS_LOCAL_RUNTIME"
POLICY_NEEDS_HOSTED_PROVIDER_APPROVAL = "NEEDS_HOSTED_PROVIDER_APPROVAL"

SELECTION_ALLOW = "ALLOW"
SELECTION_BLOCK = "BLOCK"
SELECTION_NEEDS_RUNTIME_PROFILE = "NEEDS_RUNTIME_PROFILE"
SELECTION_NEEDS_HOSTED_PROVIDER_APPROVAL = "NEEDS_HOSTED_PROVIDER_APPROVAL"
SELECTION_NEEDS_CONTEXT_REDUCTION = "NEEDS_CONTEXT_REDUCTION"

MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
MODEL_PROVIDER_UNAVAILABLE = "MODEL_PROVIDER_UNAVAILABLE"
MODEL_POLICY_DENIED = "MODEL_POLICY_DENIED"
MODEL_CONTEXT_TOO_LARGE = "MODEL_CONTEXT_TOO_LARGE"
MODEL_SECRET_DETECTED = "MODEL_SECRET_DETECTED"
MODEL_REQUEST_INVALID = "MODEL_REQUEST_INVALID"
MODEL_RESPONSE_INVALID = "MODEL_RESPONSE_INVALID"
MODEL_JSON_INVALID = "MODEL_JSON_INVALID"
MODEL_SCHEMA_INVALID = "MODEL_SCHEMA_INVALID"
MODEL_TIMEOUT = "MODEL_TIMEOUT"
MODEL_RETRY_EXHAUSTED = "MODEL_RETRY_EXHAUSTED"
MODEL_PROVIDER_ERROR = "MODEL_PROVIDER_ERROR"
MODEL_OUTPUT_TRUNCATED = "MODEL_OUTPUT_TRUNCATED"
MODEL_HOSTED_NOT_ALLOWED = "MODEL_HOSTED_NOT_ALLOWED"
MODEL_NETWORK_NOT_ALLOWED = "MODEL_NETWORK_NOT_ALLOWED"
MODEL_DIRECT_ACTION_BLOCKED = "MODEL_DIRECT_ACTION_BLOCKED"
UNKNOWN_MODEL_FAILURE = "UNKNOWN_MODEL_FAILURE"

CAPABILITY_SMALL_FAST = "SMALL_FAST"
CAPABILITY_SMALL_CODER = "SMALL_CODER"
CAPABILITY_MEDIUM_CODER_OPTIONAL = "MEDIUM_CODER_OPTIONAL"
CAPABILITY_HOSTED_FALLBACK_OPTIONAL = "HOSTED_FALLBACK_OPTIONAL"
CAPABILITY_TEST_DOUBLE = "TEST_DOUBLE"

TRANSPORT_NONE = "NONE"
TRANSPORT_TEST_DOUBLE = "TEST_DOUBLE"
TRANSPORT_LOCAL_IN_PROCESS = "LOCAL_IN_PROCESS"
TRANSPORT_LOCAL_HTTP_LOOPBACK = "LOCAL_HTTP_LOOPBACK"
TRANSPORT_HOSTED_HTTPS_APPROVED = "HOSTED_HTTPS_APPROVED"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}{uuid4().hex}"
    return uuid4().hex


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, type):
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


ALL_TASK_TYPES = {
    TASK_IMPLEMENT_PATCH,
    TASK_FIX_VALIDATION,
    TASK_WRITE_TEST,
    TASK_EXPLAIN_FAILURE,
    TASK_SUMMARIZE_CONTEXT,
    TASK_CLASSIFY_FAILURE,
    TASK_GENERATE_PLAN,
    TASK_REVIEW_OUTPUT,
    TASK_DRY_RUN,
    TASK_REPAIR_JSON,
}

ALL_PROVIDER_KINDS = {
    PROVIDER_FAKE,
    PROVIDER_LOCAL,
    PROVIDER_OLLAMA,
    PROVIDER_LMSTUDIO,
    PROVIDER_OPENAI_COMPATIBLE,
    PROVIDER_OPENCODE_COMPATIBLE,
    PROVIDER_HOSTED,
    PROVIDER_DISABLED,
}

ALL_MODEL_STATUSES = {
    MODEL_STATUS_SUCCESS,
    MODEL_STATUS_PARTIAL,
    MODEL_STATUS_BLOCKED,
    MODEL_STATUS_FAILED,
    MODEL_STATUS_INVALID,
    MODEL_STATUS_RETRYABLE,
}

ALL_POLICY_DECISIONS = {
    POLICY_ALLOW,
    POLICY_BLOCK,
    POLICY_NEEDS_REDACTION,
    POLICY_NEEDS_SMALLER_CONTEXT,
    POLICY_NEEDS_LOCAL_RUNTIME,
    POLICY_NEEDS_HOSTED_PROVIDER_APPROVAL,
}

ALL_SELECTION_DECISIONS = {
    SELECTION_ALLOW,
    SELECTION_BLOCK,
    SELECTION_NEEDS_RUNTIME_PROFILE,
    SELECTION_NEEDS_HOSTED_PROVIDER_APPROVAL,
    SELECTION_NEEDS_CONTEXT_REDUCTION,
}

ALL_MODEL_FAILURE_CLASSES = {
    MODEL_NOT_FOUND,
    MODEL_PROVIDER_UNAVAILABLE,
    MODEL_POLICY_DENIED,
    MODEL_CONTEXT_TOO_LARGE,
    MODEL_SECRET_DETECTED,
    MODEL_REQUEST_INVALID,
    MODEL_RESPONSE_INVALID,
    MODEL_JSON_INVALID,
    MODEL_SCHEMA_INVALID,
    MODEL_TIMEOUT,
    MODEL_RETRY_EXHAUSTED,
    MODEL_PROVIDER_ERROR,
    MODEL_OUTPUT_TRUNCATED,
    MODEL_HOSTED_NOT_ALLOWED,
    MODEL_NETWORK_NOT_ALLOWED,
    MODEL_DIRECT_ACTION_BLOCKED,
    UNKNOWN_MODEL_FAILURE,
}

ALL_CAPABILITY_CLASSES = {
    CAPABILITY_SMALL_FAST,
    CAPABILITY_SMALL_CODER,
    CAPABILITY_MEDIUM_CODER_OPTIONAL,
    CAPABILITY_HOSTED_FALLBACK_OPTIONAL,
    CAPABILITY_TEST_DOUBLE,
}

ALL_TRANSPORT_MODES = {
    TRANSPORT_NONE,
    TRANSPORT_TEST_DOUBLE,
    TRANSPORT_LOCAL_IN_PROCESS,
    TRANSPORT_LOCAL_HTTP_LOOPBACK,
    TRANSPORT_HOSTED_HTTPS_APPROVED,
}

ROLE_ORCHESTRATOR = "ORCHESTRATOR"
ROLE_IMPLEMENTATION_WORKER = "IMPLEMENTATION_WORKER"
ROLE_VALIDATION_REPAIR_WORKER = "VALIDATION_REPAIR_WORKER"
ROLE_REVIEWER_ASSISTANT = "REVIEWER_ASSISTANT"
ROLE_PROMOTION_CHECKER = "PROMOTION_CHECKER"
ROLE_HUMAN_OPERATOR = "HUMAN_OPERATOR"
ROLE_UNKNOWN_CALLER = "UNKNOWN_CALLER"

ALL_ROLES = {
    ROLE_ORCHESTRATOR,
    ROLE_IMPLEMENTATION_WORKER,
    ROLE_VALIDATION_REPAIR_WORKER,
    ROLE_REVIEWER_ASSISTANT,
    ROLE_PROMOTION_CHECKER,
    ROLE_HUMAN_OPERATOR,
    ROLE_UNKNOWN_CALLER,
}


@dataclass
class ModelProfile:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_profile.schema.json"
    model_id: str = ""
    display_name: str = ""
    provider_id: str = ""
    capability_class: str = CAPABILITY_TEST_DOUBLE
    model_family: str = ""
    context_window: int = 4096
    max_output_tokens: int = 1024
    enabled: bool = True
    supports_json_only: bool = True
    supports_streaming: bool = False
    supports_tool_calling: bool = False
    write_source: bool = False
    runs_tools: bool = False
    runs_commands: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelProviderProfile:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_provider_profile.schema.json"
    provider_id: str = ""
    provider_type: str = PROVIDER_FAKE
    display_name: str = ""
    transport_mode: str = TRANSPORT_TEST_DOUBLE
    endpoint_allowlisted: bool = False
    credential_ref: str | None = None
    default_timeout_seconds: int = 60
    max_retries: int = 1
    local_only: bool = True
    network_allowed: bool = False
    hosted_fallback_allowed: bool = False
    enabled: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelCapabilityProfile:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_capability_profile.schema.json"
    capability_id: str = ""
    capability_class: str = CAPABILITY_TEST_DOUBLE
    description: str = ""
    supported_tasks: list[str] = field(default_factory=list)
    requires_json_output: bool = True
    requires_output_schema: bool = False
    max_context_window: int = 4096
    writes_source: bool = False
    runs_tools: bool = False
    runs_commands: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelRequest:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_request.schema.json"
    model_request_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    caller_role: str = ROLE_UNKNOWN_CALLER
    task_type: str = TASK_SUMMARIZE_CONTEXT
    model_id: str = ""
    provider_id: str = ""
    prompt: str = ""
    system_prompt: str = ""
    json_only: bool = True
    expected_output_schema_id: str | None = None
    context_budget_tokens: int = 4096
    max_output_tokens: int = 1024
    temperature: float = 0.0
    original_request_id: str | None = None
    retry_attempt: int = 0
    dry_run: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelResponse:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_response.schema.json"
    model_response_id: str = ""
    model_request_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    model_id: str = ""
    provider_id: str = ""
    status: str = MODEL_STATUS_BLOCKED
    message: str = ""
    raw_output: str = ""
    json_output: dict | None = None
    json_valid: bool = False
    schema_valid: bool = False
    prompt_hash: str = ""
    output_hash: str = ""
    failure_class: str | None = None
    token_count_input: int = 0
    token_count_output: int = 0
    latency_seconds: float = 0.0
    tool_call_suggestions: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelRegistry:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_registry.schema.json"
    registry_id: str = ""
    created_at: str = ""
    source_component: str = REGISTRY_SOURCE_COMPONENT
    models: list[ModelProfile] = field(default_factory=list)
    provider_profiles: list[ModelProviderProfile] = field(default_factory=list)
    capability_profiles: list[ModelCapabilityProfile] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelSelectionDecision:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_selection_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    task_type: str = ""
    selected_model_id: str | None = None
    selected_provider_id: str | None = None
    decision: str = SELECTION_BLOCK
    reason: str = ""
    alternatives: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelPolicyDecision:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_policy_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    source_component: str = POLICY_SOURCE_COMPONENT
    model_id: str = ""
    caller_role: str = ROLE_UNKNOWN_CALLER
    task_type: str = ""
    decision: str = POLICY_BLOCK
    reason: str = ""
    required_checks: list[str] = field(default_factory=list)
    missing_checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelRetryRecord:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_retry_record.schema.json"
    retry_id: str = ""
    original_request_id: str = ""
    model_request_id: str = ""
    model_response_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    attempt_number: int = 1
    retry_reason: str = ""
    decision: str = "RETRY"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelAuditEvent:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_audit.schema.json"
    audit_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    model_request_id: str | None = None
    model_response_id: str | None = None
    model_id: str | None = None
    provider_id: str | None = None
    status: str = ""
    message: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class InvalidModelRequestRecord:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "invalid_model_request.schema.json"
    record_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    model_id: str | None = None
    caller_role: str | None = None
    reason: str = ""
    failure_class: str = UNKNOWN_MODEL_FAILURE
    safe_request_summary: str = ""
    raw_request: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModelCallEvidence:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_call_evidence.schema.json"
    evidence_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    model_request_id: str = ""
    model_response_id: str = ""
    model_id: str = ""
    provider_id: str = ""
    prompt_hash: str = ""
    output_hash: str = ""
    status: str = ""
    token_count_input: int = 0
    token_count_output: int = 0
    latency_seconds: float = 0.0
    artifact_refs: list[str] = field(default_factory=list)
    failure_class: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
