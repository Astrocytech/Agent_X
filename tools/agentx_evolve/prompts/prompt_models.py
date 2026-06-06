from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

PC_SCHEMA_VERSION = "1.0"
PC_ACTIVE = "ACTIVE"
PC_DEPRECATED = "DEPRECATED"
PC_RETIRED = "RETIRED"
ALL_PROMPT_CONTRACT_STATUSES = [PC_ACTIVE, PC_DEPRECATED, PC_RETIRED]

PROMPT_STATUS_DRAFT = "DRAFT"
PROMPT_STATUS_ACTIVE = "ACTIVE"
PROMPT_STATUS_DEPRECATED = "DEPRECATED"
PROMPT_STATUS_RETIRED = "RETIRED"
PROMPT_STATUS_BLOCKED = "BLOCKED"

PROMPT_TYPE_SYSTEM = "SYSTEM"
PROMPT_TYPE_DEVELOPER = "DEVELOPER"
PROMPT_TYPE_ROLE = "ROLE"
PROMPT_TYPE_TASK = "TASK"
PROMPT_TYPE_TOOL_USE = "TOOL_USE"
PROMPT_TYPE_REVIEW = "REVIEW"
PROMPT_TYPE_VALIDATION = "VALIDATION"
PROMPT_TYPE_REPAIR = "REPAIR"
PROMPT_TYPE_PROMOTION = "PROMOTION"

COMPATIBILITY_COMPATIBLE = "COMPATIBLE"
COMPATIBILITY_BREAKING = "BREAKING"
COMPATIBILITY_REQUIRES_MIGRATION = "REQUIRES_MIGRATION"
COMPATIBILITY_UNKNOWN = "UNKNOWN"

PROMPT_DECISION_ALLOW = "ALLOW"
PROMPT_DECISION_BLOCK = "BLOCK"
PROMPT_DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
PROMPT_DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
PROMPT_DECISION_NEEDS_MIGRATION = "NEEDS_MIGRATION"

PROMPT_SAFETY_LOW = "LOW"
PROMPT_SAFETY_MEDIUM = "MEDIUM"
PROMPT_SAFETY_HIGH = "HIGH"
PROMPT_SAFETY_CRITICAL = "CRITICAL"

INJECTION_RISK_SAFE = "safe"
INJECTION_RISK_SUSPICIOUS = "suspicious"
INJECTION_RISK_DANGEROUS = "dangerous"

MIGRATION_STATUS_REQUIRED = "REQUIRED"
MIGRATION_STATUS_IN_PROGRESS = "IN_PROGRESS"
MIGRATION_STATUS_COMPLETE = "COMPLETE"
MIGRATION_STATUS_BLOCKED = "BLOCKED"
MIGRATION_STATUS_NOT_REQUIRED = "NOT_REQUIRED"

ALL_PROMPT_STATUSES = [
    PROMPT_STATUS_DRAFT,
    PROMPT_STATUS_ACTIVE,
    PROMPT_STATUS_DEPRECATED,
    PROMPT_STATUS_RETIRED,
    PROMPT_STATUS_BLOCKED,
]
ALL_PROMPT_TYPES = [
    PROMPT_TYPE_SYSTEM,
    PROMPT_TYPE_DEVELOPER,
    PROMPT_TYPE_ROLE,
    PROMPT_TYPE_TASK,
    PROMPT_TYPE_TOOL_USE,
    PROMPT_TYPE_REVIEW,
    PROMPT_TYPE_VALIDATION,
    PROMPT_TYPE_REPAIR,
    PROMPT_TYPE_PROMOTION,
]
ALL_COMPATIBILITY_RESULTS = [
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_BREAKING,
    COMPATIBILITY_REQUIRES_MIGRATION,
    COMPATIBILITY_UNKNOWN,
]
ALL_PROMPT_DECISIONS = [
    PROMPT_DECISION_ALLOW,
    PROMPT_DECISION_BLOCK,
    PROMPT_DECISION_NEEDS_APPROVAL,
    PROMPT_DECISION_NEEDS_GOVERNANCE,
    PROMPT_DECISION_NEEDS_MIGRATION,
]
ALL_SAFETY_LEVELS = [
    PROMPT_SAFETY_LOW,
    PROMPT_SAFETY_MEDIUM,
    PROMPT_SAFETY_HIGH,
    PROMPT_SAFETY_CRITICAL,
]
ALL_INJECTION_RISK_LEVELS = [
    INJECTION_RISK_SAFE,
    INJECTION_RISK_SUSPICIOUS,
    INJECTION_RISK_DANGEROUS,
]
PR_READ = "READ"
PR_WRITE = "WRITE"
PR_ADMIN = "ADMIN"


@dataclass
class RolePermission:
    role: str = ""
    permission: str = PR_READ
    enabled: bool = True


@dataclass
class PromptPermissionMatrix:
    matrix_id: str = ""
    roles: dict[str, list[RolePermission]] = field(default_factory=dict)
    default_permission: str = PR_READ


