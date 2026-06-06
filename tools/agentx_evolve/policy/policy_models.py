from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4

RULE_ALLOW = "ALLOW"
RULE_DENY = "DENY"
RULE_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

ENFORCEMENT_ALLOW = "ALLOW"
ENFORCEMENT_BLOCK = "BLOCK"
ENFORCEMENT_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

SIDE_EFFECT_READ = "read"
SIDE_EFFECT_WRITE = "write"
SIDE_EFFECT_DESTRUCTIVE = "destructive"

OP_READ = "READ"
OP_WRITE = "WRITE"
OP_EDIT = "EDIT"
OP_DELETE = "DELETE"
OP_EXECUTE = "EXECUTE"
OP_NETWORK = "NETWORK"
OP_SUBPROCESS = "SUBPROCESS"


class SideEffectLevel(Enum):
    READ = SIDE_EFFECT_READ
    WRITE = SIDE_EFFECT_WRITE
    DESTRUCTIVE = SIDE_EFFECT_DESTRUCTIVE


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
            if isinstance(val, Path):
                result[f] = str(val)
            elif isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            elif isinstance(val, Enum):
                result[f] = val.value
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


@dataclass
class PolicyRule:
    rule_id: str = ""
    timestamp: str = ""
    effect: str = RULE_DENY
    operation: str = ""
    target_pattern: str = ""
    reason: str = ""
    priority: int = 0
    conditions: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class CapabilityDefinition:
    schema_version: str = "1.0"
    schema_id: str = "capability_definition.schema.json"
    capability_id: str = ""
    timestamp: str = ""
    name: str = ""
    description: str = ""
    allowed_operations: list[str] = field(default_factory=lambda: [OP_READ])
    side_effect_level: str = SIDE_EFFECT_READ
    requires_approval: bool = False
    rate_limit_per_minute: int = 0
    enabled: bool = True
    allowed_profiles: list[str] = field(default_factory=lambda: ["*"])
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ToolCapability:
    schema_version: str = "1.0"
    schema_id: str = "tool_capability.schema.json"
    tool_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    description: str = ""
    capabilities: list[CapabilityDefinition] = field(default_factory=list)
    policy_rules: list[PolicyRule] = field(default_factory=list)
    enabled: bool = True
    requires_approval: bool = False
    side_effect_level: str = SIDE_EFFECT_READ
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def get_capability(self, name: str) -> CapabilityDefinition | None:
        for c in self.capabilities:
            if c.name == name:
                return c
        return None

    def get_rule_for_operation(self, operation: str) -> PolicyRule | None:
        for rule in self.policy_rules:
            if rule.operation == operation or rule.operation == "*":
                return rule
        return None


@dataclass
class CapabilityRegistry:
    schema_version: str = "1.0"
    schema_id: str = "capability_registry.schema.json"
    registry_id: str = ""
    timestamp: str = ""
    tools: dict[str, ToolCapability] = field(default_factory=dict)
    global_rules: list[PolicyRule] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = to_dict(self)
        d["tools"] = [v.to_dict() for v in self.tools.values()]
        d["global_rules"] = [r.to_dict() for r in self.global_rules]
        return d

    def register_tool(self, tool: ToolCapability) -> ToolCapability:
        self.tools[tool.tool_name] = tool
        return tool

    def get_tool(self, tool_name: str) -> ToolCapability | None:
        return self.tools.get(tool_name)

    def remove_tool(self, tool_name: str) -> bool:
        if tool_name in self.tools:
            del self.tools[tool_name]
            return True
        return False

    def list_tools(self) -> list[ToolCapability]:
        return list(self.tools.values())

    def list_enabled_tools(self) -> list[ToolCapability]:
        return [t for t in self.tools.values() if t.enabled]


@dataclass
class PolicyEnforcementResult:
    schema_version: str = "1.0"
    schema_id: str = "policy_enforcement_result.schema.json"
    enforcement_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    operation: str = ""
    decision: str = ENFORCEMENT_BLOCK
    reason: str = ""
    matched_rule_id: str | None = None
    matched_rule_effect: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


