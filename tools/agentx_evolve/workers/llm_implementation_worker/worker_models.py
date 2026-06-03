from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_BLOCKED,
    MODE_RESTRICTED,
    DEP_NOT_CHECKED,
    SCHEMA_VERSION,
    SOURCE_COMPONENT,
    DEFAULT_MAX_CONTEXT_CHARS,
    DEFAULT_MAX_MODEL_OUTPUT_CHARS,
    DEFAULT_TEMPERATURE,
    ALL_WORKER_STATUSES,
    ALL_WORKER_MODES,
    ALL_DEPENDENCY_STATUSES,
    ALL_PATCH_FORMATS,
    ALL_HANDOFF_STATUSES,
    ALL_MODEL_RESPONSE_STATUSES,
    HANDOFF_STATUS_PENDING,
    PATCH_FORMAT_STRUCTURED_FILE_CHANGE_LIST,
    MODEL_RESPONSE_STATUS_SUCCESS,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    ALL_WORKER_FAILURE_CLASSES,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{ts}"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def sha256_dict(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return dict(obj)


def compute_self_hash(data: dict, self_hash_field: str = "evidence_manifest_sha256") -> str:
    canonical = {k: v for k, v in data.items() if k != self_hash_field}
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def redact_secret_like(value: str) -> str:
    secret_indicators = [
        "sk-", "pk-", "api_key", "apikey", "api-key",
        "token", "secret", "password", "credential",
        "-----BEGIN", "-----END",
    ]
    if any(indicator.lower() in value.lower() for indicator in secret_indicators):
        return "[REDACTED]"
    return value


@dataclass
class LLMWorkerTask:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_task.schema.json"
    task_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    requested_by: str = ""
    caller_role: str = ""
    session_id: str | None = None
    worker_mode: str = MODE_RESTRICTED
    implementation_goal: str = ""
    target_component_id: str = ""
    target_files: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    available_context_refs: list[str] = field(default_factory=list)
    model_profile_id: str | None = None
    tool_policy_context_id: str | None = None
    patch_session_id: str | None = None
    dry_run: bool = True
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS
    max_model_output_chars: int = DEFAULT_MAX_MODEL_OUTPUT_CHARS
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class DependencyStatus:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_dependency_status.schema.json"
    dependency_status_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str | None = None
    model_adapter: str = DEP_NOT_CHECKED
    tool_adapter: str = DEP_NOT_CHECKED
    policy_registry: str = DEP_NOT_CHECKED
    failure_taxonomy: str = DEP_NOT_CHECKED
    governed_patch_execution: str = DEP_NOT_CHECKED
    restricted_mode: bool = True
    allowed_modes: list[str] = field(default_factory=list)
    blocked_capabilities: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_restricted(self) -> bool:
        return self.restricted_mode

    def can_call_model(self) -> bool:
        return self.model_adapter == "AVAILABLE" and not self.restricted_mode

    def can_use_tools(self) -> bool:
        return self.tool_adapter == "AVAILABLE" and not self.restricted_mode

    def can_handoff_patch(self) -> bool:
        return self.governed_patch_execution == "AVAILABLE" and not self.restricted_mode


@dataclass
class LLMWorkerContextPackage:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_context_package.schema.json"
    context_package_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    included_files: list[str] = field(default_factory=list)
    excluded_files: list[str] = field(default_factory=list)
    included_artifact_refs: list[str] = field(default_factory=list)
    context_summary: str = ""
    context_chunks: list[dict] = field(default_factory=list)
    redaction_report: dict = field(default_factory=dict)
    truncation_report: dict = field(default_factory=dict)
    prompt_injection_report: dict = field(default_factory=dict)
    context_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def total_chars(self) -> int:
        return sum(len(str(c)) for c in self.context_chunks)


