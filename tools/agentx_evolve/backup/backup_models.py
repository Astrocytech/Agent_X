from __future__ import annotations
import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---- Constants ----

SCHEMA_VERSION = "1.0"
SOURCE_COMPONENT = "BackupDisasterRecovery"
COMPONENT_ID = "AGENTX_BACKUP_DISASTER_RECOVERY"
COMPONENT_NAME = "Backup / Disaster Recovery Layer"

CANONICAL_SUBDIRECTORY = "tools/agentx_evolve/backup/"
CANONICAL_SCHEMA_SUBDIRECTORY = "tools/agentx_evolve/schemas/"
CANONICAL_TEST_SUBDIRECTORY = "tools/agentx_evolve/tests/"
RUNTIME_ARTIFACT_ROOT = ".agentx-init/backups/"
SNAPSHOT_STORAGE_ROOT = ".agentx-init/backups/snapshots/"

BACKUP_STATUS_CREATED = "CREATED"
BACKUP_STATUS_STAGED = "STAGED"
BACKUP_STATUS_VERIFIED = "VERIFIED"
BACKUP_STATUS_FAILED = "FAILED"
BACKUP_STATUS_INVALID = "INVALID"
BACKUP_STATUS_BLOCKED = "BLOCKED"
ALL_BACKUP_STATUSES = [BACKUP_STATUS_CREATED, BACKUP_STATUS_STAGED, BACKUP_STATUS_VERIFIED, BACKUP_STATUS_FAILED, BACKUP_STATUS_INVALID, BACKUP_STATUS_BLOCKED]

RESTORE_STATUS_PLANNED = "PLANNED"
RESTORE_STATUS_DRY_RUN = "DRY_RUN"
RESTORE_STATUS_BLOCKED = "BLOCKED"
RESTORE_STATUS_RESTORED = "RESTORED"
RESTORE_STATUS_FAILED = "FAILED"
ALL_RESTORE_STATUSES = [RESTORE_STATUS_PLANNED, RESTORE_STATUS_DRY_RUN, RESTORE_STATUS_BLOCKED, RESTORE_STATUS_RESTORED, RESTORE_STATUS_FAILED]

DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
DECISION_DRY_RUN_ONLY = "DRY_RUN_ONLY"
ALL_DECISIONS = [DECISION_ALLOW, DECISION_BLOCK, DECISION_NEEDS_GOVERNANCE, DECISION_NEEDS_APPROVAL, DECISION_DRY_RUN_ONLY]

BACKUP_SCOPE_RUNTIME = "RUNTIME"
BACKUP_SCOPE_SOURCE = "SOURCE"
BACKUP_SCOPE_CONFIG = "CONFIG"
BACKUP_SCOPE_EVIDENCE = "EVIDENCE"
BACKUP_SCOPE_RELEASE = "RELEASE"
ALL_BACKUP_SCOPES = [BACKUP_SCOPE_RUNTIME, BACKUP_SCOPE_SOURCE, BACKUP_SCOPE_CONFIG, BACKUP_SCOPE_EVIDENCE, BACKUP_SCOPE_RELEASE]

RESTORE_MODE_DRY_RUN = "DRY_RUN"
RESTORE_MODE_RUNTIME_ONLY = "RUNTIME_ONLY"
RESTORE_MODE_SOURCE_RESTORE = "SOURCE_RESTORE"
RESTORE_MODE_RELEASE_RESTORE = "RELEASE_RESTORE"
RESTORE_MODE_FULL_RECOVERY = "FULL_RECOVERY"
ALL_RESTORE_MODES = [RESTORE_MODE_DRY_RUN, RESTORE_MODE_RUNTIME_ONLY, RESTORE_MODE_SOURCE_RESTORE, RESTORE_MODE_RELEASE_RESTORE, RESTORE_MODE_FULL_RECOVERY]

