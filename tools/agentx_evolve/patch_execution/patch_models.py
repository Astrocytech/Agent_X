from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

SOURCE_COMPONENT = "GovernedPatchExecution"
SPEC_SCHEMA_VERSION = "1.0"

SESSION_STATUS_CREATED = "CREATED"
SESSION_STATUS_BLOCKED = "BLOCKED"
SESSION_STATUS_FAILED = "FAILED"
SESSION_STATUS_ROLLED_BACK = "ROLLED_BACK"
SESSION_STATUS_ROLLBACK_FAILED = "ROLLBACK_FAILED"
SESSION_STATUS_ACCEPTED = "ACCEPTED"

OP_EXACT_EDIT = "EXACT_EDIT"
OP_WRITE_FILE = "WRITE_FILE"
OP_CREATE_FILE = "CREATE_FILE"
OP_DELETE_FILE = "DELETE_FILE"
OP_RENAME_FILE = "RENAME_FILE"
OP_PATCH_TEXT = "PATCH_TEXT"

FINAL_PENDING = "PENDING"
FINAL_ACCEPT = "ACCEPT"
FINAL_REJECT = "REJECT"
FINAL_ROLLBACK = "ROLLBACK"

PATCH_PENDING = "PENDING"
PATCH_APPLIED = "APPLIED"
PATCH_BLOCKED = "BLOCKED"
PATCH_FAILED = "FAILED"
PATCH_DRY_RUN = "DRY_RUN"

TRIGGER_VALIDATION_FAILED = "VALIDATION_FAILED"
TRIGGER_SOURCE_GUARD_FAILED = "SOURCE_GUARD_FAILED"
TRIGGER_PATCH_FAILED = "PATCH_FAILED"
TRIGGER_USER_REQUEST = "USER_REQUEST"
TRIGGER_UNKNOWN = "UNKNOWN"

GUARD_PASS = "PASS"
GUARD_BLOCKED = "BLOCKED"
GUARD_FAILED = "FAILED"

VALIDATION_PASS = "PASS"
VALIDATION_FAILED = "FAILED"
VALIDATION_BLOCKED = "BLOCKED"
VALIDATION_SKIPPED = "SKIPPED"

MODE_DRY_RUN = "DRY_RUN"
MODE_LIVE = "LIVE"

LIFECYCLE_STATES = [
    "CREATED",
    "PROPOSAL_LOADED",
    "GOVERNANCE_CHECKED",
    "POLICY_CHECKED",
    "SANDBOX_CHECKED",
    "DRY_RUN_READY",
    "SNAPSHOT_CREATED",
    "PATCH_APPLIED",
    "SOURCE_GUARD_CHECKED",
    "VALIDATION_RUNNING",
    "VALIDATION_PASSED",
    "VALIDATION_FAILED",
    "ROLLBACK_RUNNING",
    "ROLLED_BACK",
    "ROLLBACK_FAILED",
    "ACCEPTED",
    "FAILED",
    "BLOCKED",
]

FAILURE_TYPES = {
    "PATCH_SESSION_CREATE_FAILED",
    "PATCH_PROPOSAL_INVALID",
    "PATCH_POLICY_BLOCKED",
    "PATCH_SANDBOX_BLOCKED",
    "PATCH_TARGET_OUTSIDE_SCOPE",
    "PATCH_TARGET_L0_BLOCKED",
    "PATCH_TARGET_PROTECTED_BLOCKED",
    "PATCH_TARGET_SYMLINK_ESCAPE",
    "PATCH_LIMIT_EXCEEDED",
    "PATCH_BINARY_BLOCKED",
    "PATCH_ENCODING_FAILED",
    "DRY_RUN_FAILED",
    "ROLLBACK_SNAPSHOT_FAILED",
    "PATCH_APPLY_FAILED",
    "PARTIAL_APPLY_FAILED",
    "SOURCE_INVENTORY_FAILED",
    "SOURCE_CHANGE_GUARD_FAILED",
    "VALIDATION_COMMAND_BLOCKED",
    "VALIDATION_FAILED",
    "ROLLBACK_FAILED",
    "EVIDENCE_WRITE_FAILED",
    "SCHEMA_VALIDATION_FAILED",
    "LOCK_CONFLICT",
    "UNKNOWN_PATCH_EXECUTION_ERROR",
}

class PatchLimitError(Exception):
    def __init__(self, message: str = "", code: str = ""):
        super().__init__(message)
        self.code = code


PLE_SIZE_EXCEEDED = "SIZE_EXCEEDED"
PLE_FILES_EXCEEDED = "FILES_EXCEEDED"


