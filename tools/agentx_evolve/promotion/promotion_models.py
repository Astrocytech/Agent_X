from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from typing import Any

from agentx_evolve.model.model_models import new_id, utc_now_iso

SCHEMA_VERSION = "1.0"

PC_APPROVED = "APPROVED"
PC_BLOCKED = "BLOCKED"
PC_NEEDS_APPROVAL = "NEEDS_APPROVAL"
PC_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
PC_NEEDS_VALIDATION = "NEEDS_VALIDATION"
PC_EXPIRED = "EXPIRED"
PC_INVALID = "INVALID"
PC_FAILED = "FAILED"
PC_DRY_RUN = "DRY_RUN"
ALL_PROMOTION_STATUSES = [
    PC_APPROVED, PC_BLOCKED, PC_NEEDS_APPROVAL, PC_NEEDS_GOVERNANCE,
    PC_NEEDS_VALIDATION, PC_EXPIRED, PC_INVALID, PC_FAILED, PC_DRY_RUN,
]

PD_PROMOTE = "PROMOTE"
PD_BLOCK = "BLOCK"
PD_DEFER = "DEFER"
PD_EXPIRE = "EXPIRE"
PD_INVALIDATE = "INVALIDATE"
PD_REQUEST_APPROVAL = "REQUEST_APPROVAL"
PD_REQUEST_GOVERNANCE = "REQUEST_GOVERNANCE"
PD_REQUEST_VALIDATION = "REQUEST_VALIDATION"
PD_DRY_RUN_ONLY = "DRY_RUN_ONLY"
ALL_PROMOTION_DECISIONS = [
    PD_PROMOTE, PD_BLOCK, PD_DEFER, PD_EXPIRE, PD_INVALIDATE,
    PD_REQUEST_APPROVAL, PD_REQUEST_GOVERNANCE, PD_REQUEST_VALIDATION,
    PD_DRY_RUN_ONLY,
]