BACKUP_FAILURE_POLICY_DENIED = "BACKUP_POLICY_DENIED"
BACKUP_FAILURE_SANDBOX_DENIED = "BACKUP_SANDBOX_DENIED"
BACKUP_FAILURE_HASH_MISMATCH = "BACKUP_HASH_MISMATCH"
BACKUP_FAILURE_MANIFEST_INVALID = "BACKUP_MANIFEST_INVALID"
BACKUP_FAILURE_SNAPSHOT_MISSING = "BACKUP_SNAPSHOT_MISSING"
BACKUP_FAILURE_SNAPSHOT_PARTIAL = "BACKUP_SNAPSHOT_PARTIAL"
BACKUP_FAILURE_RESTORE_BLOCKED = "BACKUP_RESTORE_BLOCKED"
BACKUP_FAILURE_RETENTION_BLOCKED = "BACKUP_RETENTION_BLOCKED"
BACKUP_FAILURE_LOCK_HELD = "BACKUP_LOCK_HELD"
BACKUP_FAILURE_SECRET_EXCLUDED = "BACKUP_SECRET_EXCLUDED"
BACKUP_FAILURE_UNKNOWN = "BACKUP_UNKNOWN_FAILURE"
ALL_BACKUP_FAILURES = [BACKUP_FAILURE_POLICY_DENIED, BACKUP_FAILURE_SANDBOX_DENIED, BACKUP_FAILURE_HASH_MISMATCH, BACKUP_FAILURE_MANIFEST_INVALID, BACKUP_FAILURE_SNAPSHOT_MISSING, BACKUP_FAILURE_SNAPSHOT_PARTIAL, BACKUP_FAILURE_RESTORE_BLOCKED, BACKUP_FAILURE_RETENTION_BLOCKED, BACKUP_FAILURE_LOCK_HELD, BACKUP_FAILURE_SECRET_EXCLUDED, BACKUP_FAILURE_UNKNOWN]

LOCK_STATUS_ACQUIRED = "ACQUIRED"
LOCK_STATUS_RELEASED = "RELEASED"
LOCK_STATUS_STALE = "STALE"
LOCK_STATUS_BLOCKED = "BLOCKED"
ALL_LOCK_STATUSES = [LOCK_STATUS_ACQUIRED, LOCK_STATUS_RELEASED, LOCK_STATUS_STALE, LOCK_STATUS_BLOCKED]

CLI_STATUS_SUCCESS = "SUCCESS"
CLI_STATUS_BLOCKED = "BLOCKED"
CLI_STATUS_FAILED = "FAILED"
CLI_STATUS_INVALID = "INVALID"
ALL_CLI_STATUSES = [CLI_STATUS_SUCCESS, CLI_STATUS_BLOCKED, CLI_STATUS_FAILED, CLI_STATUS_INVALID]

VALIDATION_STATUS_PASS = "PASS"
VALIDATION_STATUS_PARTIAL = "PARTIAL"
VALIDATION_STATUS_FAIL = "FAIL"
VALIDATION_STATUS_BLOCKED = "BLOCKED"
VALIDATION_STATUS_NOT_CHECKED = "NOT CHECKED"
VALIDATION_STATUS_NOT_RUN = "NOT RUN"
VALIDATION_STATUS_NOT_APPLICABLE = "NOT APPLICABLE"
VALIDATION_STATUS_DEFERRED = "DEFERRED SAFELY"
ALL_VALIDATION_STATUSES = [VALIDATION_STATUS_PASS, VALIDATION_STATUS_PARTIAL, VALIDATION_STATUS_FAIL, VALIDATION_STATUS_BLOCKED, VALIDATION_STATUS_NOT_CHECKED, VALIDATION_STATUS_NOT_RUN, VALIDATION_STATUS_NOT_APPLICABLE, VALIDATION_STATUS_DEFERRED]

GIT_STATUS_CLEAN = "CLEAN"
GIT_STATUS_DIRTY = "DIRTY"
GIT_STATUS_UNKNOWN = "UNKNOWN"
ALL_GIT_STATUSES = [GIT_STATUS_CLEAN, GIT_STATUS_DIRTY, GIT_STATUS_UNKNOWN]

# ---- Helpers ----

def utc_now_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond:06d}Z"

def new_id(prefix: str = "backup") -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

def to_dict(obj: Any) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            elif hasattr(val, "__dataclass_fields__"):
                result[f] = to_dict(val)
            elif val is not None:
                result[f] = val
        return result
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if v is not None}
    return {}

def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sha256_bytes(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))

def sha256_dict(data: dict) -> str:
    return sha256_bytes(canonical_json(data))

def safe_relative_path(path: Path, root: Path) -> str:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        rp = resolved_path.relative_to(resolved_root)
        return rp.as_posix()
    except ValueError:
        raise ValueError(f"Path {path} is not under root {root}")