PAE_ALLOW = "ALLOW"
PAE_BLOCK = "BLOCK"
PAE_WARN = "WARN"
ALL_POLICY_AUDIT_EFFECTS = {PAE_ALLOW, PAE_BLOCK, PAE_WARN}


@dataclass
class PolicyAuditEntry:
    entry_id: str = ""
    timestamp: str = ""
    session_id: str = ""
    decision: str = PAE_BLOCK
    reason: str = ""
    metadata: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


_audit_log: list[PolicyAuditEntry] = []


def log_policy_decision(
    session_id: str,
    decision: str = PAE_BLOCK,
    reason: str = "",
    metadata: dict | None = None,
) -> PolicyAuditEntry:
    entry = PolicyAuditEntry(
        entry_id=new_id("pae"),
        timestamp=utc_now_iso(),
        session_id=session_id,
        decision=decision,
        reason=reason,
        metadata=metadata or {},
    )
    _audit_log.append(entry)
    return entry


def get_policy_audit_log() -> list[PolicyAuditEntry]:
    return list(_audit_log)


def get_policy_audit_by_session(session_id: str) -> list[PolicyAuditEntry]:
    return [e for e in _audit_log if e.session_id == session_id]


def clear_policy_audit_log() -> None:
    _audit_log.clear()


# ── Policy / Capability Registry (spec v5) constants and dataclasses ──────────

# Decision constants
DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_WARN = "WARN"
DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
DECISION_NEEDS_SANDBOX_CHECK = "NEEDS_SANDBOX_CHECK"
DECISION_NEEDS_RISK_REVIEW = "NEEDS_RISK_REVIEW"
DECISION_NEEDS_VALIDATION = "NEEDS_VALIDATION"
DECISION_UNKNOWN_ROLE = "UNKNOWN_ROLE"
DECISION_UNKNOWN_TOOL = "UNKNOWN_TOOL"
DECISION_UNKNOWN_MODEL = "UNKNOWN_MODEL"
DECISION_INVALID_POLICY = "INVALID_POLICY"

# Role constants
ROLE_ORCHESTRATOR = "ORCHESTRATOR"
ROLE_IMPLEMENTATION_WORKER = "IMPLEMENTATION_WORKER"
ROLE_VALIDATION_REPAIR_WORKER = "VALIDATION_REPAIR_WORKER"
ROLE_REVIEWER_ASSISTANT = "REVIEWER_ASSISTANT"
ROLE_PROMOTION_CHECKER = "PROMOTION_CHECKER"
ROLE_PATCH_EXECUTOR = "PATCH_EXECUTOR"
ROLE_TOOL_ADAPTER = "TOOL_ADAPTER"
ROLE_MODEL_ADAPTER = "MODEL_ADAPTER"
ROLE_HUMAN_OPERATOR = "HUMAN_OPERATOR"

ALL_ROLES = [
    ROLE_ORCHESTRATOR,
    ROLE_IMPLEMENTATION_WORKER,
    ROLE_VALIDATION_REPAIR_WORKER,
    ROLE_REVIEWER_ASSISTANT,
    ROLE_PROMOTION_CHECKER,
    ROLE_PATCH_EXECUTOR,
    ROLE_TOOL_ADAPTER,
    ROLE_MODEL_ADAPTER,
    ROLE_HUMAN_OPERATOR,
]

# Effect constants
EFFECT_READ = "READ"
EFFECT_WRITE_RUNTIME = "WRITE_RUNTIME"
EFFECT_WRITE_SOURCE = "WRITE_SOURCE"
EFFECT_EDIT_SOURCE = "EDIT_SOURCE"
EFFECT_PATCH_PRECHECK = "PATCH_PRECHECK"
EFFECT_PATCH_APPLY = "PATCH_APPLY"
EFFECT_EXECUTE_COMMAND = "EXECUTE_COMMAND"
EFFECT_USE_MODEL = "USE_MODEL"
EFFECT_USE_NETWORK = "USE_NETWORK"
EFFECT_READ_GIT = "READ_GIT"
EFFECT_WRITE_GIT = "WRITE_GIT"
EFFECT_REQUEST_APPROVAL = "REQUEST_APPROVAL"
EFFECT_PROMOTE = "PROMOTE"
EFFECT_ROLLBACK = "ROLLBACK"
EFFECT_AUDIT_WRITE = "AUDIT_WRITE"
EFFECT_GRAPH_WRITE = "GRAPH_WRITE"
EFFECT_MEMORY_WRITE = "MEMORY_WRITE"