@dataclass
class LLMWorkerPromptPackage:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_prompt_package.schema.json"
    prompt_package_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    context_package_id: str = ""
    system_contract: str = ""
    developer_contract: str = ""
    task_prompt: str = ""
    output_schema_instruction: str = ""
    forbidden_actions: list[str] = field(default_factory=list)
    required_output_sections: list[str] = field(default_factory=list)
    prompt_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LLMWorkerModelRequest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_model_request.schema.json"
    model_request_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    model_profile_id: str = ""
    prompt_package_id: str = ""
    requested_capability: str = ""
    max_output_chars: int = DEFAULT_MAX_MODEL_OUTPUT_CHARS
    temperature: float | None = DEFAULT_TEMPERATURE
    deterministic: bool = True
    policy_decision_id: str | None = None
    model_request_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LLMWorkerModelResponse:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_model_response.schema.json"
    model_response_id: str = ""
    created_at: str = ""
    source_component: str = "ModelAdapter"
    task_id: str = ""
    model_request_id: str = ""
    status: str = MODEL_RESPONSE_STATUS_SUCCESS
    raw_response_ref: str | None = None
    safe_summary: str = ""
    parsed_output_ref: str | None = None
    usage_summary: dict = field(default_factory=dict)
    failure_class: str | None = None
    model_response_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_success(self) -> bool:
        return self.status == MODEL_RESPONSE_STATUS_SUCCESS


@dataclass
class ParsedModelOutput:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_model_output.schema.json"
    parsed_output_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    model_response_id: str = ""
    implementation_summary: str = ""
    implementation_plan: dict = field(default_factory=dict)
    files_to_change: list[str] = field(default_factory=list)
    schemas_to_change: list[str] = field(default_factory=list)
    tests_to_change: list[str] = field(default_factory=list)
    patch_proposal: dict | None = None
    validation_handoff: dict | None = None
    risk_notes: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    rejected_content: list[dict] = field(default_factory=list)
    parsed_output_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ImplementationPlan:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_implementation_plan.schema.json"
    plan_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    target_component_id: str = ""
    steps: list[dict] = field(default_factory=list)
    files_expected_to_change: list[str] = field(default_factory=list)
    schemas_expected_to_change: list[str] = field(default_factory=list)
    tests_expected_to_change: list[str] = field(default_factory=list)
    risk_notes: list[str] = field(default_factory=list)
    required_authorities: list[str] = field(default_factory=list)
    validation_commands: list[str] = field(default_factory=list)
    acceptance_criteria_mapping: list[dict] = field(default_factory=list)
    implementation_plan_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PatchProposal:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_patch_proposal.schema.json"
    patch_proposal_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    plan_id: str = ""
    patch_format: str = PATCH_FORMAT_STRUCTURED_FILE_CHANGE_LIST
    target_files: list[str] = field(default_factory=list)
    proposed_changes: list[dict] = field(default_factory=list)
    diff_ref: str | None = None
    governed_patch_request_ref: str | None = None
    rationale: str = ""
    requires_governance: bool = True
    requires_human_approval: bool = True
    handoff_status: str = HANDOFF_STATUS_PENDING
    patch_proposal_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ValidationHandoff:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_validation_handoff.schema.json"
    validation_handoff_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    plan_id: str = ""
    patch_proposal_id: str | None = None
    validation_commands: list[str] = field(default_factory=list)
    expected_artifacts: list[str] = field(default_factory=list)
    tool_requests: list[dict] = field(default_factory=list)
    handoff_target: str = "ToolAdapter"
    dry_run: bool = True
    validation_handoff_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class LLMWorkerResult:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_result.schema.json"
    worker_result_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    status: str = WORKER_BLOCKED
    message: str = ""
    worker_mode: str = MODE_RESTRICTED
    implementation_plan_id: str | None = None
    patch_proposal_id: str | None = None
    validation_handoff_id: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    failure_class: str | None = None
    worker_result_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_success(self) -> bool:
        return self.status == "SUCCESS"

    def is_blocked(self) -> bool:
        return self.status in ("BLOCKED", "FAILED", "INVALID")


@dataclass
class LLMWorkerAuditEvent:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "llm_worker_audit.schema.json"
    audit_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    task_id: str | None = None
    status: str = ""
    message: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