FC_CANDIDATE_MISSING = "PROMOTION_CANDIDATE_MISSING"
FC_CANDIDATE_INVALID = "PROMOTION_CANDIDATE_INVALID"
FC_CANDIDATE_SUPERSEDED = "PROMOTION_CANDIDATE_SUPERSEDED"
FC_VALIDATION_MISSING = "PROMOTION_VALIDATION_MISSING"
FC_VALIDATION_FAILED = "PROMOTION_VALIDATION_FAILED"
FC_VALIDATION_STALE = "PROMOTION_VALIDATION_STALE"
FC_SCHEMA_VALIDATION_FAILED = "PROMOTION_SCHEMA_VALIDATION_FAILED"
FC_APPROVAL_MISSING = "PROMOTION_APPROVAL_MISSING"
FC_APPROVAL_INVALID = "PROMOTION_APPROVAL_INVALID"
FC_APPROVAL_REVOKED = "PROMOTION_APPROVAL_REVOKED"
FC_APPROVAL_QUORUM_MISSING = "PROMOTION_APPROVAL_QUORUM_MISSING"
FC_APPROVAL_SCOPE_INSUFFICIENT = "PROMOTION_APPROVAL_SCOPE_INSUFFICIENT"
FC_RISK_UNACCEPTED = "PROMOTION_RISK_UNACCEPTED"
FC_RISK_BLOCKING = "PROMOTION_RISK_BLOCKING"
FC_POLICY_DENIED = "PROMOTION_POLICY_DENIED"
FC_PATCH_EVIDENCE_MISSING = "PROMOTION_PATCH_EVIDENCE_MISSING"
FC_PATCH_EVIDENCE_INVALID = "PROMOTION_PATCH_EVIDENCE_INVALID"
FC_PATCH_ROLLBACK_EVIDENCE_MISSING = "PROMOTION_PATCH_ROLLBACK_EVIDENCE_MISSING"
FC_PATCH_COMMIT_MISMATCH = "PROMOTION_PATCH_COMMIT_MISMATCH"
FC_TOOL_EVIDENCE_MISSING = "PROMOTION_TOOL_EVIDENCE_MISSING"
FC_TOOL_EVIDENCE_INVALID = "PROMOTION_TOOL_EVIDENCE_INVALID"
FC_TOOL_UNRESOLVED_BLOCKER = "PROMOTION_TOOL_UNRESOLVED_BLOCKER"
FC_TOOL_MCP_EXPOSURE_UNSAFE = "PROMOTION_TOOL_MCP_EXPOSURE_UNSAFE"
FC_GIT_STATE_INVALID = "PROMOTION_GIT_STATE_INVALID"
FC_EVIDENCE_HASH_MISSING = "PROMOTION_EVIDENCE_HASH_MISSING"
FC_EVIDENCE_HASH_MISMATCH = "PROMOTION_EVIDENCE_HASH_MISMATCH"
FC_COMPLETION_RECORD_INVALID = "PROMOTION_COMPLETION_RECORD_INVALID"
FC_REVIEW_REPORT_MISSING = "PROMOTION_REVIEW_REPORT_MISSING"
FC_EXPIRED = "PROMOTION_EXPIRED"
FC_DEPENDENCY_UNAVAILABLE = "PROMOTION_DEPENDENCY_UNAVAILABLE"
FC_SOURCE_MUTATION_DETECTED = "PROMOTION_SOURCE_MUTATION_DETECTED"
FC_RELEASE_SCOPE_MISMATCH = "PROMOTION_RELEASE_SCOPE_MISMATCH"
FC_TIMESTAMP_INVALID = "PROMOTION_TIMESTAMP_INVALID"
FC_VALIDATION_TIME_INVALID = "PROMOTION_VALIDATION_TIME_INVALID"
FC_LOCK_UNAVAILABLE = "PROMOTION_LOCK_UNAVAILABLE"
FC_UNKNOWN_FAILURE = "PROMOTION_UNKNOWN_FAILURE"
ALL_FAILURE_CLASSES = [
    FC_CANDIDATE_MISSING, FC_CANDIDATE_INVALID, FC_CANDIDATE_SUPERSEDED,
    FC_VALIDATION_MISSING, FC_VALIDATION_FAILED, FC_VALIDATION_STALE,
    FC_SCHEMA_VALIDATION_FAILED, FC_APPROVAL_MISSING, FC_APPROVAL_INVALID,
    FC_APPROVAL_REVOKED, FC_APPROVAL_QUORUM_MISSING, FC_APPROVAL_SCOPE_INSUFFICIENT,
    FC_RISK_UNACCEPTED, FC_RISK_BLOCKING, FC_POLICY_DENIED,
    FC_PATCH_EVIDENCE_MISSING, FC_PATCH_EVIDENCE_INVALID,
    FC_PATCH_ROLLBACK_EVIDENCE_MISSING, FC_PATCH_COMMIT_MISMATCH,
    FC_TOOL_EVIDENCE_MISSING, FC_TOOL_EVIDENCE_INVALID,
    FC_TOOL_UNRESOLVED_BLOCKER, FC_TOOL_MCP_EXPOSURE_UNSAFE,
    FC_GIT_STATE_INVALID, FC_EVIDENCE_HASH_MISSING, FC_EVIDENCE_HASH_MISMATCH,
    FC_COMPLETION_RECORD_INVALID, FC_REVIEW_REPORT_MISSING,
    FC_EXPIRED, FC_DEPENDENCY_UNAVAILABLE, FC_SOURCE_MUTATION_DETECTED,
    FC_RELEASE_SCOPE_MISMATCH, FC_TIMESTAMP_INVALID, FC_VALIDATION_TIME_INVALID,
    FC_LOCK_UNAVAILABLE, FC_UNKNOWN_FAILURE,
]