# Trust tier constants
TRUST_TIER_0_READ_ONLY = "TRUST_TIER_0_READ_ONLY"
TRUST_TIER_1_LOCAL_STATE_WRITE = "TRUST_TIER_1_LOCAL_STATE_WRITE"
TRUST_TIER_2_APPROVED_SOURCE_WRITE = "TRUST_TIER_2_APPROVED_SOURCE_WRITE"
TRUST_TIER_3_VALIDATION_EXECUTION = "TRUST_TIER_3_VALIDATION_EXECUTION"
TRUST_TIER_4_GIT_WRITE = "TRUST_TIER_4_GIT_WRITE"
TRUST_TIER_5_NETWORK_OR_EXTERNAL = "TRUST_TIER_5_NETWORK_OR_EXTERNAL"
TRUST_TIER_6_BLOCKED = "TRUST_TIER_6_BLOCKED"

# Non-overridable block constants
BLOCK_L0_MUTATION = "L0_MUTATION_BLOCK"
BLOCK_PATH_TRAVERSAL = "PATH_TRAVERSAL_BLOCK"
BLOCK_SYMLINK_ESCAPE = "SYMLINK_ESCAPE_BLOCK"
BLOCK_MISSING_ROLLBACK = "MISSING_ROLLBACK_FOR_SOURCE_MUTATION"
BLOCK_SCHEMA_INVALID = "SCHEMA_INVALID_PROMOTION_EVIDENCE"
BLOCK_UNCONTROLLED_SHELL = "UNCONTROLLED_SHELL_EXECUTION"
BLOCK_NETWORK_LOCAL_ONLY = "NETWORK_IN_LOCAL_ONLY_MODE"

NON_OVERRIDABLE_BLOCKS = [
    BLOCK_L0_MUTATION,
    BLOCK_PATH_TRAVERSAL,
    BLOCK_SYMLINK_ESCAPE,
    BLOCK_MISSING_ROLLBACK,
    BLOCK_SCHEMA_INVALID,
    BLOCK_UNCONTROLLED_SHELL,
    BLOCK_NETWORK_LOCAL_ONLY,
]

SOURCE_COMPONENT = "PolicyCapabilityRegistry"
SPEC_SCHEMA_VERSION = "1.0"

# Stable reason codes
REASON_ALLOW_BY_CAPABILITY = "ALLOW_BY_CAPABILITY"
REASON_DEFAULT_BLOCK = "DEFAULT_BLOCK"
REASON_UNKNOWN_ROLE = "UNKNOWN_ROLE"
REASON_UNKNOWN_TOOL = "UNKNOWN_TOOL"
REASON_UNKNOWN_EFFECT = "UNKNOWN_EFFECT"
REASON_UNKNOWN_MODEL = "UNKNOWN_MODEL"
REASON_INVALID_POLICY = "INVALID_POLICY"
REASON_TOOL_BLOCKED = "TOOL_BLOCKED"
REASON_TOOL_EFFECT_NOT_ALLOWED = "TOOL_EFFECT_NOT_ALLOWED"
REASON_CAPABILITY_MISSING = "CAPABILITY_MISSING"
REASON_CAPABILITY_EFFECT_BLOCKED = "CAPABILITY_EFFECT_BLOCKED"
REASON_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
REASON_REQUIRES_GOVERNANCE = "REQUIRES_GOVERNANCE"
REASON_REQUIRES_SANDBOX = "REQUIRES_SANDBOX"
REASON_REQUIRES_RISK_REVIEW = "REQUIRES_RISK_REVIEW"
REASON_REQUIRES_VALIDATION = "REQUIRES_VALIDATION"
REASON_NETWORK_BLOCKED_BY_DEFAULT = "NETWORK_BLOCKED_BY_DEFAULT"
REASON_HOSTED_MODEL_BLOCKED_BY_DEFAULT = "HOSTED_MODEL_BLOCKED_BY_DEFAULT"
REASON_MODEL_CANNOT_WRITE_FILES = "MODEL_CANNOT_WRITE_FILES"
REASON_MODEL_CANNOT_EXECUTE_COMMANDS = "MODEL_CANNOT_EXECUTE_COMMANDS"
REASON_MODEL_CANNOT_EXECUTE_TOOLS = "MODEL_CANNOT_EXECUTE_TOOLS"
REASON_GIT_WRITE_BLOCKED_BY_DEFAULT = "GIT_WRITE_BLOCKED_BY_DEFAULT"
REASON_HUMAN_CANNOT_OVERRIDE_HARD_BLOCK = "HUMAN_CANNOT_OVERRIDE_HARD_BLOCK"
REASON_SANDBOX_BLOCK_IS_AUTHORITATIVE = "SANDBOX_BLOCK_IS_AUTHORITATIVE"


