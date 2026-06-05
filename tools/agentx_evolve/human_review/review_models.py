from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import hashlib
import json
from agentx_evolve.model.model_models import new_id, utc_now_iso

# Decision constants
DECISION_REQUESTED = "REQUESTED"
DECISION_APPROVED = "APPROVED"
DECISION_REJECTED = "REJECTED"
DECISION_DEFERRED = "DEFERRED"
DECISION_NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
DECISION_REVOKED = "REVOKED"
DECISION_EXPIRED = "EXPIRED"
DECISION_INVALID = "INVALID"
ALL_DECISIONS = [
    DECISION_REQUESTED, DECISION_APPROVED, DECISION_REJECTED,
    DECISION_DEFERRED, DECISION_NEEDS_CLARIFICATION, DECISION_REVOKED,
    DECISION_EXPIRED, DECISION_INVALID,
]

# Validation status constants
VALIDATION_VALID = "VALID"
VALIDATION_INVALID = "INVALID"
VALIDATION_EXPIRED = "EXPIRED"
VALIDATION_REVOKED = "REVOKED"
VALIDATION_OUT_OF_SCOPE = "OUT_OF_SCOPE"
VALIDATION_MISSING = "MISSING"
VALIDATION_FORGED_OR_UNTRUSTED = "FORGED_OR_UNTRUSTED"
VALIDATION_STALE = "STALE"
VALIDATION_REPLAYED = "REPLAYED"
VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH = "CROSS_REPO_OR_SESSION_MISMATCH"
VALIDATION_BLOCKED = "BLOCKED"
ALL_VALIDATION_STATUSES = [
    VALIDATION_VALID, VALIDATION_INVALID, VALIDATION_EXPIRED,
    VALIDATION_REVOKED, VALIDATION_OUT_OF_SCOPE, VALIDATION_MISSING,
    VALIDATION_FORGED_OR_UNTRUSTED, VALIDATION_STALE, VALIDATION_REPLAYED,
    VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH, VALIDATION_BLOCKED,
]

# Request status constants
REQ_PENDING = "PENDING"
REQ_APPROVED = "APPROVED"
REQ_REJECTED = "REJECTED"
REQ_DEFERRED = "DEFERRED"
REQ_NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
REQ_CLOSED = "CLOSED"
REQ_EXPIRED = "EXPIRED"
REQ_REVOKED = "REVOKED"
REQ_INVALID = "INVALID"
ALL_REQUEST_STATUSES = [
    REQ_PENDING, REQ_APPROVED, REQ_REJECTED, REQ_DEFERRED,
    REQ_NEEDS_CLARIFICATION, REQ_CLOSED, REQ_EXPIRED, REQ_REVOKED, REQ_INVALID,
]

# Scope type constants
SCOPE_ACTION = "ACTION"
SCOPE_TOOL_CALL = "TOOL_CALL"
SCOPE_PATCH_SESSION = "PATCH_SESSION"
SCOPE_FILE_PATH = "FILE_PATH"
SCOPE_COMMIT = "COMMIT"
SCOPE_PROMOTION = "PROMOTION"
SCOPE_SESSION = "SESSION"
ALL_SCOPE_TYPES = [
    SCOPE_ACTION, SCOPE_TOOL_CALL, SCOPE_PATCH_SESSION,
    SCOPE_FILE_PATH, SCOPE_COMMIT, SCOPE_PROMOTION, SCOPE_SESSION,
]

# Auth method constants
AUTH_LOCAL_CONFIG = "LOCAL_CONFIG"
AUTH_MANUAL_RECORD = "MANUAL_RECORD"
AUTH_SIGNED_RECORD = "SIGNED_RECORD"
AUTH_EXTERNAL_ASSERTION = "EXTERNAL_ASSERTION"
AUTH_UNKNOWN = "UNKNOWN"
ALL_AUTH_METHODS = [
    AUTH_LOCAL_CONFIG, AUTH_MANUAL_RECORD, AUTH_SIGNED_RECORD,
    AUTH_EXTERNAL_ASSERTION, AUTH_UNKNOWN,
]