ALL_MIGRATION_STATUSES = [
    MIGRATION_STATUS_REQUIRED,
    MIGRATION_STATUS_IN_PROGRESS,
    MIGRATION_STATUS_COMPLETE,
    MIGRATION_STATUS_BLOCKED,
    MIGRATION_STATUS_NOT_REQUIRED,
]

P_PROMPT_EVENT_TYPE_REGISTRY_UPDATE = "REGISTRY_UPDATE"
P_PROMPT_EVENT_TYPE_VERSION_CREATED = "VERSION_CREATED"
P_PROMPT_EVENT_TYPE_VERSION_ACTIVATED = "VERSION_ACTIVATED"
P_PROMPT_EVENT_TYPE_VERSION_DEPRECATED = "VERSION_DEPRECATED"
P_PROMPT_EVENT_TYPE_VERSION_RETIRED = "VERSION_RETIRED"
P_PROMPT_EVENT_TYPE_BINDING_CREATED = "BINDING_CREATED"
P_PROMPT_EVENT_TYPE_DIFF_CREATED = "DIFF_CREATED"
P_PROMPT_EVENT_TYPE_MIGRATION_CREATED = "MIGRATION_CREATED"
P_PROMPT_EVENT_TYPE_MIGRATION_COMPLETED = "MIGRATION_COMPLETED"
P_PROMPT_EVENT_TYPE_SAFETY_CHECK = "SAFETY_CHECK"
P_PROMPT_EVENT_TYPE_ACTIVATION_FAILED = "ACTIVATION_FAILED"
P_PROMPT_EVENT_TYPE_BINDING_FAILED = "BINDING_FAILED"


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


def redact_prompt_text(value: str, max_chars: int = 4000) -> str:
    if len(value) <= max_chars:
        return value
    half = max_chars // 2
    return value[:half] + f"\n... [REDACTED {len(value) - max_chars} chars] ...\n" + value[-half:]


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return dict(obj)