@dataclass
class CapabilityEntry:
    capability_id: str = ""
    role: str = ""
    tool_name: str = ""
    allowed_effects: list[str] = field(default_factory=list)
    blocked_effects: list[str] = field(default_factory=list)
    requires_approval: bool = False
    requires_governance: bool = False
    requires_sandbox: bool = False
    requires_risk_review: bool = False
    allowed_paths: list[str] = field(default_factory=list)
    blocked_paths: list[str] = field(default_factory=list)
    allowed_commands: list[str] = field(default_factory=list)
    allowed_model_profiles: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class CapabilityPolicy:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "capability_policy.schema.json"
    policy_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    default_decision: str = DECISION_BLOCK
    roles: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    capabilities: list[CapabilityEntry] = field(default_factory=list)
    blocked_effects: list[str] = field(default_factory=list)
    approval_required_effects: list[str] = field(default_factory=list)
    governance_required_effects: list[str] = field(default_factory=list)
    sandbox_required_effects: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ToolEntry:
    tool_name: str = ""
    tool_category: str = ""
    trust_tier: str = TRUST_TIER_6_BLOCKED
    requested_effects: list[str] = field(default_factory=list)
    requires_governance: bool = False
    requires_human_approval: bool = False
    requires_sandbox: bool = False
    requires_risk_review: bool = False
    writes_source: bool = False
    writes_runtime: bool = False
    executes_command: bool = False
    uses_network: bool = False
    uses_model: bool = False
    allowlisted: bool = False
    blocked: bool = True
    notes: str = ""


@dataclass
class ToolPolicy:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "tool_policy.schema.json"
    policy_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    tools: list[ToolEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ModelProfile:
    model_profile_id: str = ""
    provider_type: str = ""
    allowed_task_types: list[str] = field(default_factory=list)
    blocked_task_types: list[str] = field(default_factory=list)
    may_read_source_context: bool = False
    may_write_files: bool = False
    may_execute_tools: bool = False
    may_execute_commands: bool = False
    may_use_network: bool = False
    requires_redaction: bool = True
    requires_json_output: bool = True
    max_context_tokens: int = 4096
    local_only: bool = True
    requires_human_approval: bool = False
    notes: str = ""


@dataclass
class ModelPolicy:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "model_policy.schema.json"
    policy_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    default_model_mode: str = "local_only"
    model_profiles: list[ModelProfile] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class RolePermissionMatrix:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "role_permission_matrix.schema.json"
    matrix_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    roles: list[str] = field(default_factory=list)
    matrix: dict[str, Any] = field(default_factory=dict)
    non_overridable_blocks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PolicyDecision:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "policy_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    caller_role: str = ""
    tool_name: str = ""
    requested_effect: str = ""
    target: str | None = None
    decision: str = DECISION_BLOCK
    reason: str = ""
    applied_policy_ids: list[str] = field(default_factory=list)
    required_followups: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PolicyViolation:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "policy_violation.schema.json"
    violation_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    caller_role: str = ""
    tool_name: str = ""
    requested_effect: str = ""
    target: str | None = None
    violation_type: str = ""
    severity: str = "HIGH"
    reason: str = ""
    decision_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PolicyAudit:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "policy_audit.schema.json"
    audit_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    decision_id: str = ""
    caller_role: str = ""
    tool_name: str = ""
    requested_effect: str = ""
    decision: str = ""
    reason: str = ""
    success: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