AT_HUMAN_REVIEW = "HUMAN_REVIEW"
AT_GOVERNANCE = "GOVERNANCE"
AT_RISK_ACCEPTANCE = "RISK_ACCEPTANCE"
AT_POLICY_EXCEPTION = "POLICY_EXCEPTION"
AT_PROMOTION_APPROVAL = "PROMOTION_APPROVAL"
ALL_APPROVAL_TYPES = [
    AT_HUMAN_REVIEW, AT_GOVERNANCE, AT_RISK_ACCEPTANCE,
    AT_POLICY_EXCEPTION, AT_PROMOTION_APPROVAL,
]

RS_LOW = "LOW"
RS_MEDIUM = "MEDIUM"
RS_HIGH = "HIGH"
RS_CRITICAL = "CRITICAL"
ALL_RISK_SEVERITIES = [RS_LOW, RS_MEDIUM, RS_HIGH, RS_CRITICAL]

WT_CLEAN = "CLEAN"
WT_EXPECTED_RUNTIME_ARTIFACTS_ONLY = "EXPECTED_RUNTIME_ARTIFACTS_ONLY"
WT_DIRTY = "DIRTY"
WT_UNKNOWN = "UNKNOWN"
ALL_WORKING_TREE_STATUSES = [
    WT_CLEAN, WT_EXPECTED_RUNTIME_ARTIFACTS_ONLY, WT_DIRTY, WT_UNKNOWN,
]

CS_PASS = "PASS"
CS_FAIL = "FAIL"
CS_NOT_RUN = "NOT_RUN"
ALL_COMMAND_STATUSES = [CS_PASS, CS_FAIL, CS_NOT_RUN]

SMS_CLEAN = "CLEAN"
SMS_EXPECTED_RUNTIME_ARTIFACTS_ONLY = "EXPECTED_RUNTIME_ARTIFACTS_ONLY"
SMS_DIRTY = "DIRTY"
SMS_NOT_CHECKED = "NOT_CHECKED"
ALL_SOURCE_MUTATION_STATUSES = [
    SMS_CLEAN, SMS_EXPECTED_RUNTIME_ARTIFACTS_ONLY, SMS_DIRTY, SMS_NOT_CHECKED,
]

CT_IMPLEMENTATION = "IMPLEMENTATION"
CT_PATCH_SESSION = "PATCH_SESSION"
CT_TOOL_LAYER = "TOOL_LAYER"
CT_MODEL_LAYER = "MODEL_LAYER"
CT_CONFIG_CHANGE = "CONFIG_CHANGE"
CT_DOCUMENTATION_CHANGE = "DOCUMENTATION_CHANGE"
CT_RELEASE_BUNDLE = "RELEASE_BUNDLE"
ALL_CANDIDATE_TYPES = [
    CT_IMPLEMENTATION, CT_PATCH_SESSION, CT_TOOL_LAYER, CT_MODEL_LAYER,
    CT_CONFIG_CHANGE, CT_DOCUMENTATION_CHANGE, CT_RELEASE_BUNDLE,
]

EV_TRUSTED_VALIDATED = "TRUSTED_VALIDATED"
EV_TRUSTED_CURRENT_COMMIT = "TRUSTED_CURRENT_COMMIT"
EV_STALE_DIFFERENT_COMMIT = "STALE_DIFFERENT_COMMIT"
EV_UNVERIFIED_IMPORTED = "UNVERIFIED_IMPORTED"
EV_MISSING = "MISSING"
EV_TAMPERED = "TAMPERED"
ALL_EVIDENCE_STATUSES = [
    EV_TRUSTED_VALIDATED, EV_TRUSTED_CURRENT_COMMIT, EV_STALE_DIFFERENT_COMMIT,
    EV_UNVERIFIED_IMPORTED, EV_MISSING, EV_TAMPERED,
]