def redact_backup_value(value: object) -> object:
    if isinstance(value, str):
        v = str(value)
        v = re.sub(r"(API_KEY\s*=\s*).*", r"\1***REDACTED***", v, flags=re.IGNORECASE)
        v = re.sub(r"(SECRET\s*=\s*).*", r"\1***REDACTED***", v, flags=re.IGNORECASE)
        v = re.sub(r"(TOKEN\s*=\s*).*", r"\1***REDACTED***", v, flags=re.IGNORECASE)
        v = re.sub(r"(PASSWORD\s*=\s*).*", r"\1***REDACTED***", v, flags=re.IGNORECASE)
        return v
    if isinstance(value, dict):
        return {k: redact_backup_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_backup_value(v) for v in value]
    return value

def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path

def write_jsonl_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text().splitlines(keepends=True) if path.exists() else []
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        for line in existing:
            f.write(line)
        f.write(canonical_json(data) + "\n")
    tmp.replace(path)
    return path

def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent

def manifests_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "manifests"

def snapshots_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "snapshots"

def staging_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "staging"

def restore_plans_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "restore_plans"

def disaster_recovery_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "disaster_recovery"

def evidence_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "evidence"

def locks_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "locks"

def catalog_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "backups" / "catalog"

def is_secret_like_path(path: Path, excluded_secret_patterns: list[str] | None = None) -> bool:
    name = path.name
    if name in (".env",):
        return True
    if name.endswith((".pem", ".key", ".p12", ".pfx")):
        return True
    if "token" in name.lower() or "secret" in name.lower() or "credential" in name.lower():
        return True
    if name == "credentials.json":
        return True
    if excluded_secret_patterns:
        for pat in excluded_secret_patterns:
            if re.search(pat, str(path)):
                return True
    return False

def compute_repo_root_fingerprint(repo_root: Path) -> str:
    git_dir = repo_root / ".git"
    if git_dir.is_dir():
        return sha256_text(repo_root.resolve().as_posix())
    return sha256_text(repo_root.resolve().as_posix())

def check_backup_format_compatibility(manifest: "BackupManifest", catalog: "BackupCatalog") -> dict:
    issues = []
    if manifest.schema_version != catalog.backup_format_version:
        issues.append(f"Backup format version mismatch: manifest {manifest.schema_version} vs catalog {catalog.backup_format_version}")
    if manifest.source_component != SOURCE_COMPONENT:
        issues.append(f"Source component mismatch: {manifest.source_component} vs {SOURCE_COMPONENT}")
    return {"compatible": len(issues) == 0, "issues": issues}

def cleanup_stale_staging_snapshots(repo_root: Path, policy: "BackupRetentionPolicy", context: dict) -> dict:
    staging = staging_dir(repo_root)
    if not staging.exists():
        return {"deleted": [], "errors": []}
    deleted = []
    errors = []
    for entry in staging.iterdir():
        if entry.is_dir() and entry.name.endswith(".staging"):
            try:
                for f in entry.rglob("*"):
                    f.unlink()
                entry.rmdir()
                deleted.append(entry.name)
            except Exception as e:
                errors.append(f"Failed to clean {entry.name}: {e}")
    return {"deleted": deleted, "errors": errors}

# ---- Whitelisted backup/restore/DR commands ----

BACKUP_ALLOWED_COMMANDS = [
    "build_backup_manifest",
    "write_backup_manifest",
    "finalize_manifest_hash",
    "create_backup_snapshot",
    "verify_backup_snapshot",
    "create_restore_decision",
    "plan_restore",
    "execute_restore_plan",
    "build_disaster_recovery_plan",
    "apply_backup_retention_policy",
    "cleanup_stale_staging_snapshots",
    "load_backup_catalog",
    "write_backup_catalog",
    "update_catalog_for_manifest",
    "mark_backup_deleted",
    "record_stale_staging_path",
    "acquire_backup_lock",
    "release_backup_lock",
    "is_lock_active",
    "build_restore_preflight_record",
    "start_restore_transaction",
    "record_restore_transaction_step",
    "complete_restore_transaction",
]

BACKUP_FORBIDDEN_COMMAND_PATTERNS = [
    "shell", "exec", "popen", "system", "subprocess",
    "git push", "git commit", "git tag",
    "upload", "publish", "npm publish", "twine upload",
]

# ---- Dataclasses ----

