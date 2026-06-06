from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

SPEC_SCHEMA_VERSION = "1.0"
SOURCE_COMPONENT = "ToolMCPAdapter"
POLICY_SOURCE_COMPONENT = "ToolPolicy"
INVALID_SOURCE_COMPONENT = "InvalidToolHandler"
REGISTRY_SOURCE_COMPONENT = "ToolRegistry"

TRUST_TIER_0_READ_ONLY = "TRUST_TIER_0_READ_ONLY"
TRUST_TIER_1_LOCAL_STATE_WRITE = "TRUST_TIER_1_LOCAL_STATE_WRITE"
TRUST_TIER_2_APPROVED_SOURCE_WRITE = "TRUST_TIER_2_APPROVED_SOURCE_WRITE"
TRUST_TIER_3_VALIDATION_EXECUTION = "TRUST_TIER_3_VALIDATION_EXECUTION"
TRUST_TIER_4_GIT_WRITE = "TRUST_TIER_4_GIT_WRITE"
TRUST_TIER_5_NETWORK_OR_EXTERNAL = "TRUST_TIER_5_NETWORK_OR_EXTERNAL"
TRUST_TIER_6_BLOCKED = "TRUST_TIER_6_BLOCKED"

ROLE_ORCHESTRATOR = "ORCHESTRATOR"
ROLE_IMPLEMENTATION_WORKER = "IMPLEMENTATION_WORKER"
ROLE_VALIDATION_REPAIR_WORKER = "VALIDATION_REPAIR_WORKER"
ROLE_REVIEWER_ASSISTANT = "REVIEWER_ASSISTANT"
ROLE_PROMOTION_CHECKER = "PROMOTION_CHECKER"
ROLE_HUMAN_OPERATOR = "HUMAN_OPERATOR"
ROLE_MCP_CLIENT = "MCP_CLIENT"
ROLE_UNKNOWN_CALLER = "UNKNOWN_CALLER"

STATUS_SUCCESS = "SUCCESS"
STATUS_PARTIAL = "PARTIAL"
STATUS_BLOCKED = "BLOCKED"
STATUS_FAILED = "FAILED"
STATUS_INVALID = "INVALID"

EFFECT_READ = "READ"
EFFECT_WRITE = "WRITE"
EFFECT_EXECUTE = "EXECUTE"
EFFECT_VALIDATE = "VALIDATE"
EFFECT_REPORT = "REPORT"
EFFECT_PLAN = "PLAN"
EFFECT_PROPOSE = "PROPOSE"
EFFECT_APPROVE = "APPROVE"
EFFECT_PROMOTE = "PROMOTE"
EFFECT_ROLLBACK = "ROLLBACK"

TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
TOOL_SCHEMA_INVALID = "TOOL_SCHEMA_INVALID"
TOOL_POLICY_DENIED = "TOOL_POLICY_DENIED"
TOOL_SANDBOX_DENIED = "TOOL_SANDBOX_DENIED"
TOOL_GOVERNANCE_REQUIRED = "TOOL_GOVERNANCE_REQUIRED"
TOOL_HUMAN_APPROVAL_REQUIRED = "TOOL_HUMAN_APPROVAL_REQUIRED"
TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"
TOOL_TIMEOUT = "TOOL_TIMEOUT"
TOOL_RESULT_SCHEMA_INVALID = "TOOL_RESULT_SCHEMA_INVALID"
MCP_REQUEST_INVALID = "MCP_REQUEST_INVALID"
MCP_TOOL_BLOCKED = "MCP_TOOL_BLOCKED"
COMMAND_NOT_IMPLEMENTED = "COMMAND_NOT_IMPLEMENTED"
UNKNOWN_TOOL_FAILURE = "UNKNOWN_TOOL_FAILURE"

DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
DECISION_NEEDS_SANDBOX_CHECK = "NEEDS_SANDBOX_CHECK"
DECISION_NEEDS_DRY_RUN = "NEEDS_DRY_RUN"


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


ALL_TRUST_TIERS = {
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_1_LOCAL_STATE_WRITE,
    TRUST_TIER_2_APPROVED_SOURCE_WRITE,
    TRUST_TIER_3_VALIDATION_EXECUTION,
    TRUST_TIER_4_GIT_WRITE,
    TRUST_TIER_5_NETWORK_OR_EXTERNAL,
    TRUST_TIER_6_BLOCKED,
}

ALL_ROLES = {
    ROLE_ORCHESTRATOR,
    ROLE_IMPLEMENTATION_WORKER,
    ROLE_VALIDATION_REPAIR_WORKER,
    ROLE_REVIEWER_ASSISTANT,
    ROLE_PROMOTION_CHECKER,
    ROLE_HUMAN_OPERATOR,
    ROLE_MCP_CLIENT,
    ROLE_UNKNOWN_CALLER,
}