DEFAULT_VALIDATION_FRESHNESS_MINUTES = 1440
DEFAULT_ALLOWED_CLOCK_SKEW_MINUTES = 5
DEFAULT_LOCK_TIMEOUT_SECONDS = 10
DEFAULT_STALE_LOCK_AGE_SECONDS = 900
DEFAULT_REQUIRED_APPROVAL_QUORUM = 1
DEFAULT_HIGH_RISK_APPROVAL_QUORUM = 2
DEFAULT_CRITICAL_RISK_APPROVAL_QUORUM = 2


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if val is not None:
                result[f] = _serialize(val)
        return result
    return _serialize(obj)


def _serialize(val: Any) -> Any:
    if isinstance(val, (list, tuple)):
        return [_serialize(v) for v in val]
    if isinstance(val, dict):
        return {k: _serialize(v) for k, v in val.items()}
    if hasattr(val, "__dataclass_fields__"):
        return to_dict(val)
    if isinstance(val, Path):
        return str(val.as_posix())
    return val


def from_dict(model_type: type, data: dict) -> object:
    field_types = {}
    if hasattr(model_type, "__dataclass_fields__"):
        field_types = {f: ft.type for f, ft in model_type.__dataclass_fields__.items()}
    kwargs = {}
    for f in model_type.__dataclass_fields__:
        if f in data:
            kwargs[f] = data[f]
    return model_type(**kwargs)