@dataclass
class BackupPolicy:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_policy.schema.json"
    policy_id: str = ""
    allowed_backup_roots: list[str] = field(default_factory=lambda: ["."])
    allowed_restore_roots: list[str] = field(default_factory=lambda: [".agentx-init"])
    excluded_paths: list[str] = field(default_factory=lambda: [".git", ".agentx-init/backups", ".venv", "node_modules", "__pycache__"])
    excluded_globs: list[str] = field(default_factory=lambda: ["**/__pycache__/**", "**/.pytest_cache/**", "**/*.pyc", "**/.DS_Store", "**/.env", "**/.env.*"])
    excluded_secret_patterns: list[str] = field(default_factory=list)
    require_git_status: bool = True
    require_hashes: bool = True
    require_manifest_validation: bool = True
    require_restore_dry_run: bool = True
    allow_source_backup: bool = False
    allow_source_restore: bool = False
    allow_runtime_restore: bool = True
    allow_release_restore: bool = False
    allow_secret_backup_plaintext: bool = False
    retention_policy_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupRetentionPolicy:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_retention_policy.schema.json"
    retention_policy_id: str = ""
    keep_latest_verified_count: int = 3
    keep_minimum_total_count: int = 2
    max_snapshot_age_days: int | None = 90
    protect_release_linked: bool = True
    protect_manually_marked: bool = True
    dry_run: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupFileRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_file_record.schema.json"
    relative_path: str = ""
    original_path: str = ""
    backup_path: str = ""
    file_size_bytes: int = 0
    sha256: str | None = None
    included: bool = False
    exclusion_reason: str | None = None
    path_type: str = "file"
    mode: str | None = None
    mtime_ns: int | None = None
    symlink_target: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupSnapshotRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_snapshot_record.schema.json"
    snapshot_id: str = ""
    backup_id: str = ""
    snapshot_path: str = ""
    staging_path: str | None = None
    finalized: bool = False
    file_count: int = 0
    total_size_bytes: int = 0
    snapshot_index_path: str = ""
    snapshot_index_sha256: str | None = None
    protected: bool = False
    release_ref: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupSnapshotIndex:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_snapshot_index.schema.json"
    snapshot_index_id: str = ""
    backup_id: str = ""
    created_at: str = ""
    snapshot_path: str = ""
    file_records: list[BackupFileRecord] = field(default_factory=list)
    snapshot_sha256: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_manifest.schema.json"
    backup_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    repo_root: str = ""
    git_commit: str | None = None
    git_branch: str | None = None
    git_status_summary: str = GIT_STATUS_UNKNOWN
    backup_scope: list[str] = field(default_factory=list)
    snapshot_path: str = ""
    snapshot_record: BackupSnapshotRecord | None = None
    file_records: list[BackupFileRecord] = field(default_factory=list)
    excluded_records: list[BackupFileRecord] = field(default_factory=list)
    manifest_sha256: str | None = None
    snapshot_sha256: str | None = None
    policy_decision_id: str | None = None
    sandbox_decision_ids: list[str] = field(default_factory=list)
    promotion_refs: list[str] = field(default_factory=list)
    monitoring_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    status: str = BACKUP_STATUS_CREATED
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupVerificationResult:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_verification_result.schema.json"
    verification_id: str = ""
    backup_id: str = ""
    verified_at: str = ""
    manifest_path: str = ""
    snapshot_path: str = ""
    status: str = VALIDATION_STATUS_NOT_CHECKED
    files_checked: int = 0
    files_passed: int = 0
    files_failed: int = 0
    hash_mismatches: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    partial_snapshot_detected: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class RestoreRequest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "restore_request.schema.json"
    restore_request_id: str = ""
    requested_at: str = ""
    requested_by_role: str = ""
    backup_id: str = ""
    restore_mode: str = RESTORE_MODE_DRY_RUN
    target_root: str = ""
    dry_run: bool = True
    requested_paths: list[str] = field(default_factory=list)
    policy_decision_id: str | None = None
    governance_decision_id: str | None = None
    human_approval_id: str | None = None
    promotion_decision_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class RestoreDecision:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "restore_decision.schema.json"
    restore_decision_id: str = ""
    restore_request_id: str = ""
    decided_at: str = ""
    decision: str = DECISION_BLOCK
    reason: str = ""
    required_authorities: list[str] = field(default_factory=list)
    missing_authorities: list[str] = field(default_factory=list)
    destructive_actions_allowed: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class RestorePlan:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "restore_plan.schema.json"
    restore_plan_id: str = ""
    restore_request_id: str = ""
    backup_id: str = ""
    created_at: str = ""
    restore_mode: str = RESTORE_MODE_DRY_RUN
    dry_run: bool = True
    restore_decision_id: str | None = None
    files_to_restore: list[str] = field(default_factory=list)
    files_to_skip: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    destructive_actions: list[str] = field(default_factory=list)
    required_approvals: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    status: str = RESTORE_STATUS_PLANNED
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class RestoreResult:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "restore_result.schema.json"
    restore_result_id: str = ""
    restore_plan_id: str = ""
    backup_id: str = ""
    completed_at: str = ""
    status: str = RESTORE_STATUS_BLOCKED
    restored_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class DisasterRecoveryPlan:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "disaster_recovery_plan.schema.json"
    disaster_recovery_plan_id: str = ""
    created_at: str = ""
    trigger: str = ""
    selected_backup_id: str | None = None
    recovery_steps: list[str] = field(default_factory=list)
    validation_steps: list[str] = field(default_factory=list)
    rollback_steps: list[str] = field(default_factory=list)
    required_approvals: list[str] = field(default_factory=list)
    rejected_backup_ids: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupAuditEvent:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_audit_event.schema.json"
    audit_id: str = ""
    timestamp: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    backup_id: str | None = None
    restore_request_id: str | None = None
    status: str = ""
    message: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupEvidenceManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_evidence_manifest.schema.json"
    evidence_manifest_id: str = ""
    component_id: str = COMPONENT_ID
    created_at: str = ""
    backup_id: str | None = None
    restore_request_id: str | None = None
    evidence_files: list[str] = field(default_factory=list)
    evidence_file_hashes: dict[str, str] = field(default_factory=dict)
    runtime_artifacts: list[str] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    final_status: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupCompletionRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_completion_record.schema.json"
    component_id: str = COMPONENT_ID
    component_name: str = COMPONENT_NAME
    status: str = ""
    validated_commit: str | None = None
    validated_at: str = ""
    backup_ids: list[str] = field(default_factory=list)
    restore_plan_ids: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    hash_refs: list[dict] = field(default_factory=list)
    commands_run: list[dict] = field(default_factory=list)
    validated_capabilities: list[str] = field(default_factory=list)
    deviations_from_contract: list[dict] = field(default_factory=list)
    unresolved_risks: list[dict] = field(default_factory=list)
    final_decision: str = "NOT DONE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupCatalog:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_catalog.schema.json"
    catalog_id: str = ""
    updated_at: str = ""
    project_id: str = ""
    repo_root_fingerprint: str = ""
    backup_format_version: str = "1.0"
    snapshots: list[dict] = field(default_factory=list)
    latest_verified_backup_id: str | None = None
    protected_backup_ids: list[str] = field(default_factory=list)
    deleted_backup_ids: list[str] = field(default_factory=list)
    stale_staging_paths: list[str] = field(default_factory=list)
    catalog_sha256: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupLockRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_lock_record.schema.json"
    lock_record_id: str = ""
    lock_name: str = ""
    lock_id: str = ""
    acquired_at: str = ""
    released_at: str | None = None
    stale_after_seconds: int = 1800
    owner_component: str = SOURCE_COMPONENT
    status: str = LOCK_STATUS_ACQUIRED
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class RestorePreflightRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "restore_preflight_record.schema.json"
    preflight_id: str = ""
    restore_request_id: str = ""
    backup_id: str = ""
    checked_at: str = ""
    backup_format_compatible: bool = False
    project_identity_match: bool = False
    schema_versions_supported: bool = False
    verified_backup: bool = False
    target_paths_sandboxed: bool = False
    git_state_safe: bool = False
    promotion_gate_passed: bool = False
    destructive_actions_detected: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class RestoreTransactionRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "restore_transaction_record.schema.json"
    transaction_id: str = ""
    restore_plan_id: str = ""
    backup_id: str = ""
    started_at: str = ""
    completed_at: str | None = None
    mode: str = ""
    pre_restore_checkpoint_path: str | None = None
    touched_paths: list[str] = field(default_factory=list)
    restored_paths: list[str] = field(default_factory=list)
    skipped_paths: list[str] = field(default_factory=list)
    rollback_available: bool = False
    rollback_notes: list[str] = field(default_factory=list)
    status: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass
class BackupCliResult:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "backup_cli_result.schema.json"
    command_name: str = ""
    command_id: str = ""
    started_at: str = ""
    completed_at: str = ""
    status: str = CLI_STATUS_SUCCESS
    exit_code: int = 0
    message: str = ""
    data: dict = field(default_factory=dict)
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