@dataclass
class PromptContract:
    schema_version: str = "1.0"
    schema_id: str = "prompt_contract.schema.json"
    prompt_contract_id: str = ""
    prompt_name: str = ""
    description: str = ""
    owner_component: str = ""
    prompt_type: str = ""
    allowed_roles: list[str] = field(default_factory=list)
    allowed_task_types: list[str] = field(default_factory=list)
    allowed_model_profiles: list[str] = field(default_factory=list)
    allowed_tool_names: list[str] = field(default_factory=list)
    input_contract_id: str = ""
    output_contract_id: str = ""
    safety_rule_ids: list[str] = field(default_factory=list)
    provenance_required: bool = True
    runtime_binding_required: bool = True
    versioning_required: bool = True
    active_version_id: str | None = None
    status: str = PROMPT_STATUS_DRAFT
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptVersion:
    schema_version: str = "1.0"
    schema_id: str = "prompt_version.schema.json"
    prompt_version_id: str = ""
    prompt_contract_id: str = ""
    version: str = ""
    created_at: str = ""
    created_by: str = ""
    status: str = PROMPT_STATUS_DRAFT
    prompt_body: str = ""
    prompt_body_sha256: str = ""
    change_summary: str = ""
    breaking_change: bool = False
    supersedes_version_id: str | None = None
    migration_id: str | None = None
    provenance_id: str = ""
    audit_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptRegistry:
    schema_version: str = "1.0"
    schema_id: str = "prompt_registry.schema.json"
    registry_id: str = ""
    registry_version: str = "1.0"
    created_at: str = ""
    source_component: str = "PromptRegistry"
    contracts: list[PromptContract] = field(default_factory=list)
    versions: list[PromptVersion] = field(default_factory=list)
    active_bindings: dict = field(default_factory=dict)
    registry_sha256: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptRegistrySnapshot:
    schema_version: str = "1.0"
    schema_id: str = "prompt_registry_snapshot.schema.json"
    snapshot_id: str = ""
    registry_id: str = ""
    registry_version: str = ""
    created_at: str = ""
    source_component: str = "PromptRegistry"
    prompt_contract_ids: list[str] = field(default_factory=list)
    prompt_version_ids: list[str] = field(default_factory=list)
    active_bindings: dict = field(default_factory=dict)
    registry_sha256: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptInputContract:
    schema_version: str = "1.0"
    schema_id: str = "prompt_input_contract.schema.json"
    input_contract_id: str = ""
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    field_types: dict = field(default_factory=dict)
    max_input_chars: int = 0
    redaction_required: bool = False
    context_sources_allowed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptOutputContract:
    schema_version: str = "1.0"
    schema_id: str = "prompt_output_contract.schema.json"
    output_contract_id: str = ""
    required_format: str = ""
    required_fields: list[str] = field(default_factory=list)
    forbidden_fields: list[str] = field(default_factory=list)
    max_output_chars: int = 0
    schema_ref: str | None = None
    requires_json: bool = False
    requires_evidence_refs: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptSafetyRule:
    schema_version: str = "1.0"
    schema_id: str = "prompt_safety_rule.schema.json"
    safety_rule_id: str = ""
    name: str = ""
    safety_level: str = PROMPT_SAFETY_MEDIUM
    description: str = ""
    forbidden_content_patterns: list[str] = field(default_factory=list)
    required_instructions: list[str] = field(default_factory=list)
    tool_use_constraints: list[str] = field(default_factory=list)
    model_use_constraints: list[str] = field(default_factory=list)
    injection_defense_required: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptProvenance:
    schema_version: str = "1.0"
    schema_id: str = "prompt_provenance.schema.json"
    provenance_id: str = ""
    prompt_contract_id: str = ""
    prompt_version_id: str = ""
    created_at: str = ""
    created_by: str = ""
    source_documents: list[str] = field(default_factory=list)
    basis_contracts: list[str] = field(default_factory=list)
    review_refs: list[str] = field(default_factory=list)
    approval_refs: list[str] = field(default_factory=list)
    prompt_body_sha256: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptDiffRecord:
    schema_version: str = "1.0"
    schema_id: str = "prompt_diff.schema.json"
    diff_id: str = ""
    from_prompt_version_id: str = ""
    to_prompt_version_id: str = ""
    created_at: str = ""
    summary: str = ""
    added_sections: list[str] = field(default_factory=list)
    removed_sections: list[str] = field(default_factory=list)
    changed_sections: list[str] = field(default_factory=list)
    compatibility_result: str = COMPATIBILITY_UNKNOWN
    breaking_reasons: list[str] = field(default_factory=list)
    diff_sha256: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptMigrationRecord:
    schema_version: str = "1.0"
    schema_id: str = "prompt_migration.schema.json"
    migration_id: str = ""
    from_prompt_version_id: str = ""
    to_prompt_version_id: str = ""
    created_at: str = ""
    migration_status: str = MIGRATION_STATUS_REQUIRED
    required_actions: list[str] = field(default_factory=list)
    affected_runtime_bindings: list[str] = field(default_factory=list)
    approval_required: bool = True
    governance_required: bool = True
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptRuntimeBinding:
    schema_version: str = "1.0"
    schema_id: str = "prompt_runtime_binding.schema.json"
    binding_id: str = ""
    prompt_contract_id: str = ""
    prompt_version_id: str = ""
    bound_at: str = ""
    bound_by_component: str = ""
    caller_role: str = ""
    task_type: str = ""
    model_profile_id: str | None = None
    context_pack_id: str | None = None
    allowed_tool_names: list[str] = field(default_factory=list)
    input_contract_id: str = ""
    output_contract_id: str = ""
    policy_decision_id: str | None = None
    registry_snapshot_sha256: str | None = None
    prompt_body_sha256: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptWorkerPayload:
    schema_version: str = "1.0"
    schema_id: str = "prompt_worker_payload.schema.json"
    payload_id: str = ""
    binding_id: str = ""
    prompt_contract_id: str = ""
    prompt_version_id: str = ""
    prompt_body: str = ""
    prompt_body_sha256: str = ""
    input_data: dict = field(default_factory=dict)
    input_contract_id: str = ""
    output_contract_id: str = ""
    allowed_tool_names: list[str] = field(default_factory=list)
    model_profile_id: str | None = None
    context_pack_id: str | None = None
    registry_snapshot_sha256: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptPermissionDecision:
    schema_version: str = "1.0"
    schema_id: str = "prompt_permission_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    source_component: str = "PromptPermission"
    prompt_contract_id: str = ""
    prompt_version_id: str | None = None
    caller_role: str = ""
    task_type: str = ""
    model_profile_id: str | None = None
    decision: str = PROMPT_DECISION_BLOCK
    reason: str = ""
    missing_checks: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptAuditEvent:
    schema_version: str = "1.0"
    schema_id: str = "prompt_audit.schema.json"
    audit_id: str = ""
    timestamp: str = ""
    source_component: str = "PromptContractVersioning"
    event_type: str = ""
    prompt_contract_id: str | None = None
    prompt_version_id: str | None = None
    status: str = ""
    message: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


PromptDiff = PromptDiffRecord
PromptMigration = PromptMigrationRecord


@dataclass
class PromptEvidenceManifest:
    schema_version: str = "1.0"
    schema_id: str = "prompt_evidence_manifest.schema.json"
    component_id: str = ""
    validated_commit: str = ""
    validated_at: str = ""
    review_environment: dict = field(default_factory=dict)
    commands: list[dict] = field(default_factory=list)
    dependency_state: dict = field(default_factory=dict)
    runtime_artifacts: list[str] = field(default_factory=list)
    evidence_file_hashes: list[dict] = field(default_factory=list)
    prompt_body_hashes_verified: list[str] = field(default_factory=list)
    registry_snapshot_hashes_verified: list[str] = field(default_factory=list)
    diff_hashes_verified: list[str] = field(default_factory=list)
    redaction_status: str = ""
    runtime_boundary_status: str = ""
    source_mutation_status: str = ""
    deviation_register: list[dict] = field(default_factory=list)
    final_decision: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromptInjectionAssessment:
    schema_version: str = "1.0"
    schema_id: str = "prompt_injection_assessment.schema.json"
    assessment_id: str = ""
    prompt_id: str = ""
    risk_level: str = INJECTION_RISK_SAFE
    indicators: list[str] = field(default_factory=list)
    passed: bool = True
    assessed_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