def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def append_jsonl(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")
    return path


def redact_sensitive_values(data: object) -> object:
    if isinstance(data, dict):
        redacted = {}
        for k, v in data.items():
            if isinstance(v, str) and k.lower() in ("secret", "password", "token", "api_key", "private_key"):
                redacted[k] = "***REDACTED***"
            else:
                redacted[k] = redact_sensitive_values(v)
        return redacted
    if isinstance(data, list):
        return [redact_sensitive_values(v) for v in data]
    return data


@dataclass
class ReleaseCandidate:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_release_candidate.schema.json"
    candidate_id: str = ""
    candidate_hash: str = ""
    created_at: str = ""
    created_by: str | None = None
    component_id: str = ""
    component_name: str = ""
    roadmap_layer: str | int = ""
    candidate_type: str = CT_IMPLEMENTATION
    source_branch: str | None = None
    source_commit: str = ""
    base_commit: str | None = None
    changed_files: list[str] = field(default_factory=list)
    changed_schemas: list[str] = field(default_factory=list)
    changed_tests: list[str] = field(default_factory=list)
    related_layers: list[str] = field(default_factory=list)
    required_validations: list[str] = field(default_factory=list)
    required_approvals: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    risk_ids: list[str] = field(default_factory=list)
    policy_context_id: str | None = None
    patch_session_id: str | None = None
    tool_session_id: str | None = None
    git_evidence_id: str | None = None
    git_status_summary: dict = field(default_factory=dict)
    expires_at: str | None = None
    supersedes_candidate_id: str | None = None
    superseded_by_candidate_id: str | None = None
    superseded_at: str | None = None
    supersession_reason: str | None = None
    release_scope: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ValidationEvidence:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_validation_evidence.schema.json"
    evidence_id: str = ""
    evidence_hash: str = ""
    created_at: str = ""
    component_id: str = ""
    validated_commit: str = ""
    validation_started_at: str = ""
    validation_completed_at: str = ""
    commands: list[dict] = field(default_factory=list)
    compileall_status: str = CS_NOT_RUN
    compileall_exit_code: int | None = None
    pytest_status: str = CS_NOT_RUN
    pytest_exit_code: int | None = None
    schema_validation_status: str = CS_NOT_RUN
    schema_validation_exit_code: int | None = None
    source_mutation_status: str = SMS_NOT_CHECKED
    evidence_files: list[str] = field(default_factory=list)
    evidence_hashes: list[dict] = field(default_factory=list)
    review_report_refs: list[str] = field(default_factory=list)
    completion_record_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RiskAcceptance:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_risk_acceptance.schema.json"
    risk_acceptance_id: str = ""
    risk_acceptance_hash: str = ""
    created_at: str = ""
    component_id: str = ""
    candidate_id: str = ""
    risks: list[dict] = field(default_factory=list)
    accepted_risks: list[str] = field(default_factory=list)
    blocking_risks: list[str] = field(default_factory=list)
    accepted_by: str | None = None
    approval_ref: str | None = None
    expires_at: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ApprovalReference:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_approval_reference.schema.json"
    approval_id: str = ""
    approval_hash: str = ""
    created_at: str = ""
    approved_by: str = ""
    approval_type: str = AT_HUMAN_REVIEW
    component_id: str = ""
    candidate_id: str = ""
    scope: list[str] = field(default_factory=list)
    approved_commit: str = ""
    expires_at: str | None = None
    source: str = ""
    artifact_ref: str | None = None
    signature_hash: str | None = None
    revoked: bool = False
    revoked_at: str | None = None
    revoked_by: str | None = None
    revocation_reason: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitEvidence:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_git_evidence.schema.json"
    git_evidence_id: str = ""
    git_evidence_hash: str = ""
    created_at: str = ""
    component_id: str = ""
    candidate_id: str = ""
    source_branch: str | None = None
    source_commit: str = ""
    base_commit: str | None = None
    working_tree_status: str = WT_UNKNOWN
    expected_runtime_artifacts_only: bool = False
    changed_files: list[str] = field(default_factory=list)
    diff_name_only: list[str] = field(default_factory=list)
    commit_reachable: bool = True
    untracked_files: list[str] = field(default_factory=list)
    forbidden_git_actions_detected: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromotionGatePolicy:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_gate_policy.schema.json"
    policy_id: str = ""
    policy_hash: str = ""
    created_at: str = ""
    component_id: str = "AGENTX_PROMOTION_RELEASE_GATE"
    source_component: str = "PromotionReleaseGate"
    require_clean_git_state: bool = True
    allow_expected_runtime_artifacts_only: bool = True
    validation_freshness_minutes: int = DEFAULT_VALIDATION_FRESHNESS_MINUTES
    require_compileall_pass: bool = True
    require_pytest_pass: bool = True
    require_schema_validation_pass: bool = True
    require_command_exit_codes: bool = True
    require_evidence_hashes: bool = True
    require_review_report: bool = True
    require_completion_record_for_approved: bool = True
    require_policy_decision: bool = True
    require_human_approval_when_listed: bool = True
    require_patch_evidence_when_patch_session_exists: bool = True
    require_tool_evidence_when_tool_session_exists: bool = True
    allow_dry_run_without_policy: bool = True
    allow_network: bool = False
    allow_git_write: bool = False
    allow_source_mutation: bool = False
    allow_release_action: bool = False
    allowed_runtime_roots: list[str] = field(default_factory=list)
    non_overridable_blockers: list[str] = field(default_factory=list)
    required_approval_quorum: int = DEFAULT_REQUIRED_APPROVAL_QUORUM
    require_distinct_approvers: bool = True
    high_risk_approval_quorum: int = DEFAULT_HIGH_RISK_APPROVAL_QUORUM
    critical_risk_approval_quorum: int = DEFAULT_CRITICAL_RISK_APPROVAL_QUORUM
    allowed_clock_skew_minutes: int = DEFAULT_ALLOWED_CLOCK_SKEW_MINUTES
    lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS
    stale_lock_age_seconds: int = DEFAULT_STALE_LOCK_AGE_SECONDS
    allow_stale_lock_recovery: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromotionGateDecision:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_gate_decision.schema.json"
    decision_id: str = ""
    gate_decision_hash: str = ""
    idempotency_key: str = ""
    created_at: str = ""
    component_id: str = ""
    candidate_id: str = ""
    source_commit: str = ""
    decision: str = PD_BLOCK
    status: str = PC_BLOCKED
    reason: str = ""
    checks_run: list[dict] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    blocking_failures: list[dict] = field(default_factory=list)
    high_issues: list[dict] = field(default_factory=list)
    non_blocking_followups: list[dict] = field(default_factory=list)
    required_approvals_status: str = CS_NOT_RUN
    validation_status: str = CS_NOT_RUN
    risk_status: str = CS_NOT_RUN
    policy_status: str = CS_NOT_RUN
    patch_evidence_status: str = CS_NOT_RUN
    tool_evidence_status: str = CS_NOT_RUN
    git_status: str = CS_NOT_RUN
    expiry_status: str = CS_NOT_RUN
    dry_run: bool = False
    evidence_manifest_path: str | None = None
    evidence_manifest_sha256: str | None = None
    review_report_path: str | None = None
    review_report_sha256: str | None = None
    completion_record_path: str | None = None
    completion_record_sha256: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromotionEvidenceManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_evidence_manifest.schema.json"
    manifest_id: str = ""
    manifest_hash: str = ""
    created_at: str = ""
    component_id: str = ""
    candidate_id: str = ""
    source_commit: str = ""
    decision_id: str = ""
    gate_decision_hash: str = ""
    idempotency_key: str = ""
    reviewed_commit: str | None = None
    runtime_artifact_root: str = ""
    evidence_files: list[dict] = field(default_factory=list)
    evidence_file_hashes: list[dict] = field(default_factory=list)
    command_outputs: list[dict] = field(default_factory=list)
    policy_decision_refs: list[str] = field(default_factory=list)
    approval_refs: list[str] = field(default_factory=list)
    patch_evidence_refs: list[str] = field(default_factory=list)
    tool_evidence_refs: list[str] = field(default_factory=list)
    git_evidence_refs: list[str] = field(default_factory=list)
    failure_record_refs: list[str] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    source_mutation_status: str = SMS_NOT_CHECKED
    hash_status: str = CS_NOT_RUN
    final_decision: str = PC_BLOCKED
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromotionReviewReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_review_report.schema.json"
    review_report_id: str = ""
    review_report_hash: str = ""
    created_at: str = ""
    component_id: str = ""
    candidate_id: str = ""
    source_commit: str = ""
    decision_id: str = ""
    reviewed_branch: str | None = None
    reviewed_commit: str = ""
    review_environment: dict = field(default_factory=dict)
    commands_run: list[dict] = field(default_factory=list)
    coverage_statuses: dict = field(default_factory=dict)
    blockers: list[dict] = field(default_factory=list)
    high_issues: list[dict] = field(default_factory=list)
    non_blocking_followups: list[dict] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    evidence_manifest_path: str = ""
    evidence_manifest_sha256: str = ""
    completion_record_path: str | None = None
    completion_record_sha256: str | None = None
    implementation_rating: float | None = None
    final_verdict: str = "NOT_DONE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PromotionCompletionRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_completion_record.schema.json"
    completion_record_id: str = ""
    completion_record_hash: str = ""
    created_at: str = ""
    component_id: str = ""
    component_name: str = ""
    candidate_id: str = ""
    source_commit: str = ""
    decision_id: str = ""
    decision_status: str = PC_APPROVED
    decision: str = PD_PROMOTE
    approved_at: str = ""
    approved_by: str | None = None
    basis_documents: list[str] = field(default_factory=list)
    validated_commands: list[dict] = field(default_factory=list)
    validated_evidence: list[dict] = field(default_factory=list)
    release_scope: list[str] = field(default_factory=list)
    policy_decision_refs: list[str] = field(default_factory=list)
    approval_refs: list[str] = field(default_factory=list)
    risk_acceptance_refs: list[str] = field(default_factory=list)
    git_evidence_refs: list[str] = field(default_factory=list)
    patch_evidence_refs: list[str] = field(default_factory=list)
    tool_evidence_refs: list[str] = field(default_factory=list)
    evidence_manifest_path: str = ""
    evidence_manifest_sha256: str = ""
    review_report_path: str = ""
    review_report_sha256: str = ""
    deviation_register: list[dict] = field(default_factory=list)
    unresolved_risks: list[dict] = field(default_factory=list)
    final_decision: str = "DONE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