ALL_STATUSES = {
    STATUS_SUCCESS,
    STATUS_PARTIAL,
    STATUS_BLOCKED,
    STATUS_FAILED,
    STATUS_INVALID,
}

ALL_EFFECTS = {
    EFFECT_READ,
    EFFECT_WRITE,
    EFFECT_EXECUTE,
    EFFECT_VALIDATE,
    EFFECT_REPORT,
    EFFECT_PLAN,
    EFFECT_PROPOSE,
    EFFECT_APPROVE,
    EFFECT_PROMOTE,
    EFFECT_ROLLBACK,
}

ALL_TOOL_FAILURE_CLASSES = {
    TOOL_NOT_FOUND,
    TOOL_SCHEMA_INVALID,
    TOOL_POLICY_DENIED,
    TOOL_SANDBOX_DENIED,
    TOOL_GOVERNANCE_REQUIRED,
    TOOL_HUMAN_APPROVAL_REQUIRED,
    TOOL_EXECUTION_FAILED,
    TOOL_TIMEOUT,
    TOOL_RESULT_SCHEMA_INVALID,
    MCP_REQUEST_INVALID,
    MCP_TOOL_BLOCKED,
    COMMAND_NOT_IMPLEMENTED,
    UNKNOWN_TOOL_FAILURE,
}


@dataclass
class ToolDefinition:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_definition.schema.json"
    tool_name: str = ""
    description: str = ""
    owner_component: str = ""
    trust_tier: str = TRUST_TIER_0_READ_ONLY
    input_schema_id: str = ""
    output_schema_id: str = ""
    allowed_roles: list[str] = field(default_factory=list)
    requested_effects: list[str] = field(default_factory=list)
    requires_sandbox_check: bool = False
    requires_capability_policy: bool = False
    requires_governance: bool = False
    requires_human_approval: bool = False
    requires_dry_run: bool = False
    writes_source: bool = False
    writes_runtime_state: bool = False
    runs_subprocess: bool = False
    uses_network: bool = False
    allowlisted: bool = True
    enabled: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolRegistry:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_registry.schema.json"
    registry_id: str = ""
    created_at: str = ""
    source_component: str = REGISTRY_SOURCE_COMPONENT
    tools: list[ToolDefinition] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolCall:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_call.schema.json"
    tool_call_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    caller_role: str = ROLE_UNKNOWN_CALLER
    caller_id: str | None = None
    session_id: str | None = None
    tool_name: str = ""
    arguments: dict = field(default_factory=dict)
    requested_effect: str = EFFECT_READ
    dry_run: bool = False
    policy_decision_id: str | None = None
    sandbox_decision_id: str | None = None
    governance_decision_id: str | None = None
    human_approval_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolResult:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_result.schema.json"
    tool_result_id: str = ""
    tool_call_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    tool_name: str = ""
    status: str = STATUS_BLOCKED
    exit_code: int = 1
    message: str = ""
    data: dict = field(default_factory=dict)
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    failure_class: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolPermissionDecision:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_permission_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    source_component: str = POLICY_SOURCE_COMPONENT
    tool_name: str = ""
    caller_role: str = ROLE_UNKNOWN_CALLER
    requested_effect: str = ""
    decision: str = DECISION_BLOCK
    reason: str = ""
    required_checks: list[str] = field(default_factory=list)
    missing_checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class InvalidToolRecord:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "invalid_tool_record.schema.json"
    record_id: str = ""
    timestamp: str = ""
    source_component: str = INVALID_SOURCE_COMPONENT
    tool_name: str | None = None
    caller_role: str | None = None
    reason: str = ""
    raw_call: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolAuditEvent:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_audit.schema.json"
    audit_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    tool_call_id: str | None = None
    tool_result_id: str | None = None
    tool_name: str | None = None
    status: str = ""
    message: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolEvidenceManifest:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_evidence_manifest.schema.json"
    manifest_id: str = ""
    component_id: str = SOURCE_COMPONENT
    validated_commit: str = ""
    validated_at: str = ""
    calls: list[ToolCall] = field(default_factory=list)
    results: list[ToolResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolReviewReport:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_review_report.schema.json"
    review_report_id: str = ""
    component_id: str = SOURCE_COMPONENT
    reviewed_commit: str = ""
    reviewed_at: str = ""
    findings: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    final_verdict: str = "NOT_DONE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolCompletionRecord:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_completion_record.schema.json"
    completion_record_id: str = ""
    component_id: str = SOURCE_COMPONENT
    status: str = ""
    validated_commit: str = ""
    validated_at: str = ""
    implementation_score: float = 0.0
    final_decision: str = "NOT_DONE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