RISK_LEVEL_LOW = "LOW"
RISK_LEVEL_MEDIUM = "MEDIUM"
RISK_LEVEL_HIGH = "HIGH"
RISK_LEVEL_CRITICAL = "CRITICAL"
ALL_RISK_LEVELS = [RISK_LEVEL_LOW, RISK_LEVEL_MEDIUM, RISK_LEVEL_HIGH, RISK_LEVEL_CRITICAL]

SOURCE_COMPONENT = "HumanReviewApproval"

SCHEMA_VERSION = "1.0"


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if val is None:
                result[f] = None
            elif hasattr(val, "__dataclass_fields__"):
                result[f] = to_dict(val)
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


def sha256_dict(data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash_payload(data: dict) -> dict:
    return {k: v for k, v in data.items() if k not in ("request_hash", "decision_hash", "revocation_hash", "clarification_hash", "record_hash", "payload_hash")}


def redact_sensitive_fields(data: dict) -> dict:
    sensitive_keys = {"secret", "password", "token", "api_key", "private_key", "raw_prompt"}
    return {k: v for k, v in data.items() if k.lower() not in sensitive_keys}


# ---- Dataclasses ----

@dataclass
class HumanReviewerIdentity:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_reviewer_identity.schema.json"
    reviewer_id: str = ""
    reviewer_label: str = ""
    reviewer_role: str = ""
    auth_method: str = AUTH_UNKNOWN
    auth_evidence_refs: list[str] = field(default_factory=list)
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanApprovalScope:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_approval_scope.schema.json"
    scope_id: str = ""
    scope_type: str = SCOPE_ACTION
    action_id: str | None = None
    tool_call_id: str | None = None
    patch_session_id: str | None = None
    promotion_request_id: str | None = None
    policy_decision_id: str | None = None
    file_paths: list[str] = field(default_factory=list)
    commit_hashes: list[str] = field(default_factory=list)
    artifact_hashes: list[str] = field(default_factory=list)
    session_id: str | None = None
    allowed_effects: list[str] = field(default_factory=list)
    blocked_effects: list[str] = field(default_factory=list)
    risk_level: str | None = None
    repo_identity_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanReviewRequest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_review_request.schema.json"
    request_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    requested_by: str = ""
    requested_action: str = ""
    requested_effect: str = ""
    risk_level: str = RISK_LEVEL_LOW
    reason: str = ""
    scope: HumanApprovalScope | None = None
    policy_decision_id: str | None = None
    tool_call_id: str | None = None
    patch_session_id: str | None = None
    promotion_request_id: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    status: str = REQ_PENDING
    request_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanApprovalDecision:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_approval_decision.schema.json"
    decision_id: str = ""
    request_id: str = ""
    decided_at: str = ""
    source_component: str = SOURCE_COMPONENT
    reviewer: HumanReviewerIdentity | None = None
    decision: str = DECISION_APPROVED
    reason: str = ""
    scope: HumanApprovalScope | None = None
    expires_at: str | None = None
    no_expiry_reason: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    request_hash: str | None = None
    decision_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanRejectionDecision:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_rejection_decision.schema.json"
    decision_id: str = ""
    request_id: str = ""
    decided_at: str = ""
    source_component: str = SOURCE_COMPONENT
    reviewer: HumanReviewerIdentity | None = None
    decision: str = DECISION_REJECTED
    reason: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    request_hash: str | None = None
    decision_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanDeferralDecision:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_review_deferral.schema.json"
    decision_id: str = ""
    request_id: str = ""
    decided_at: str = ""
    source_component: str = SOURCE_COMPONENT
    reviewer: HumanReviewerIdentity | None = None
    decision: str = DECISION_DEFERRED
    reason: str = ""
    deferred_until: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    request_hash: str | None = None
    decision_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanClarificationRequest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_clarification_request.schema.json"
    clarification_id: str = ""
    request_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    reviewer: HumanReviewerIdentity | None = None
    clarification_question: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    request_hash: str | None = None
    clarification_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanApprovalRevocation:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_approval_revocation.schema.json"
    revocation_id: str = ""
    approval_decision_id: str = ""
    request_id: str = ""
    revoked_at: str = ""
    source_component: str = SOURCE_COMPONENT
    revoked_by: HumanReviewerIdentity | None = None
    reason: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    revocation_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanReviewValidationResult:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_review_validation_result.schema.json"
    validation_id: str = ""
    validated_at: str = ""
    source_component: str = SOURCE_COMPONENT
    approval_decision_id: str | None = None
    request_id: str | None = None
    requested_action: str = ""
    requested_effect: str = ""
    status: str = VALIDATION_INVALID
    reason: str = ""
    matched_scope: bool = False
    expired: bool = False
    revoked: bool = False
    allowed: bool = False
    non_overridable_block_present: bool = False
    replay_or_context_mismatch: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanReviewQueue:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_review_queue.schema.json"
    queue_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    source_component: str = SOURCE_COMPONENT
    pending_requests: list[HumanReviewRequest] = field(default_factory=list)
    resolved_requests: list[str] = field(default_factory=list)
    deferred_requests: list[str] = field(default_factory=list)
    clarification_requests: list[str] = field(default_factory=list)
    queue_version: int = 1
    queue_hash: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanReviewAuditEvent:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_review_audit.schema.json"
    audit_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    request_id: str | None = None
    decision_id: str | None = None
    validation_id: str | None = None
    status: str = ""
    message: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanReviewEvidenceManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "human_review_evidence_manifest.schema.json"
    component_id: str = "AGENTX_HUMAN_REVIEW_APPROVAL"
    validated_commit: str | None = None
    created_at: str = ""
    runtime_artifact_root: str = ".agentx-init/human_review/"
    commands: list[dict] = field(default_factory=list)
    evidence_files: list[dict] = field(default_factory=list)
    evidence_file_hashes: list[dict] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HumanReviewCompletionRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "completion_record.schema.json"
    component_id: str = "AGENTX_HUMAN_REVIEW_APPROVAL"
    component_name: str = "Human Review / Approval Interface"
    status: str = ""
    validated_commit: str = ""
    validated_at: str = ""
    canonical_subdirectory: str = "tools/agentx_evolve/human_review/"
    runtime_artifact_root: str = ".agentx-init/human_review/"
    basis_documents: list[str] = field(default_factory=list)
    commands_run: list[dict] = field(default_factory=list)
    files_created_or_changed: list[str] = field(default_factory=list)
    schemas_created_or_changed: list[str] = field(default_factory=list)
    tests_created_or_changed: list[str] = field(default_factory=list)
    evidence_manifest_path: str = ""
    evidence_manifest_sha256: str = ""
    completion_record_sha256: str = ""
    final_decision: str = ""
    deviations_from_contract: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


# Approved runtime artifact subdirectories
RUNTIME_DIRS = [
    ".agentx-init/human_review/",
]

def human_review_runs_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "human_review"


def from_dict(model_type: type, data: dict) -> object:
    field_types = {}
    if hasattr(model_type, "__dataclass_fields__"):
        for f_name, f_def in model_type.__dataclass_fields__.items():
            field_types[f_name] = f_def.type
    field_values = {}
    for f_name in getattr(model_type, "__dataclass_fields__", {}):
        if f_name in data:
            val = data[f_name]
            f_type = field_types.get(f_name)
            if hasattr(f_type, "__args__"):
                import typing
                args = typing.get_args(f_type)
                if args and hasattr(args[0], "__dataclass_fields__") and isinstance(val, list):
                    val = [from_dict(args[0], v) if isinstance(v, dict) else v for v in val]
                elif args and hasattr(args[0], "__dataclass_fields__") and isinstance(val, dict):
                    val = from_dict(args[0], val)
            elif hasattr(f_type, "__dataclass_fields__") and isinstance(val, dict):
                val = from_dict(f_type, val)
            field_values[f_name] = val
    return model_type(**field_values)


def atomic_write_json(path: Path, payload: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    tmp.replace(path)
    return payload


def append_jsonl(path: Path, payload: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")
    return payload