DEFAULT_LIMITS = {
    "max_changed_files_per_session": 5,
    "max_patch_operations_per_session": 20,
    "max_single_file_bytes": 1048576,
    "max_patch_text_bytes": 262144,
    "max_total_snapshot_bytes": 10485760,
    "max_validation_runtime_seconds": 120,
    "max_session_runtime_seconds": 300,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    try:
        data = path.read_bytes()
        return hashlib.sha256(data).hexdigest()
    except (OSError, FileNotFoundError):
        return None


def to_dict(obj: object) -> dict:
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
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


@dataclass
class PatchOperation:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "patch_operation.schema.json"
    operation_id: str = ""
    operation_type: str = OP_EXACT_EDIT
    target_path: str = ""
    old_text: str | None = None
    new_text: str | None = None
    content: str | None = None
    allow_create: bool = False
    allow_delete: bool = False
    expected_before_hash: str | None = None
    requires_rollback_snapshot: bool = True
    approved: bool = False


@dataclass
class PatchApplication:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "patch_application.schema.json"
    application_id: str = ""
    session_id: str = ""
    proposal_id: str | None = None
    governance_decision_id: str | None = None
    policy_decision_id: str | None = None
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    mode: str = MODE_DRY_RUN
    operations: list[PatchOperation] = field(default_factory=list)
    target_paths: list[str] = field(default_factory=list)
    status: str = PATCH_PENDING
    before_hashes: dict[str, str] = field(default_factory=dict)
    after_hashes: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PatchResult:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "patch_result.schema.json"
    result_id: str = ""
    session_id: str = ""
    application_id: str = ""
    mode: str = MODE_DRY_RUN
    status: str = PATCH_PENDING
    changed_paths: list[str] = field(default_factory=list)
    created_paths: list[str] = field(default_factory=list)
    deleted_paths: list[str] = field(default_factory=list)
    before_hashes: dict[str, str] = field(default_factory=dict)
    after_hashes: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RollbackSnapshot:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "rollback_snapshot.schema.json"
    snapshot_id: str = ""
    session_id: str = ""
    timestamp: str = ""
    source_component: str = "RollbackManager"
    snapshot_root: str = ""
    files: list[dict] = field(default_factory=list)
    status: str = "CREATED"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RollbackRecord:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "rollback_record.schema.json"
    rollback_id: str = ""
    session_id: str = ""
    snapshot_id: str = ""
    timestamp: str = ""
    source_component: str = "RollbackManager"
    trigger: str = TRIGGER_UNKNOWN
    restored_files: list[str] = field(default_factory=list)
    removed_created_files: list[str] = field(default_factory=list)
    verification_status: str = GUARD_PASS
    status: str = SESSION_STATUS_ROLLED_BACK
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ImplementationSession:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "implementation_session.schema.json"
    session_id: str = ""
    proposal_id: str | None = None
    governance_decision_id: str | None = None
    policy_decision_id: str | None = None
    sandbox_decision_ids: list[str] = field(default_factory=list)
    dry_run_id: str | None = None
    rollback_snapshot_id: str | None = None
    patch_application_id: str | None = None
    source_inventory_before_id: str | None = None
    source_inventory_after_id: str | None = None
    source_change_guard_id: str | None = None
    validation_result_id: str | None = None
    rollback_record_id: str | None = None
    target_paths: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    lifecycle_state: str = "CREATED"
    status: str = SESSION_STATUS_CREATED
    final_decision: str = FINAL_PENDING
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class SourceChangeGuardResult:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "source_change_guard.schema.json"
    guard_id: str = ""
    session_id: str = ""
    timestamp: str = ""
    source_component: str = "SourceChangeGuard"
    approved_paths: list[str] = field(default_factory=list)
    actual_changed_paths: list[str] = field(default_factory=list)
    unexpected_paths: list[str] = field(default_factory=list)
    missing_expected_paths: list[str] = field(default_factory=list)
    forbidden_paths: list[str] = field(default_factory=list)
    status: str = GUARD_PASS
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ImplementationValidationGateResult:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "implementation_validation_gate.schema.json"
    validation_gate_id: str = ""
    session_id: str = ""
    timestamp: str = ""
    source_component: str = "ImplementationValidationGate"
    commands_requested: list[str] = field(default_factory=list)
    commands_allowed: list[str] = field(default_factory=list)
    commands_blocked: list[str] = field(default_factory=list)
    validation_status: str = VALIDATION_SKIPPED
    requires_rollback: bool = False
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PatchExecutionDecision:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "patch_execution_decision.schema.json"
    decision_id: str = ""
    session_id: str | None = None
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    decision: str = FINAL_PENDING
    reason: str = ""
    required_actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PatchExecutionAuditEvent:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "patch_execution_audit.schema.json"
    audit_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    session_id: str = ""
    decision: str = ""
    artifacts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DryRunResult:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "dry_run_result.schema.json"
    dry_run_id: str = ""
    session_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    would_change_paths: list[str] = field(default_factory=list)
    would_create_paths: list[str] = field(default_factory=list)
    would_delete_paths: list[str] = field(default_factory=list)
    sandbox_decision_ids: list[str] = field(default_factory=list)
    policy_decision_id: str | None = None
    rollback_required: bool = True
    validation_plan: list[str] = field(default_factory=list)
    status: str = GUARD_PASS
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class SourceInventory:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "source_inventory.schema.json"
    inventory_id: str = ""
    session_id: str = ""
    timestamp: str = ""
    source_component: str = "SourceChangeGuard"
    scope: str = "BEFORE"
    tracked_paths: list[str] = field(default_factory=list)
    path_hashes: dict[str, str] = field(default_factory=dict)
    git_status_short: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class TemporaryPolicyBridge:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "temporary_policy_bridge.schema.json"
    policy_bridge_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    mode: str = "TEMPORARY_FAIL_CLOSED"
    allowed_roles: list[str] = field(default_factory=list)
    allowed_operations: list[str] = field(default_factory=lambda: [OP_EXACT_EDIT, OP_WRITE_FILE, OP_CREATE_FILE, OP_PATCH_TEXT])
    allowed_paths: list[str] = field(default_factory=list)
    blocked_paths: list[str] = field(default_factory=list)
    requires_governance: bool = True
    requires_rollback: bool = True
    status: str = "ACTIVE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ApprovedMutation:
    schema_version: str = "1.0"
    schema_id: str = "approved_mutation.schema.json"
    mutation_id: str = ""
    target_path: str = ""
    allowed_change_types: list[str] = field(default_factory=lambda: ["UPDATE", "CREATE"])
    governance_decision_id: str = ""
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mutation_id": self.mutation_id,
            "target_path": self.target_path,
            "allowed_change_types": self.allowed_change_types,
            "governance_decision_id": self.governance_decision_id,
        }

    def allows_path(self, path: str) -> bool:
        return path == self.target_path or path.startswith(self.target_path.rstrip("/") + "/")

    def allows_change_type(self, change_type: str) -> bool:
        return change_type in self.allowed_change_types


@dataclass
class MutationAllowlist:
    schema_version: str = "1.0"
    schema_id: str = "mutation_allowlist.schema.json"
    allowlist_id: str = ""
    timestamp: str = ""
    governance_decision_id: str = ""
    mutations: list[ApprovedMutation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"mutations": [m.to_dict() for m in self.mutations]} if self.mutations else {}

    def allows_mutation(self, target_path: str, change_type: str) -> bool:
        return any(
            m.allows_path(target_path) and m.allows_change_type(change_type)
            for m in self.mutations
        )

    def is_empty(self) -> bool:
        return len(self.mutations) == 0


@dataclass
class PatchLimits:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "patch_limits.schema.json"
    limits_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    max_changed_files_per_session: int = 5
    max_patch_operations_per_session: int = 20
    max_single_file_bytes: int = 1048576
    max_patch_text_bytes: int = 262144
    max_total_snapshot_bytes: int = 10485760
    max_validation_runtime_seconds: int = 120
    max_session_runtime_seconds: int = 300
    status: str = "ACTIVE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PatchCandidate:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "patch_candidate.schema.json"
    candidate_id: str = ""
    proposal_id: str = ""
    context_packet_id: str = ""
    prompt_contract_id: str = ""
    risk_classification_id: str = ""
    governance_decision_id: str = ""
    session_id: str = ""
    created_at: str = ""
    source_commit: str = ""
    operations: list[PatchOperation] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=list)
    blocked_paths: list[str] = field(default_factory=list)
    rollback_plan: str = ""
    status: str = "CREATED"
    validation_status: str = "NOT_RUN"
    validation_commands: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        from dataclasses import asdict
        d = asdict(self)
        d["operations"] = [op.to_dict() if hasattr(op, "to_dict") else op for op in d["operations"]]
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatchCandidate:
        ops = [PatchOperation(**op) if isinstance(op, dict) else op for op in data.get("operations", [])]
        data["operations"] = ops
        return cls(**data)
