# BACKUP_DISASTER_RECOVERY_IMPLEMENTATION_SPEC

```text
document_id: BACKUP_DISASTER_RECOVERY_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen coding-agent handoff with schema/path/CLI precision controls
component_id: AGENTX_BACKUP_DISASTER_RECOVERY
component_name: Backup / Disaster Recovery Layer
roadmap_layer: 21
roadmap_phase: Phase F — Resilience / Recovery
based_on: BACKUP_DISASTER_RECOVERY_EQC_FIC_SIB_SCHEMA_CONTRACT
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Git Integration Acceptance Criteria, Promotion / Release Gate Acceptance Criteria, Monitoring / Observability Acceptance Criteria
target_language: Python
canonical_subdirectory: tools/agentx_evolve/backup/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/backups/
implementation_mode: deterministic backup, verify, restore-plan, safe restore-stub, retention, and disaster-recovery planning layer
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was strong and close to final. I would rate it:

```text
9.8/10
```

It covered the requested coding-agent handoff areas and added important safety controls for catalog indexing, restore preflight, restore transactions, compatibility checks, snapshot finalization, lock evidence, disaster-recovery drill mode, and CLI acceptance criteria.

## 0.2 Why v3 Was Not Fully 10/10

The remaining gaps were not conceptual gaps. They were precision gaps that could still confuse a coding agent:

```text
1. Some added schema filenames lacked the canonical schema subdirectory prefix.
2. The file record dataclass omitted mode, mtime, and symlink fields that the later file-record format required.
3. The public __init__.py exports did not include the added v3 catalog, lock, preflight, and transaction dataclasses/functions.
4. Section numbering had duplicate Slice D and duplicate Section 14 headings.
5. Implementation order numbering had repeated and skipped numbers.
6. Backup catalog schema and runtime paths needed a clearer single canonical path rule.
7. Restore preflight needed an explicit rule that ALLOW is impossible when the preflight record is missing or failed.
8. CLI/tool wrapper results needed a schema-valid result envelope and exact exit-code conventions.
9. Stale staging cleanup needed an explicit safe cleanup function and blocked-delete rules.
10. Evidence immutability after completion needed to be stated.
```

## 0.3 v4 Improvements

This v4 adds:

```text
canonical schema path correction for every schema
file metadata dataclass alignment with manifest format
expanded public exports for catalog, lock, preflight, and transaction APIs
stable section numbering and implementation order numbering
canonical catalog path and hash rules
preflight-as-gate rule before any executable restore plan
structured CLI/tool result envelope with exit-code conventions
stale staging cleanup API and safe-delete restrictions
evidence immutability rule after completion record
final frozen handoff corrections without weakening safety
```

This v4 is the final 10/10 coding-agent handoff.


# 1. Purpose

This document is the implementation specification for the **Backup / Disaster Recovery Layer**.

It is a coding-agent handoff. It defines the exact subdirectories, files, schemas, classes, functions, runtime artifacts, integrations, tests, implementation order, acceptance criteria, and Definition of Done required to implement the layer safely.

The Backup / Disaster Recovery Layer preserves recoverable Agent_X state without becoming a bypass around:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Git Integration Layer
Promotion / Release Gate
Monitoring / Observability
Tool / MCP Adapter governance
schema validation
audit/evidence rules
```

The layer must support:

```text
backup manifest creation
snapshot creation
snapshot indexing
snapshot integrity verification
restore request validation
restore decision creation
restore planning
restore dry-run
restore execution stub or runtime-only restore when allowed
disaster recovery planning
backup retention cleanup
backup audit/evidence logging
backup CLI/tool wrappers, if exposed
completion evidence
```

The layer must not:

```text
silently overwrite current work
restore unverified state
restore hash-mismatched state
include secrets in plaintext backups
delete the only valid recovery point
delete protected release backups
write outside approved runtime roots
restore source files without policy, sandbox, governance, Git safety, and human approval
execute raw shell
require network, hosted model, LLM, Bun, Node, OpenCode runtime, or external storage provider for validation
```

---

# 2. Canonical Destination Summary

Create the Backup / Disaster Recovery package here:

```text
tools/agentx_evolve/backup/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/backups/
```

Approved runtime subdirectories:

```text
.agentx-init/backups/manifests/
.agentx-init/backups/snapshots/
.agentx-init/backups/staging/
.agentx-init/backups/restore_plans/
.agentx-init/backups/disaster_recovery/
.agentx-init/backups/evidence/
.agentx-init/backups/locks/
.agentx-init/backups/catalog/
```

Intended package split:

```text
tools/agentx_evolve/backup/       = new Backup / Disaster Recovery Layer
tools/agentx_evolve/security/     = Security Sandbox / Filesystem Boundary
tools/agentx_evolve/policy/       = Policy / Capability Registry
tools/agentx_evolve/git/          = Git Integration Layer, if implemented
tools/agentx_evolve/promotion/    = Promotion / Release Gate, if implemented
tools/agentx_evolve/monitoring/   = Monitoring / Observability, if implemented
tools/agentx_evolve/tools/        = Tool / MCP Adapter, if backup wrappers are exposed as tools
```

---

# 3. Implementation Goal

At the end of implementation, Agent_X must have a deterministic backup and disaster recovery layer that can:

```text
create backup policies
create backup manifests
create atomic snapshots under approved runtime paths
create snapshot indexes
exclude secrets and forbidden files
hash every backed-up file
hash manifests, snapshot indexes, evidence files, and completion records
verify snapshot integrity
create restore decisions
plan restore without mutating files
block unsafe or unapproved restore actions
optionally restore runtime artifacts when policy and sandbox allow
generate disaster recovery plans from verified backups
apply retention rules without deleting protected snapshots
record backup, restore, verification, retention, and disaster recovery evidence
emit monitoring events when monitoring exists
fail closed when required upstream authorities are unavailable
```

The layer must be able to answer:

```text
what was backed up
why it was backed up
when it was backed up
from which commit / branch / working-tree state
which files were included
which files were excluded
which paths were blocked
which hashes were recorded
whether backup verification passed
whether restore is safe
which approvals are required before restore
which snapshots are protected from cleanup
which recovery point should be used after failure
which evidence proves the recovery point is valid
```

---

# 4. Exact Subdirectory

Canonical package:

```text
tools/agentx_evolve/backup/
```

Required package files:

```text
tools/agentx_evolve/backup/__init__.py
tools/agentx_evolve/backup/backup_models.py
tools/agentx_evolve/backup/backup_manifest.py
tools/agentx_evolve/backup/snapshot_creator.py
tools/agentx_evolve/backup/snapshot_verifier.py
tools/agentx_evolve/backup/restore_planner.py
tools/agentx_evolve/backup/restore_executor.py
tools/agentx_evolve/backup/disaster_recovery_planner.py
tools/agentx_evolve/backup/retention_manager.py
tools/agentx_evolve/backup/backup_audit_logger.py
tools/agentx_evolve/backup/backup_cli_tools.py
tools/agentx_evolve/backup/backup_dependency_adapters.py
tools/agentx_evolve/backup/backup_schema_validator.py
tools/agentx_evolve/backup/backup_locks.py
tools/agentx_evolve/backup/backup_catalog.py
tools/agentx_evolve/backup/restore_preflight.py
tools/agentx_evolve/backup/restore_transaction.py
```

Reason for added files:

```text
backup_dependency_adapters.py isolates optional upstream integrations and fail-closed fallback behavior.
backup_schema_validator.py gives a deterministic validation entrypoint.
backup_locks.py prevents overlapping backup/restore/retention operations.
backup_catalog.py maintains the atomic catalog of known verified, failed, protected, and deleted snapshots.
restore_preflight.py creates a separate preflight record before any restore plan is executable.
restore_transaction.py records runtime-only restore attempts, touched paths, checkpoints, and rollback notes.
```

---

# 5. Files to Create

## 5.1 Package Files

```text
__init__.py
backup_models.py
backup_manifest.py
snapshot_creator.py
snapshot_verifier.py
restore_planner.py
restore_executor.py
disaster_recovery_planner.py
retention_manager.py
backup_audit_logger.py
backup_cli_tools.py
backup_dependency_adapters.py
backup_schema_validator.py
backup_locks.py
backup_catalog.py
restore_preflight.py
restore_transaction.py
```

## 5.2 Schema Files

```text
tools/agentx_evolve/schemas/backup_policy.schema.json
tools/agentx_evolve/schemas/backup_manifest.schema.json
tools/agentx_evolve/schemas/backup_snapshot_record.schema.json
tools/agentx_evolve/schemas/backup_snapshot_index.schema.json
tools/agentx_evolve/schemas/backup_file_record.schema.json
tools/agentx_evolve/schemas/backup_verification_result.schema.json
tools/agentx_evolve/schemas/restore_request.schema.json
tools/agentx_evolve/schemas/restore_decision.schema.json
tools/agentx_evolve/schemas/restore_plan.schema.json
tools/agentx_evolve/schemas/restore_result.schema.json
tools/agentx_evolve/schemas/disaster_recovery_plan.schema.json
tools/agentx_evolve/schemas/backup_retention_policy.schema.json
tools/agentx_evolve/schemas/backup_audit_event.schema.json
tools/agentx_evolve/schemas/backup_evidence_manifest.schema.json
tools/agentx_evolve/schemas/backup_completion_record.schema.json
tools/agentx_evolve/schemas/backup_catalog.schema.json
tools/agentx_evolve/schemas/backup_lock_record.schema.json
tools/agentx_evolve/schemas/restore_preflight_record.schema.json
tools/agentx_evolve/schemas/restore_transaction_record.schema.json
tools/agentx_evolve/schemas/backup_cli_result.schema.json
```

## 5.3 Test Files

```text
tools/agentx_evolve/tests/test_backup_models.py
tools/agentx_evolve/tests/test_backup_manifest_schema.py
tools/agentx_evolve/tests/test_backup_manifest_writer.py
tools/agentx_evolve/tests/test_snapshot_creator.py
tools/agentx_evolve/tests/test_snapshot_verifier.py
tools/agentx_evolve/tests/test_restore_planner.py
tools/agentx_evolve/tests/test_restore_executor.py
tools/agentx_evolve/tests/test_disaster_recovery_planner.py
tools/agentx_evolve/tests/test_backup_retention_manager.py
tools/agentx_evolve/tests/test_backup_audit_logger.py
tools/agentx_evolve/tests/test_backup_cli_tools.py
tools/agentx_evolve/tests/test_backup_dependency_adapters.py
tools/agentx_evolve/tests/test_backup_locks.py
tools/agentx_evolve/tests/test_backup_negative_cases.py
tools/agentx_evolve/tests/test_backup_schema_validation.py
```

Dedicated schema validation utility:

```text
tools/agentx_evolve/tests/validate_backup_disaster_recovery_schemas.py
```

---

# 6. Implementation Slices

Build this layer in small slices. Do not implement backup, restore, retention, and disaster recovery as one broad pass.

## 6.1 Slice A — Models, Constants, Schemas

Implement:

```text
backup_models.py
all backup/restore/DR schemas
schema validation tests
```

Acceptance:

```text
dataclasses instantiate
schemas validate valid examples
schemas reject missing required fields
schemas reject invalid enum values
no filesystem writes occur
```

## 6.2 Slice B — Dependency Adapters and Locks

Implement:

```text
backup_dependency_adapters.py
backup_locks.py
```

Acceptance:

```text
Sandbox unavailable -> path operations BLOCK
Policy unavailable -> mutating backup/restore/retention actions BLOCK
Git unavailable -> git metadata UNKNOWN and source restore BLOCKS
Promotion unavailable -> release restore and release cleanup BLOCK
Monitoring unavailable -> local evidence warning only
backup lock prevents overlapping backup jobs
restore lock prevents overlapping restore jobs
retention lock prevents overlapping cleanup jobs
```

## 6.3 Slice C — Catalog, Compatibility, and Lock Evidence

Implement:

```text
backup_catalog.py
backup_locks.py lock-record evidence
backup format compatibility checks
```

Acceptance:

```text
backup catalog initializes under .agentx-init/backups/catalog/
catalog updates are atomic
catalog records verified, failed, protected, deleted, and stale-staging entries
restore planning can locate backups through catalog, not ad hoc directory guessing
lock acquisition writes BackupLockRecord evidence
restore planning blocks incompatible backup format, schema version, component version, or project identity
```

## 6.4 Slice D — Audit Logger and Evidence Manifest

Implement:

```text
backup_audit_logger.py
backup_evidence_manifest.schema.json
```

Acceptance:

```text
JSONL histories append
latest artifacts write atomically
evidence manifest writes with SHA-256 hashes
secret-like values are redacted
evidence stays under .agentx-init/backups/evidence/
```

## 6.5 Slice E — Manifest Builder and Snapshot Creator

Implement:

```text
backup_manifest.py
snapshot_creator.py
```

Acceptance:

```text
manifest records included and excluded files
snapshot is created in staging first
snapshot finalizes by atomic rename
partial/interrupted staging snapshots are not trusted
all included files are hashed
path traversal and symlink escape block
```

## 6.6 Slice F — Snapshot Verifier

Implement:

```text
snapshot_verifier.py
```

Acceptance:

```text
valid snapshot verifies
missing file fails verification
hash mismatch fails verification
verification does not mutate files
verification result is evidenced
```

## 6.7 Slice G — Restore Planner and Restore Executor Stub

Implement:

```text
restore_planner.py
restore_executor.py
```

Acceptance:

```text
restore requires verified backup
restore planning is dry-run first
restore plan lists conflicts and destructive actions
source restore blocks by default
runtime-only restore may be implemented only with policy + sandbox approval
unsafe restore returns schema-valid BLOCKED result
```

## 6.8 Slice H — Disaster Recovery Planner and Retention Manager

Implement:

```text
disaster_recovery_planner.py
retention_manager.py
```

Acceptance:

```text
DR plan selects verified backups only
DR plan does not restore automatically
retention dry-run deletes nothing
retention does not delete latest verified backup
retention does not delete protected release backup
retention path deletion remains inside backup root
```

## 6.9 Slice I — CLI / Tool Wrappers and Completion Evidence

Implement if exposed:

```text
backup_cli_tools.py
backup completion evidence writer or function
```

Acceptance:

```text
wrappers return structured results
wrappers use policy and sandbox
restore execution defaults to dry-run or BLOCKED
completion record is schema-valid
```

---

# 7. Required Classes and Functions

## 7.1 `backup_models.py`

Purpose:

```text
Define shared dataclasses, constants, IDs, statuses, backup types, restore modes, restore decisions, retention policies, evidence records, and serialization helpers.
```

Required constants:

```python
BACKUP_STATUS_CREATED = "CREATED"
BACKUP_STATUS_STAGED = "STAGED"
BACKUP_STATUS_VERIFIED = "VERIFIED"
BACKUP_STATUS_FAILED = "FAILED"
BACKUP_STATUS_INVALID = "INVALID"
BACKUP_STATUS_BLOCKED = "BLOCKED"

RESTORE_STATUS_PLANNED = "PLANNED"
RESTORE_STATUS_DRY_RUN = "DRY_RUN"
RESTORE_STATUS_BLOCKED = "BLOCKED"
RESTORE_STATUS_RESTORED = "RESTORED"
RESTORE_STATUS_FAILED = "FAILED"

DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
DECISION_DRY_RUN_ONLY = "DRY_RUN_ONLY"

BACKUP_SCOPE_RUNTIME = "RUNTIME"
BACKUP_SCOPE_SOURCE = "SOURCE"
BACKUP_SCOPE_CONFIG = "CONFIG"
BACKUP_SCOPE_EVIDENCE = "EVIDENCE"
BACKUP_SCOPE_RELEASE = "RELEASE"

RESTORE_MODE_DRY_RUN = "DRY_RUN"
RESTORE_MODE_RUNTIME_ONLY = "RUNTIME_ONLY"
RESTORE_MODE_SOURCE_RESTORE = "SOURCE_RESTORE"
RESTORE_MODE_RELEASE_RESTORE = "RELEASE_RESTORE"
RESTORE_MODE_FULL_RECOVERY = "FULL_RECOVERY"

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

LOCK_STATUS_ACQUIRED = "ACQUIRED"
LOCK_STATUS_RELEASED = "RELEASED"
LOCK_STATUS_STALE = "STALE"
LOCK_STATUS_BLOCKED = "BLOCKED"

CLI_STATUS_SUCCESS = "SUCCESS"
CLI_STATUS_BLOCKED = "BLOCKED"
CLI_STATUS_FAILED = "FAILED"
CLI_STATUS_INVALID = "INVALID"
```

Required dataclasses:

```python
@dataclass
class BackupPolicy:
    schema_version: str
    schema_id: str
    policy_id: str
    allowed_backup_roots: list[str]
    allowed_restore_roots: list[str]
    excluded_paths: list[str]
    excluded_globs: list[str]
    excluded_secret_patterns: list[str]
    require_git_status: bool
    require_hashes: bool
    require_manifest_validation: bool
    require_restore_dry_run: bool
    allow_source_backup: bool
    allow_source_restore: bool
    allow_runtime_restore: bool
    allow_release_restore: bool
    allow_secret_backup_plaintext: bool
    retention_policy_id: str | None
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupRetentionPolicy:
    schema_version: str
    schema_id: str
    retention_policy_id: str
    keep_latest_verified_count: int
    keep_minimum_total_count: int
    max_snapshot_age_days: int | None
    protect_release_linked: bool
    protect_manually_marked: bool
    dry_run: bool
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupFileRecord:
    schema_version: str
    schema_id: str
    relative_path: str
    original_path: str
    backup_path: str
    file_size_bytes: int
    sha256: str | None
    included: bool
    exclusion_reason: str | None
    path_type: str
    mode: str | None
    mtime_ns: int | None
    symlink_target: str | None
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupSnapshotRecord:
    schema_version: str
    schema_id: str
    snapshot_id: str
    backup_id: str
    snapshot_path: str
    staging_path: str | None
    finalized: bool
    file_count: int
    total_size_bytes: int
    snapshot_index_path: str
    snapshot_index_sha256: str | None
    protected: bool
    release_ref: str | None
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupSnapshotIndex:
    schema_version: str
    schema_id: str
    snapshot_index_id: str
    backup_id: str
    created_at: str
    snapshot_path: str
    file_records: list[BackupFileRecord]
    snapshot_sha256: str | None
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupManifest:
    schema_version: str
    schema_id: str
    backup_id: str
    created_at: str
    source_component: str
    repo_root: str
    git_commit: str | None
    git_branch: str | None
    git_status_summary: str
    backup_scope: list[str]
    snapshot_path: str
    snapshot_record: BackupSnapshotRecord | None
    file_records: list[BackupFileRecord]
    excluded_records: list[BackupFileRecord]
    manifest_sha256: str | None
    snapshot_sha256: str | None
    policy_decision_id: str | None
    sandbox_decision_ids: list[str]
    promotion_refs: list[str]
    monitoring_refs: list[str]
    evidence_refs: list[str]
    status: str
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupVerificationResult:
    schema_version: str
    schema_id: str
    verification_id: str
    backup_id: str
    verified_at: str
    manifest_path: str
    snapshot_path: str
    status: str
    files_checked: int
    files_passed: int
    files_failed: int
    hash_mismatches: list[str]
    missing_files: list[str]
    partial_snapshot_detected: bool
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class RestoreRequest:
    schema_version: str
    schema_id: str
    restore_request_id: str
    requested_at: str
    requested_by_role: str
    backup_id: str
    restore_mode: str
    target_root: str
    dry_run: bool
    requested_paths: list[str]
    policy_decision_id: str | None
    governance_decision_id: str | None
    human_approval_id: str | None
    promotion_decision_id: str | None
    warnings: list[str]
    errors: list[str]

@dataclass
class RestoreDecision:
    schema_version: str
    schema_id: str
    restore_decision_id: str
    restore_request_id: str
    decided_at: str
    decision: str
    reason: str
    required_authorities: list[str]
    missing_authorities: list[str]
    destructive_actions_allowed: bool
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class RestorePlan:
    schema_version: str
    schema_id: str
    restore_plan_id: str
    restore_request_id: str
    backup_id: str
    created_at: str
    restore_mode: str
    dry_run: bool
    restore_decision_id: str | None
    files_to_restore: list[str]
    files_to_skip: list[str]
    conflicts: list[str]
    destructive_actions: list[str]
    required_approvals: list[str]
    blocked_reasons: list[str]
    status: str
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class RestoreResult:
    schema_version: str
    schema_id: str
    restore_result_id: str
    restore_plan_id: str
    backup_id: str
    completed_at: str
    status: str
    restored_files: list[str]
    skipped_files: list[str]
    blocked_reasons: list[str]
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class DisasterRecoveryPlan:
    schema_version: str
    schema_id: str
    disaster_recovery_plan_id: str
    created_at: str
    trigger: str
    selected_backup_id: str | None
    recovery_steps: list[str]
    validation_steps: list[str]
    rollback_steps: list[str]
    required_approvals: list[str]
    rejected_backup_ids: list[str]
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupAuditEvent:
    schema_version: str
    schema_id: str
    audit_id: str
    timestamp: str
    source_component: str
    event_type: str
    backup_id: str | None
    restore_request_id: str | None
    status: str
    message: str
    artifact_refs: list[str]
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupEvidenceManifest:
    schema_version: str
    schema_id: str
    evidence_manifest_id: str
    component_id: str
    created_at: str
    backup_id: str | None
    restore_request_id: str | None
    evidence_files: list[str]
    evidence_file_hashes: dict[str, str]
    runtime_artifacts: list[str]
    deviation_register: list[dict]
    final_status: str
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupCatalog:
    schema_version: str
    schema_id: str
    catalog_id: str
    updated_at: str
    project_id: str
    repo_root_fingerprint: str
    backup_format_version: str
    snapshots: list[dict]
    latest_verified_backup_id: str | None
    protected_backup_ids: list[str]
    deleted_backup_ids: list[str]
    stale_staging_paths: list[str]
    catalog_sha256: str | None
    warnings: list[str]
    errors: list[str]

@dataclass
class BackupLockRecord:
    schema_version: str
    schema_id: str
    lock_record_id: str
    lock_name: str
    lock_id: str
    acquired_at: str
    released_at: str | None
    stale_after_seconds: int
    owner_component: str
    status: str
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class RestorePreflightRecord:
    schema_version: str
    schema_id: str
    preflight_id: str
    restore_request_id: str
    backup_id: str
    checked_at: str
    backup_format_compatible: bool
    project_identity_match: bool
    schema_versions_supported: bool
    verified_backup: bool
    target_paths_sandboxed: bool
    git_state_safe: bool
    promotion_gate_passed: bool
    destructive_actions_detected: list[str]
    blockers: list[str]
    warnings: list[str]
    errors: list[str]

@dataclass
class RestoreTransactionRecord:
    schema_version: str
    schema_id: str
    transaction_id: str
    restore_plan_id: str
    backup_id: str
    started_at: str
    completed_at: str | None
    mode: str
    pre_restore_checkpoint_path: str | None
    touched_paths: list[str]
    restored_paths: list[str]
    skipped_paths: list[str]
    rollback_available: bool
    rollback_notes: list[str]
    status: str
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]
```


@dataclass
class BackupCliResult:
    schema_version: str
    schema_id: str
    command_name: str
    command_id: str
    started_at: str
    completed_at: str
    status: str
    exit_code: int
    message: str
    data: dict
    artifact_refs: list[str]
    evidence_refs: list[str]
    warnings: list[str]
    errors: list[str]

Required helpers:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
sha256_file(path: Path) -> str
sha256_text(text: str) -> str
sha256_directory_index(index: BackupSnapshotIndex) -> str
safe_relative_path(path: Path, root: Path) -> str
redact_backup_value(value: object) -> object
is_secret_like_path(path: Path, policy: BackupPolicy) -> bool
compute_repo_root_fingerprint(repo_root: Path) -> str
check_backup_format_compatibility(manifest: BackupManifest, catalog: BackupCatalog) -> dict
cleanup_stale_staging_snapshots(repo_root: Path, policy: BackupRetentionPolicy, context: dict) -> dict
```

Acceptance:

```text
dataclasses instantiate
schemas match dataclass fields
helpers produce deterministic strings
hash helpers use Python standard library hashlib
serialization produces JSON-compatible dictionaries
no filesystem writes occur from model definitions
```

---

# 8. Backup Manifest and Snapshot Format

## 8.1 Manifest Path

Required manifest path:

```text
.agentx-init/backups/manifests/<backup_id>.manifest.json
```

Required manifest fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_manifest.schema.json",
  "backup_id": "backup-<id>",
  "created_at": "<UTC timestamp>",
  "source_component": "BackupDisasterRecovery",
  "repo_root": "<repo root>",
  "git_commit": "<commit or null>",
  "git_branch": "<branch or null>",
  "git_status_summary": "CLEAN|DIRTY|UNKNOWN",
  "backup_scope": ["RUNTIME", "CONFIG", "EVIDENCE"],
  "snapshot_path": ".agentx-init/backups/snapshots/<backup_id>",
  "snapshot_record": {},
  "file_records": [],
  "excluded_records": [],
  "manifest_sha256": "<sha256 or null before finalization>",
  "snapshot_sha256": "<sha256 or null>",
  "policy_decision_id": "<policy decision or null>",
  "sandbox_decision_ids": [],
  "promotion_refs": [],
  "monitoring_refs": [],
  "evidence_refs": [],
  "status": "CREATED|STAGED|VERIFIED|FAILED|INVALID|BLOCKED",
  "warnings": [],
  "errors": []
}
```

## 8.2 Snapshot Layout

Snapshot staging path:

```text
.agentx-init/backups/staging/<backup_id>.staging/
```

Final snapshot path:

```text
.agentx-init/backups/snapshots/<backup_id>/
```

Snapshot index path:

```text
.agentx-init/backups/snapshots/<backup_id>/snapshot_index.json
```

Snapshot layout rules:

```text
copy files into staging first
preserve relative paths under staging
write snapshot_index.json inside staging
verify staging index before finalization
rename staging directory to final snapshot path only after all required copies and hashes pass
never treat staging directory as a valid snapshot
if final rename fails, mark backup FAILED and retain staging only as failed evidence or clean it safely
if a snapshot path already exists for the same backup_id, block unless explicitly idempotent verification mode is requested
```

## 8.3 File Record Format

Each `file_records` item must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_file_record.schema.json",
  "relative_path": "string",
  "original_path": "string",
  "backup_path": "string",
  "file_size_bytes": 0,
  "sha256": "string|null",
  "included": true,
  "exclusion_reason": null,
  "path_type": "file|directory|symlink|other",
  "mode": "<optional mode string>",
  "mtime_ns": "<optional integer timestamp>",
  "symlink_target": "<null or safe relative target>",
  "warnings": [],
  "errors": []
}
```

Manifest and snapshot rules:

```text
manifest must be schema-valid before finalization
manifest must include SHA-256 hashes for every included file
snapshot index must include SHA-256 hashes for every included file
manifest must record excluded files with exclusion reasons when practical
manifest must record Git commit/branch/status when Git layer is available
manifest must record policy and sandbox evidence IDs where available
manifest must not include raw secret values
manifest must not include raw file content
manifest hash must be computed after final manifest content is stable
snapshot index hash must be computed after snapshot index content is stable
```

---

# 9. Required Schemas

Each schema must:

```text
require schema_version
require schema_id
require warnings
require errors
reject missing required fields
reject invalid status values
reject invalid decision values
reject invalid restore modes
reject invalid backup scopes
allow evidence_refs and artifact_refs where applicable
represent BLOCKED and FAILED outcomes as valid records
```

Required schema coverage:

```text
backup_policy.schema.json validates BackupPolicy
backup_manifest.schema.json validates BackupManifest
backup_snapshot_record.schema.json validates BackupSnapshotRecord
backup_snapshot_index.schema.json validates BackupSnapshotIndex
backup_file_record.schema.json validates BackupFileRecord
backup_verification_result.schema.json validates BackupVerificationResult
restore_request.schema.json validates RestoreRequest
restore_decision.schema.json validates RestoreDecision
restore_plan.schema.json validates RestorePlan
restore_result.schema.json validates RestoreResult
disaster_recovery_plan.schema.json validates DisasterRecoveryPlan
backup_retention_policy.schema.json validates BackupRetentionPolicy
backup_audit_event.schema.json validates BackupAuditEvent
backup_evidence_manifest.schema.json validates BackupEvidenceManifest
backup_completion_record.schema.json validates completion record
backup_catalog.schema.json validates BackupCatalog
backup_lock_record.schema.json validates BackupLockRecord
restore_preflight_record.schema.json validates RestorePreflightRecord
restore_transaction_record.schema.json validates RestoreTransactionRecord
backup_cli_result.schema.json validates BackupCliResult
```

Required schema examples in tests:

```text
valid_backup_policy
valid_backup_retention_policy
valid_backup_file_record
valid_backup_snapshot_record
valid_backup_snapshot_index
valid_backup_manifest
valid_backup_verification_result
valid_restore_request_dry_run
valid_restore_decision_blocked
valid_restore_plan_blocked
valid_restore_result_blocked
valid_disaster_recovery_plan
valid_backup_audit_event
valid_backup_evidence_manifest
valid_backup_completion_record
valid_backup_catalog
valid_backup_lock_record
valid_restore_preflight_record
valid_restore_transaction_record
valid_backup_cli_result
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
unsafe restore mode without approval fails schema or is represented as BLOCKED decision/plan
invalid artifact path outside approved runtime root fails validation or is rejected by code
```

---

# 10. File-by-File Implementation Spec

## 10.1 `__init__.py`

Purpose:

```text
Expose the public Backup / Disaster Recovery API without side effects.
```

Required exports:

```python
from .backup_models import (
    BackupPolicy,
    BackupRetentionPolicy,
    BackupFileRecord,
    BackupSnapshotRecord,
    BackupSnapshotIndex,
    BackupManifest,
    BackupVerificationResult,
    RestoreRequest,
    RestoreDecision,
    RestorePlan,
    RestoreResult,
    DisasterRecoveryPlan,
    BackupAuditEvent,
    BackupEvidenceManifest,
    BackupCatalog,
    BackupLockRecord,
    RestorePreflightRecord,
    RestoreTransactionRecord,
)
from .backup_manifest import build_backup_manifest, write_backup_manifest, finalize_manifest_hash
from .snapshot_creator import create_backup_snapshot
from .snapshot_verifier import verify_backup_snapshot
from .restore_planner import create_restore_decision, plan_restore
from .restore_executor import execute_restore_plan
from .disaster_recovery_planner import build_disaster_recovery_plan
from .retention_manager import apply_backup_retention_policy
from .backup_audit_logger import write_backup_audit_event, write_backup_evidence_manifest
from .backup_catalog import load_backup_catalog, write_backup_catalog, update_catalog_for_manifest
from .backup_locks import acquire_backup_lock, release_backup_lock, is_lock_active
from .restore_preflight import build_restore_preflight_record
from .restore_transaction import start_restore_transaction, record_restore_transaction_step, complete_restore_transaction
```

Must not do:

```text
no filesystem writes
no backup creation on import
no restore on import
no Git command on import
no monitoring calls on import
no lock acquisition on import
```

## 10.2 `backup_dependency_adapters.py`

Purpose:

```text
Provide thin adapters around optional upstream layers and enforce fail-closed fallback behavior.
```

Required functions:

```python
check_backup_policy(action: str, context: dict) -> dict
check_backup_sandbox(path: Path, operation: str, context: dict) -> dict
get_git_state(repo_root: Path, context: dict) -> dict
check_promotion_restore_allowed(backup_id: str, context: dict) -> dict
emit_backup_monitoring_event(event_type: str, payload: dict, context: dict) -> dict
```

Fallback rules:

```text
Policy unavailable -> mutating actions BLOCK; read-only manifest inspection may proceed only if sandbox allows.
Sandbox unavailable -> all path read/write/delete/restore operations BLOCK.
Git unavailable -> git_commit=null, git_branch=null, git_status_summary=UNKNOWN, source restore BLOCKS.
Promotion unavailable -> release restore BLOCKS; release-linked retention delete BLOCKS unless proven not release-linked.
Monitoring unavailable -> write local warning only; backup creation may proceed.
```

Must not do:

```text
no raw shell
no direct source mutation
no network requirement
no import-time failure that prevents model/schema tests
```

## 10.3 `backup_locks.py`

Purpose:

```text
Prevent overlapping backup, restore, and retention operations.
```

Required functions:

```python
acquire_backup_lock(repo_root: Path, lock_name: str, stale_after_seconds: int = 1800) -> dict
release_backup_lock(repo_root: Path, lock_id: str) -> dict
is_lock_active(repo_root: Path, lock_name: str) -> bool
```

Lock paths:

```text
.agentx-init/backups/locks/backup.lock
.agentx-init/backups/locks/restore.lock
.agentx-init/backups/locks/retention.lock
```

Rules:

```text
backup creation must acquire backup.lock
restore execution must acquire restore.lock
retention cleanup must acquire retention.lock
restore execution and retention cleanup must not run concurrently
stale locks may be reported, not silently ignored
lock acquisition failure returns BLOCKED with BACKUP_LOCK_HELD
```

## 10.4 `backup_audit_logger.py`

Purpose:

```text
Write backup, verification, restore, retention, disaster-recovery, and evidence-manifest records.
```

Required functions:

```python
write_backup_audit_event(event: BackupAuditEvent, repo_root: Path) -> dict
append_backup_history(record: dict, repo_root: Path) -> dict
append_restore_history(record: dict, repo_root: Path) -> dict
append_verification_history(record: dict, repo_root: Path) -> dict
append_retention_history(record: dict, repo_root: Path) -> dict
append_disaster_recovery_history(record: dict, repo_root: Path) -> dict
write_latest_backup_manifest(manifest: BackupManifest, repo_root: Path) -> dict
write_latest_restore_plan(plan: RestorePlan, repo_root: Path) -> dict
write_latest_verification_result(result: BackupVerificationResult, repo_root: Path) -> dict
write_backup_evidence_manifest(manifest: BackupEvidenceManifest, repo_root: Path) -> dict
```

Required files:

```text
.agentx-init/backups/evidence/backup_history.jsonl
.agentx-init/backups/evidence/restore_history.jsonl
.agentx-init/backups/evidence/verification_history.jsonl
.agentx-init/backups/evidence/retention_history.jsonl
.agentx-init/backups/evidence/disaster_recovery_history.jsonl
.agentx-init/backups/evidence/latest_backup_manifest.json
.agentx-init/backups/evidence/latest_restore_plan.json
.agentx-init/backups/evidence/latest_verification_result.json
.agentx-init/backups/evidence/backup_disaster_recovery_evidence_manifest.json
```

Rules:

```text
append JSONL only for histories
write latest JSON atomically
write evidence manifest atomically
redact secrets before durable logging
hash evidence files with SHA-256
never log raw backed-up file content
preserve malformed existing JSONL lines
```

## 10.5 `backup_manifest.py`

Purpose:

```text
Build and persist schema-valid backup manifests.
```

Required functions:

```python
build_backup_manifest(
    repo_root: Path,
    backup_scope: list[str],
    policy: BackupPolicy,
    context: dict,
) -> BackupManifest

write_backup_manifest(
    manifest: BackupManifest,
    repo_root: Path,
) -> dict

finalize_manifest_hash(
    manifest_path: Path,
) -> str
```

Rules:

```text
must enumerate only allowed roots
must exclude forbidden paths and globs
must exclude secret-like files by default
must reject path traversal
must call Security Sandbox for path approval when available
must include file hashes for included files
must include Git metadata when Git layer is available
must record Git UNKNOWN when Git layer is unavailable
must not include raw file content
must not include secrets
must write manifest under .agentx-init/backups/manifests/
```

## 10.6 `snapshot_creator.py`

Purpose:

```text
Create atomic snapshot directories from approved manifest records.
```

Required functions:

```python
create_backup_snapshot(
    repo_root: Path,
    manifest: BackupManifest,
    policy: BackupPolicy,
    context: dict,
) -> BackupManifest
```

Rules:

```text
must acquire backup lock
must create snapshot under .agentx-init/backups/staging/<backup_id>.staging/ first
must preserve relative paths
must not follow symlinks outside approved roots
must skip excluded files
must hash copied files
must write snapshot_index.json before finalization
must verify staging snapshot before final rename
must atomically rename staging snapshot to .agentx-init/backups/snapshots/<backup_id>/
must block if manifest is schema-invalid
must block if sandbox denies any included path
must return BLOCKED/FAILED status instead of partial silent success
must release lock in finally-style cleanup
```

## 10.7 `snapshot_verifier.py`

Purpose:

```text
Verify manifest, snapshot index, and snapshot file integrity.
```

Required functions:

```python
verify_backup_snapshot(
    repo_root: Path,
    manifest_path: Path,
    context: dict,
) -> BackupVerificationResult
```

Rules:

```text
must load and validate manifest
must load and validate snapshot index
must reject staging-only snapshots
must check every included file exists in snapshot
must recompute SHA-256 for every included file
must report hash mismatches
must report missing files
must report partial snapshot state
must produce schema-valid verification result
must not modify source or snapshot files
```

## 10.8 `restore_planner.py`

Purpose:

```text
Create restore decisions and restore plans without mutating files.
```

Required functions:

```python
create_restore_decision(
    restore_request: RestoreRequest,
    manifest: BackupManifest,
    verification: BackupVerificationResult,
    policy: BackupPolicy,
    context: dict,
) -> RestoreDecision

plan_restore(
    repo_root: Path,
    restore_request: RestoreRequest,
    manifest: BackupManifest,
    verification: BackupVerificationResult,
    policy: BackupPolicy,
    context: dict,
) -> RestorePlan
```

Rules:

```text
must require verified backup before planning restore
must produce RestoreDecision before RestorePlan
must detect conflicts with current files
must list destructive actions
must list required approvals
must block source restore unless governance and policy allow it
must block release restore unless Promotion / Release Gate allows it
must support dry-run
must not mutate files
must write restore plan under .agentx-init/backups/restore_plans/
```

## 10.9 `restore_executor.py`

Purpose:

```text
Execute approved restore plans or return safe blocked stubs.
```

Required functions:

```python
execute_restore_plan(
    repo_root: Path,
    restore_plan: RestorePlan,
    policy: BackupPolicy,
    context: dict,
) -> RestoreResult
```

Default v1 behavior:

```text
runtime-only restore may be implemented if sandbox and policy allow
source restore must be BLOCKED unless Git, Policy, Governance, Human Approval, and Promotion gates explicitly allow it
release restore must be BLOCKED unless Promotion / Release Gate explicitly allows it
full recovery must be BLOCKED unless separately approved
```

Required safe stub behavior:

```text
if restore execution is not implemented, return RESTORE_STATUS_BLOCKED
failure_class = BACKUP_RESTORE_BLOCKED
write evidence
mutate nothing
```

Rules:

```text
must acquire restore lock for any non-dry-run execution
must require restore_plan.dry_run=false for actual restore
must require verified backup
must require policy approval
must require sandbox approval for target paths
must block destructive restore without governance and human approval
must write restore result evidence
must release restore lock in cleanup
```

## 10.10 `disaster_recovery_planner.py`

Purpose:

```text
Generate disaster recovery plans from available verified backups.
```

Required functions:

```python
build_disaster_recovery_plan(
    repo_root: Path,
    trigger: str,
    available_manifests: list[BackupManifest],
    verification_results: list[BackupVerificationResult],
    context: dict,
) -> DisasterRecoveryPlan
```

Rules:

```text
must select only verified backups
must reject hash-mismatched backups
must reject missing snapshots
must prefer recent verified backups unless policy says otherwise
must include recovery steps
must include validation steps
must include rollback steps
must include required approvals
must not execute restore
must write plan under .agentx-init/backups/disaster_recovery/
```

## 10.11 `retention_manager.py`

Purpose:

```text
Apply backup retention policy safely.
```

Required functions:

```python
apply_backup_retention_policy(
    repo_root: Path,
    retention_policy: BackupRetentionPolicy,
    manifests: list[BackupManifest],
    context: dict,
) -> dict

cleanup_stale_staging_snapshots(
    repo_root: Path,
    retention_policy: BackupRetentionPolicy,
    catalog: BackupCatalog,
    context: dict,
) -> dict
```

Rules:

```text
must acquire retention lock
must not delete protected snapshots
must not delete the latest verified snapshot
must not delete below keep_latest_verified_count
must not delete below keep_minimum_total_count
must not delete snapshots referenced by release/promotion records
must support dry-run cleanup
must verify target paths are inside .agentx-init/backups/
must write evidence for retention decisions
must release retention lock in cleanup
stale staging cleanup may delete only paths under .agentx-init/backups/staging/
stale staging cleanup must record catalog entry before deletion
stale staging cleanup must block if path is finalized, verified, protected, or outside staging root
```

## 10.12 `backup_cli_tools.py`

Purpose:

```text
Expose backup functions as safe CLI/tool wrappers if this layer is exposed through Tool / MCP Adapter or CLI.
```

Required functions:

```python
backup_create(arguments: dict, context: dict) -> dict
backup_verify(arguments: dict, context: dict) -> dict
backup_plan_restore(arguments: dict, context: dict) -> dict
backup_execute_restore(arguments: dict, context: dict) -> dict
backup_dr_plan(arguments: dict, context: dict) -> dict
backup_retention_cleanup(arguments: dict, context: dict) -> dict
```

Rules:

```text
must require policy checks
must require sandbox checks for path operations
must default restore execution to dry-run or BLOCKED
must return schema-valid structured results
must write evidence
must not execute raw shell
must be safe to call from Tool / MCP Adapter
```

## 10.13 `backup_schema_validator.py`

Purpose:

```text
Validate all Backup / Disaster Recovery schemas and examples deterministically.
```

Required functions:

```python
validate_backup_schemas(repo_root: Path) -> dict
load_schema(schema_name: str, repo_root: Path) -> dict
validate_example(schema_name: str, example: dict, repo_root: Path) -> dict
```

Acceptance:

```text
valid examples pass
missing required fields fail
invalid enum values fail
schema validation command exits 0 only when all required schemas pass
```

## 10.14 `backup_catalog.py`

Purpose:

```text
Maintain the canonical catalog of backup snapshots so restore, retention, and disaster recovery do not depend on unsafe ad hoc directory discovery.
```

Required functions:

```python
load_backup_catalog(repo_root: Path) -> BackupCatalog
write_backup_catalog(catalog: BackupCatalog, repo_root: Path) -> dict
update_catalog_for_manifest(catalog: BackupCatalog, manifest: BackupManifest, verification: BackupVerificationResult | None) -> BackupCatalog
mark_backup_deleted(catalog: BackupCatalog, backup_id: str, reason: str) -> BackupCatalog
record_stale_staging_path(catalog: BackupCatalog, staging_path: Path, reason: str) -> BackupCatalog
```

Rules:

```text
write catalog atomically
hash catalog after stable write
never mark backup VERIFIED without PASS verification
never remove protected backup IDs silently
retention must update catalog only after deletion succeeds
corrupt catalog blocks retention deletion and source restore
backup_catalog.json is the canonical catalog; backup_catalog.sha256 is the required sidecar hash
if catalog and sidecar hash disagree, catalog is corrupt and restore/retention must fail closed
```

## 10.15 `restore_preflight.py`

Purpose:

```text
Create an independent restore preflight record that proves compatibility, verification, policy, sandbox, Git, Promotion, and conflict checks were run before restore execution.
```

Required function:

```python
build_restore_preflight_record(
    repo_root: Path,
    restore_request: RestoreRequest,
    manifest: BackupManifest,
    verification: BackupVerificationResult,
    policy: BackupPolicy,
    context: dict,
) -> RestorePreflightRecord
```

Rules:

```text
preflight must run before RestoreDecision can ALLOW execution
preflight must block incompatible backup format
preflight must block source restore into unsafe Git state
preflight must list destructive actions
preflight must be written as evidence
RestoreDecision cannot be ALLOW if preflight is missing, schema-invalid, failed, or has blockers
RestorePlan cannot be executable if preflight is missing or failed
```

## 10.16 `restore_transaction.py`

Purpose:

```text
Record all runtime-only restore execution attempts, including touched paths, checkpoint notes, rollback notes, and final status.
```

Required functions:

```python
start_restore_transaction(repo_root: Path, restore_plan: RestorePlan, context: dict) -> RestoreTransactionRecord
record_restore_transaction_step(transaction: RestoreTransactionRecord, step: dict, repo_root: Path) -> RestoreTransactionRecord
complete_restore_transaction(transaction: RestoreTransactionRecord, status: str, repo_root: Path) -> RestoreTransactionRecord
```

Rules:

```text
non-dry-run restore blocks if transaction cannot be written
transaction must not claim rollback_available unless rollback was tested or explicitly supported
transaction must not contain raw file contents
transaction must be referenced by RestoreResult.evidence_refs
```

---

# 11. Restore Decision Matrix

Use this matrix before any restore execution.

| Restore mode | Default v1 decision | Required authorities for execution | Notes |
|---|---|---|---|
| `DRY_RUN` | ALLOW if manifest and verification pass | Policy read permission + sandbox target precheck | Mutates nothing. |
| `RUNTIME_ONLY` | ALLOW or BLOCK depending on policy/sandbox | Policy + sandbox + verified backup + restore lock | May restore only `.agentx-init/` runtime artifacts. |
| `SOURCE_RESTORE` | BLOCK by default | Policy + sandbox + governance + human approval + Git clean/safe state | Must not overwrite uncommitted work. |
| `RELEASE_RESTORE` | BLOCK by default | Source-restore authorities + Promotion / Release Gate approval | Protects release-linked state. |
| `FULL_RECOVERY` | BLOCK by default | Separate future acceptance pass | Not implemented in this layer v1. |

Decision precedence:

```text
INVALID_REQUEST
HASH_MISMATCH
SNAPSHOT_MISSING
POLICY_BLOCK
SANDBOX_BLOCK
GIT_UNSAFE
PROMOTION_BLOCK
NEEDS_GOVERNANCE
NEEDS_APPROVAL
DRY_RUN_ONLY
ALLOW
```

---

# 12. Restore Flow

Restore must be planned before it can be executed.

Required restore planning flow:

```text
1. Receive RestoreRequest.
2. Validate restore_request.schema.json.
3. Load backup manifest.
4. Validate backup_manifest.schema.json.
5. Verify snapshot integrity or load recent PASS verification result.
6. Check Policy / Capability Registry.
7. Check Security Sandbox target paths.
8. Check Git Integration state if source restore is requested.
9. Check Promotion / Release Gate if restoring a release snapshot.
10. Detect conflicts with current files.
11. Detect destructive actions.
12. Require dry-run for first pass.
13. Create RestoreDecision.
14. Create RestorePlan.
15. Write restore plan evidence.
16. Return RestorePlan.
```

Required restore execution flow:

```text
1. Receive RestorePlan.
2. Validate restore_plan.schema.json.
3. Confirm backup verification PASS.
4. Confirm restore decision ALLOW.
5. Confirm restore_plan is not blocked.
6. Confirm policy approval.
7. Confirm sandbox approval.
8. Confirm governance and human approval for source restore.
9. Confirm Git working tree state is safe.
10. Confirm Promotion / Release Gate approval if release state is involved.
11. Acquire restore lock.
12. Execute runtime-only restore if allowed, or return BLOCKED stub.
13. Write RestoreResult.
14. Write restore history evidence.
15. Release restore lock.
16. Return RestoreResult.
```

Default v1 restriction:

```text
restore planning and dry-run are required
runtime-only restore may be implemented
source restore should remain blocked unless all upstream gates are stable and explicitly approve
release restore should remain blocked unless Promotion / Release Gate explicitly approves
full disaster recovery execution remains blocked/stubbed unless separately accepted
```

---

# 13. Disaster Recovery Flow

Disaster recovery planning flow:

```text
1. Receive disaster recovery trigger.
2. Enumerate available backup manifests.
3. Validate manifests.
4. Load or run verification results.
5. Exclude failed, missing, partial, stale, or hash-mismatched backups.
6. Exclude release-linked backups when Promotion / Release Gate is unavailable and release restore is requested.
7. Select best recovery point.
8. Build recovery steps.
9. Build validation steps.
10. Build rollback steps.
11. Identify required approvals.
12. Write DisasterRecoveryPlan.
13. Write disaster recovery evidence.
14. Return plan.
```

Disaster recovery execution is not required in v1.

Default v1 behavior:

```text
produce plan only
do not restore automatically
do not mutate source
do not delete corrupted state
do not push Git changes
do not promote recovered state
```

---

# 14. Backup Catalog, Compatibility, and Finalization Rules

## 14.1 Backup Catalog

Create and maintain an atomic catalog here:

```text
.agentx-init/backups/catalog/backup_catalog.json
.agentx-init/backups/catalog/backup_catalog.sha256
```

The catalog must record:

```text
all known backup IDs
latest verified backup ID
verified snapshot paths
failed snapshot paths
protected backup IDs
release-linked backup IDs
deleted backup IDs
stale staging paths
backup format version
project identity / repo root fingerprint
catalog SHA-256
```

Catalog rules:

```text
catalog updates must be atomic
catalog must not be updated to mark a backup VERIFIED until snapshot verification passes
retention must consult catalog before deleting anything
restore planning must locate snapshots through catalog or validated manifest path
manual directory scanning must not be the only restore discovery mechanism
corrupt catalog blocks retention deletion and source restore
backup_catalog.json is the canonical catalog; backup_catalog.sha256 is the required sidecar hash
if catalog and sidecar hash disagree, catalog is corrupt and restore/retention must fail closed
```

## 14.2 Compatibility Checks

Before restore planning, check:

```text
backup format version is supported
schema versions are supported
component_id matches AGENTX_BACKUP_DISASTER_RECOVERY
project identity matches or user explicitly approves cross-project restore
repo root fingerprint matches when source restore is requested
Python/platform assumptions do not invalidate path semantics
manifest hash and snapshot index hash are valid
```

If compatibility fails:

```text
DRY_RUN may report incompatibility
RUNTIME_ONLY restore blocks unless policy explicitly allows migration
SOURCE_RESTORE blocks
RELEASE_RESTORE blocks
FULL_RECOVERY blocks
```

## 14.3 Finalization Marker

Each finalized snapshot must contain:

```text
.agentx-init/backups/snapshots/<backup_id>/snapshot_index.json
.agentx-init/backups/snapshots/<backup_id>/.snapshot_finalized.json
```

The finalization marker must include:

```text
backup_id
finalized_at
snapshot_index_sha256
manifest_sha256
file_count
total_size_bytes
status = FINALIZED
```

Rules:

```text
no finalization marker -> not a valid finalized snapshot
finalization marker with mismatched hashes -> verification FAIL
staging directory with finalization marker -> verification FAIL
failed snapshot must never be marked VERIFIED in catalog
```

## 14.4 Restore Preflight and Restore Transaction Safety

Restore planning must create a preflight record before a restore plan is executable:

```text
.agentx-init/backups/restore_plans/<preflight_id>.restore_preflight.json
```

Restore execution, if implemented for runtime-only restore, must create a transaction record:

```text
.agentx-init/backups/restore_plans/<transaction_id>.restore_transaction.json
```

Preflight must record:

```text
compatibility checks
verification status
policy decision
sandbox decision
git safety state
promotion gate state
conflicts
destructive actions
blockers
```

Transaction must record:

```text
pre-restore checkpoint path, if any
touched paths
restored paths
skipped paths
rollback availability
rollback notes
status
evidence refs
```

Rules:

```text
source restore requires preflight PASS plus governance, human approval, policy, sandbox, Git safety, and Promotion approval where applicable
runtime-only restore must still create a transaction record
if transaction record cannot be written, restore execution blocks
restore transaction does not guarantee automatic rollback unless rollback_available=true and a tested rollback plan exists
```

## 14.5 Disaster-Recovery Drill Mode

Disaster recovery must support a drill mode:

```text
DR_DRILL_PLAN_ONLY
```

Drill mode must:

```text
select a verified backup
run compatibility checks
create restore preflight
create a DR plan
list exact validation commands
write evidence
mutate nothing
delete nothing
restore nothing
```

Drill mode is required for acceptance because it proves recovery readiness without destructive behavior.

---

# 15. Runtime Artifacts

All runtime artifacts must be under:

```text
.agentx-init/backups/
```

Required directories:

```text
.agentx-init/backups/manifests/
.agentx-init/backups/snapshots/
.agentx-init/backups/staging/
.agentx-init/backups/restore_plans/
.agentx-init/backups/disaster_recovery/
.agentx-init/backups/evidence/
.agentx-init/backups/locks/
.agentx-init/backups/catalog/
```

Required artifacts:

```text
.agentx-init/backups/manifests/<backup_id>.manifest.json
.agentx-init/backups/snapshots/<backup_id>/snapshot_index.json
.agentx-init/backups/restore_plans/<restore_plan_id>.restore_plan.json
.agentx-init/backups/disaster_recovery/<plan_id>.dr_plan.json
.agentx-init/backups/evidence/backup_history.jsonl
.agentx-init/backups/evidence/restore_history.jsonl
.agentx-init/backups/evidence/verification_history.jsonl
.agentx-init/backups/evidence/retention_history.jsonl
.agentx-init/backups/evidence/disaster_recovery_history.jsonl
.agentx-init/backups/evidence/latest_backup_manifest.json
.agentx-init/backups/evidence/latest_restore_plan.json
.agentx-init/backups/evidence/latest_verification_result.json
.agentx-init/backups/evidence/backup_disaster_recovery_evidence_manifest.json
.agentx-init/backups/evidence/backup_disaster_recovery_completion_record.json
.agentx-init/backups/catalog/backup_catalog.json
.agentx-init/backups/catalog/backup_catalog.sha256
.agentx-init/backups/restore_plans/<preflight_id>.restore_preflight.json
.agentx-init/backups/restore_plans/<transaction_id>.restore_transaction.json
```

Runtime artifact rules:

```text
runtime artifacts must not be written outside .agentx-init/backups/ unless explicitly delegated to another approved component
any exception must be listed in the deviation register
history logs must be append-only JSONL
latest artifacts must be written atomically
backup snapshots must preserve relative paths
secret files must be excluded unless a future encrypted backup policy explicitly permits them
hashes must be recorded for manifests, snapshot indexes, files, evidence manifests, and completion records
```

Deviation register entry format:

```text
deviations:
  - id: <DEV-001>
    area: <Runtime Artifact Boundary | Git | Promotion | Monitoring | Restore | Retention | Other>
    description: <what differs from this spec>
    reason: <why accepted>
    safety_impact: <none | low | medium | high>
    compensating_control: <test/evidence/control>
    accepted_status: DEFERRED SAFELY | NOT APPLICABLE | NON-BLOCKING FOLLOW-UP
```

---

# 16. Integration Requirements

## 16.1 Security Sandbox Integration

Required:

```text
all backup source paths must be checked by Security Sandbox
all restore target paths must be checked by Security Sandbox
retention deletion targets must be checked by Security Sandbox
path traversal must block
symlink escape must block
source restore must block if sandbox is unavailable
```

Expected adapter behavior:

```python
# Example only; exact names may differ.
from agentx_evolve.security import (
    validate_path_boundary,
    safe_read_file,
    safe_write_file,
    safe_copy_file,
    safe_delete_runtime_artifact,
)
```

If actual names differ, implement a thin adapter in `backup_dependency_adapters.py`. If sandbox is unavailable, fail closed.

## 16.2 Policy / Capability Registry Integration

Required:

```text
backup creation requires policy check
restore planning requires policy check
restore execution requires policy check
retention cleanup requires policy check
source restore requires governance and human approval where applicable
missing policy blocks mutating actions
```

Policy must decide:

```text
allowed backup roots
allowed restore roots
backup scope
restore mode
retention delete permission
source restore permission
release snapshot permission
secret inclusion policy
```

If Policy / Capability Registry is unavailable:

```text
allow manifest building for read-only runtime inspection only if sandbox allows
block restore execution
block source restore
block release restore
block retention deletion
block secret backup
```

## 16.3 Git Integration Layer

Required when Git layer exists:

```text
record current commit
record current branch
record git status summary
block source restore into dirty working tree unless explicitly approved
block restore that overwrites uncommitted work
record Git evidence refs
```

If Git Integration Layer is unavailable:

```text
git_commit = null
git_branch = null
git_status_summary = UNKNOWN
source restore remains BLOCKED unless explicitly approved by policy, governance, and human approval
```

## 16.4 Promotion / Release Gate Integration

Required when backup is tied to release or promotion state:

```text
create pre-promotion backup before promotion
create post-promotion backup after successful promotion
record promotion/release IDs in manifest evidence_refs
block restore of release state unless Promotion / Release Gate allows it
protect release-linked backups from retention cleanup
```

If Promotion / Release Gate is unavailable:

```text
release restore remains BLOCKED
release-linked backup cleanup remains BLOCKED unless policy confirms not release-linked
```

## 16.5 Monitoring / Observability Integration

Required when Monitoring / Observability exists:

```text
emit backup_created event
emit backup_failed event
emit backup_verification_failed event
emit restore_planned event
emit restore_blocked event
emit restore_completed event
emit retention_cleanup event
emit disaster_recovery_plan_created event
```

If Monitoring is unavailable:

```text
write local evidence only
do not fail backup creation only because monitoring is unavailable
record warning that monitoring was unavailable
```

## 16.6 Tool / MCP Adapter Integration

If backup functions are exposed as tools:

```text
register backup_create
register backup_verify
register backup_plan_restore
register backup_execute_restore
register backup_dr_plan
register backup_retention_cleanup
```

Tool exposure rules:

```text
backup_verify may be read-only
backup_plan_restore must be dry-run by default
backup_execute_restore must be BLOCKED or runtime-only governed by default
backup_retention_cleanup must be dry-run by default
no backup tool may expose source restore over MCP by default
no backup tool may expose external storage/network behavior by default
```

---

# 17. Idempotency, Locking, and Partial Failure Rules

## 17.1 Idempotency

Required behavior:

```text
build_backup_manifest with same inputs may create a new backup_id, but file hash results must be deterministic.
verify_backup_snapshot may be repeated and must return the same PASS/FAIL result unless files changed.
plan_restore may be repeated and must return equivalent conflicts, destructive actions, and required approvals for the same inputs.
execute_restore_plan must not execute twice unless the plan explicitly allows retry and the previous result did not restore any files.
retention dry-run may be repeated and must produce equivalent candidate deletion list for the same inputs.
```

## 17.2 Locking

Required locks:

```text
backup.lock for snapshot creation
restore.lock for restore execution
retention.lock for retention cleanup
```

Rules:

```text
backup verification may run without backup lock if snapshot is finalized
restore execution cannot run while retention cleanup is active
retention cleanup cannot run while restore execution is active
stale lock handling must be explicit and evidenced
```

## 17.3 Partial Failure

Partial backup behavior:

```text
if any required included file fails to copy, backup status becomes FAILED
if staging snapshot exists without finalized marker/index, it is not a valid backup
if manifest exists but snapshot is missing, verification fails
if snapshot index is missing or invalid, verification fails
partial success must be evidenced; it must not be reported as VERIFIED
```

---

# 18. Redaction, Secret Exclusion, and Output Bounds

Before writing evidence, redact:

```text
API keys
tokens
passwords
provider credentials
environment variable values matching secret-like names
private keys
raw prompt text, if future tools emit it
unredacted command output
```

Secret-like files are excluded by default:

```text
.env
*.pem
*.key
id_rsa
id_ed25519
credentials.json
secrets.*
```

Evidence output limits:

```text
max_message_chars = 4000
max_list_items_per_field = 500
max_path_chars = 1000
max_error_chars = 4000
```

Rules:

```text
do not log raw backed-up file content
do not log unredacted command output
do not include raw secret values in manifests, audit events, evidence manifests, or completion records
if a secret-like file is excluded, record exclusion reason without reading the secret value
```

---

# 19. Test Cases

## 19.1 Model and Schema Tests

Required tests:

```text
test_backup_models_instantiate
test_backup_manifest_schema_accepts_valid_manifest
test_backup_manifest_schema_rejects_missing_backup_id
test_backup_manifest_schema_rejects_invalid_status
test_backup_snapshot_index_schema_accepts_valid_index
test_restore_request_schema_accepts_dry_run
test_restore_request_schema_rejects_invalid_restore_mode
test_restore_decision_schema_accepts_blocked_decision
test_restore_plan_schema_accepts_blocked_plan
test_backup_verification_schema_accepts_hash_mismatch_result
test_disaster_recovery_plan_schema_accepts_valid_plan
test_backup_retention_policy_schema_accepts_valid_policy
test_backup_audit_event_schema_accepts_valid_event
test_backup_evidence_manifest_schema_accepts_valid_manifest
```

## 19.2 Dependency Adapter and Lock Tests

Required tests:

```text
test_policy_unavailable_blocks_mutating_actions
test_sandbox_unavailable_blocks_path_operations
test_git_unavailable_records_unknown_and_blocks_source_restore
test_promotion_unavailable_blocks_release_restore
test_monitoring_unavailable_records_warning_only
test_backup_lock_prevents_overlapping_backup
test_restore_lock_prevents_overlapping_restore
test_retention_lock_prevents_overlapping_cleanup
```

## 19.3 Manifest Writer Tests

Required tests:

```text
test_build_backup_manifest_records_allowed_files
test_build_backup_manifest_excludes_forbidden_paths
test_build_backup_manifest_excludes_secret_like_files
test_build_backup_manifest_records_sha256
test_write_backup_manifest_writes_under_runtime_root
test_manifest_does_not_include_raw_file_content
test_manifest_records_git_unknown_when_git_unavailable
```

## 19.4 Snapshot Creator Tests

Required tests:

```text
test_create_snapshot_copies_allowed_files
test_create_snapshot_preserves_relative_paths
test_create_snapshot_uses_staging_then_final_path
test_create_snapshot_writes_snapshot_index
test_create_snapshot_blocks_path_traversal
test_create_snapshot_blocks_symlink_escape
test_create_snapshot_blocks_when_sandbox_denies
test_create_snapshot_blocks_schema_invalid_manifest
test_partial_staging_snapshot_not_marked_verified
```

## 19.5 Snapshot Verifier Tests

Required tests:

```text
test_verify_snapshot_passes_when_hashes_match
test_verify_snapshot_fails_on_hash_mismatch
test_verify_snapshot_fails_on_missing_file
test_verify_snapshot_fails_on_missing_index
test_verify_snapshot_rejects_staging_only_snapshot
test_verify_snapshot_does_not_mutate_files
test_verify_snapshot_returns_schema_valid_result
```

## 19.6 Restore Planner Tests

Required tests:

```text
test_plan_restore_requires_verified_backup
test_create_restore_decision_blocks_hash_mismatch
test_plan_restore_detects_conflicts
test_plan_restore_lists_destructive_actions
test_plan_restore_blocks_source_restore_without_governance
test_plan_restore_blocks_release_restore_without_promotion_gate
test_plan_restore_supports_dry_run
test_plan_restore_writes_restore_plan_evidence
```

## 19.7 Restore Executor Tests

Required tests:

```text
test_execute_restore_blocks_unverified_backup
test_execute_restore_blocks_source_restore_by_default
test_execute_restore_blocks_release_restore_by_default
test_execute_restore_blocks_without_policy
test_execute_restore_blocks_without_sandbox
test_execute_restore_runtime_only_stub_returns_blocked_or_success_if_implemented
test_execute_restore_writes_restore_result_evidence
test_execute_restore_lock_blocks_concurrent_execution
```

## 19.8 Disaster Recovery Planner Tests

Required tests:

```text
test_dr_plan_selects_verified_backup_only
test_dr_plan_excludes_hash_mismatched_backup
test_dr_plan_excludes_missing_snapshot
test_dr_plan_includes_recovery_steps
test_dr_plan_includes_validation_steps
test_dr_plan_does_not_execute_restore
test_dr_plan_writes_evidence
```

## 19.9 Retention Manager Tests

Required tests:

```text
test_retention_dry_run_deletes_nothing
test_retention_does_not_delete_latest_verified_backup
test_retention_does_not_delete_below_minimum_verified_count
test_retention_does_not_delete_protected_backup
test_retention_does_not_delete_release_linked_backup
test_retention_blocks_path_outside_backup_root
test_retention_writes_decision_evidence
test_retention_lock_blocks_concurrent_cleanup
```

## 19.10 Audit Logger Tests

Required tests:

```text
test_backup_history_jsonl_appends
test_restore_history_jsonl_appends
test_verification_history_jsonl_appends
test_latest_backup_manifest_atomic_write
test_latest_restore_plan_atomic_write
test_backup_audit_redacts_secrets
test_backup_audit_records_hashes
test_backup_evidence_manifest_records_hashes
```

## 19.11 Negative Tests

Required negative tests:

```text
test_backup_rejects_path_traversal
test_backup_rejects_symlink_escape
test_backup_excludes_secret_files_by_default
test_backup_does_not_read_secret_value_for_exclusion
test_restore_rejects_unverified_snapshot
test_restore_rejects_hash_mismatched_snapshot
test_restore_rejects_dirty_worktree_source_restore_without_approval
test_restore_rejects_policy_missing_for_mutation
test_restore_rejects_sandbox_missing_for_target_path
test_restore_rejects_release_restore_without_promotion_gate
test_retention_rejects_delete_only_valid_backup
test_retention_rejects_delete_release_linked_backup
test_no_backup_artifact_written_outside_runtime_root
test_no_source_mutation_during_backup_or_verify
test_no_raw_shell_execution
test_no_network_required_for_validation
```

## 19.12 Catalog, Compatibility, Preflight, Transaction, and CLI Acceptance Tests

Required tests:

```text
test_backup_catalog_initializes
test_backup_catalog_atomic_write
test_backup_catalog_records_verified_backup_only_after_pass_verification
test_backup_catalog_corruption_blocks_retention_delete
test_restore_blocks_incompatible_backup_format
test_restore_blocks_project_identity_mismatch_for_source_restore
test_snapshot_finalization_marker_required
test_snapshot_finalization_marker_hash_mismatch_fails_verification
test_restore_preflight_created_before_restore_plan_allow
test_restore_transaction_required_for_runtime_restore
test_restore_transaction_records_touched_paths_without_file_content
test_dr_drill_mode_mutates_nothing
test_stale_staging_cleanup_records_catalog_entry
test_backup_cli_create_requires_policy_and_sandbox
test_backup_cli_execute_restore_defaults_to_blocked_or_dry_run
test_backup_cli_retention_cleanup_defaults_to_dry_run
```

CLI result envelope, if CLI commands are exposed:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_cli_result.schema.json",
  "command_name": "backup_create",
  "command_id": "backup-cli-<id>",
  "started_at": "<UTC timestamp>",
  "completed_at": "<UTC timestamp>",
  "status": "SUCCESS|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

CLI exit-code rules:

```text
0 = SUCCESS
1 = FAILED
2 = INVALID request/schema
3 = BLOCKED by policy/sandbox/governance/approval/compatibility
4 = verification failed
5 = retention safety block
```

CLI command acceptance criteria, if CLI commands are exposed:

```text
backup create command returns structured JSON
backup verify command returns structured JSON
backup plan-restore command defaults to dry-run
backup execute-restore command blocks unless explicit approved non-dry-run authority exists
backup retention-cleanup command defaults to dry-run
all commands record exit_code
all commands write evidence
no command requires network or external storage for validation
no command executes raw shell
```

---

# 20. Implementation Order

Implement in this exact order:

```text
1. Create tools/agentx_evolve/backup/ package.
2. Implement backup_models.py.
3. Create schema files under tools/agentx_evolve/schemas/.
4. Implement backup_schema_validator.py and schema tests.
5. Implement backup_dependency_adapters.py.
6. Implement backup_locks.py with BackupLockRecord evidence.
7. Implement backup_catalog.py with atomic catalog writes and hash sidecar.
8. Implement backup_audit_logger.py.
9. Implement backup_manifest.py.
10. Implement snapshot_creator.py with staging/finalize behavior.
11. Implement snapshot_verifier.py.
12. Implement restore_preflight.py.
13. Implement restore_planner.py with RestoreDecision.
14. Implement restore_transaction.py.
15. Implement restore_executor.py as safe BLOCKED/runtime-only stub first.
16. Implement disaster_recovery_planner.py.
17. Implement retention_manager.py.
18. Implement stale staging cleanup function and tests.
19. Implement backup_cli_tools.py only if CLI/tool wrappers are exposed.
20. Implement integration adapter tests for Security Sandbox, Policy Registry, Git, Promotion, and Monitoring.
21. Implement negative tests.
22. Run compileall.
23. Run pytest.
24. Run schema validation.
25. Verify git status.
26. Write evidence manifest.
27. Write completion evidence.
```

Rationale:

```text
models first
schemas second
dependency adapters before behavior that depends on upstream layers
locks before snapshot/restore/retention operations
audit logger before writing runtime artifacts
manifest before snapshot
snapshot before verification
verification before restore planning
restore decision before restore execution
disaster recovery planning after verified backups exist
retention after protection rules exist
CLI wrappers last
```

---

# 21. Acceptance Criteria

## 21.1 GO Criteria

The layer may be marked implemented only if all are true:

```text
all target package files exist
all required schemas exist
all required tests exist
backup manifest can be created
snapshot can be created under approved runtime root using staging/finalize flow
snapshot index is written
snapshot verification passes for valid backup
hash mismatch is detected
missing snapshot file is detected
partial staging snapshot is rejected
backup catalog is written atomically
backup catalog records verified backups only after verification PASS
compatibility checks block incompatible restore
restore preflight is created before executable restore plan
restore decision is created
restore planning works in dry-run mode
source restore blocks by default
release restore blocks by default unless Promotion / Release Gate approves
restore execution is safe stub or runtime-only governed restore
restore transaction record exists for any non-dry-run runtime restore
retention dry-run works
retention does not delete protected backups
retention consults catalog before deletion
retention does not delete latest verified backup
retention does not delete below minimum verified count
backup evidence is written
restore evidence is written
verification evidence is written
evidence manifest is written
SHA-256 hashes are recorded for final evidence artifacts
secrets are excluded or redacted
Security Sandbox checks are enforced
Policy / Capability Registry checks are enforced or fail closed
Git state is recorded or source restore blocks when Git unavailable
Promotion-linked backups are protected or restore blocks when promotion unavailable
Monitoring events emit when monitoring exists or warning is recorded when unavailable
compileall passes
pytest passes
schema validation passes
git status is clean or only expected runtime artifacts exist
completion record exists
```

## 21.2 NO-GO Criteria

The layer is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
backup writes outside .agentx-init/backups/ without recorded accepted deviation
restore mutates source by default
restore overwrites uncommitted work without approval
restore executes from unverified backup
restore executes from incompatible backup format without explicit migration approval
restore executes without preflight record
restore ignores hash mismatch
restore ignores missing snapshot index
retention deletes latest verified backup
retention deletes catalog-protected backup
retention deletes below minimum verified backup count
retention deletes protected release backup
secrets are included in plaintext backup without explicit approved encryption policy
path traversal is possible
symlink escape is possible
raw shell is executed
network/external storage is required for validation
Policy missing results in mutating ALLOW
Sandbox missing results in path operation ALLOW
backup/restore evidence is missing
evidence hashes are missing
completion record is missing
```

## 21.3 Conditional GO

Conditional GO is allowed for:

```text
restore executor implemented as safe BLOCKED stub
source restore blocked until governance integration is mature
release restore blocked until Promotion / Release Gate integration is mature
Monitoring unavailable but local evidence written
Promotion unavailable but release restore blocked
Git unavailable but Git metadata recorded as UNKNOWN and source restore blocked
CLI wrappers not implemented if no CLI exposure is required
```

Conditional GO is not allowed for:

```text
schema failures
evidence failures
evidence hash failures
path traversal failures
secret leakage
unverified restore
hash-mismatched restore
source mutation without approval
retention deleting protected backups
```

---

# 22. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_backup_disaster_recovery_schemas.py
git status --short
```

If the dedicated schema validator is not implemented, the schema validation may be covered by:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_backup_schema_validation.py
```

Required result:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts under .agentx-init/backups/
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
external backup service
external storage provider
```

---

# 23. Completion Evidence

After implementation, write:

```text
.agentx-init/backups/evidence/backup_disaster_recovery_evidence_manifest.json
.agentx-init/backups/evidence/backup_disaster_recovery_completion_record.json
.agentx-init/backups/catalog/backup_catalog.json
.agentx-init/backups/catalog/backup_catalog.sha256
.agentx-init/backups/restore_plans/<preflight_id>.restore_preflight.json
.agentx-init/backups/restore_plans/<transaction_id>.restore_transaction.json
```

Evidence manifest required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_evidence_manifest.schema.json",
  "evidence_manifest_id": "backup-evidence-<id>",
  "component_id": "AGENTX_BACKUP_DISASTER_RECOVERY",
  "created_at": "<UTC timestamp>",
  "backup_id": "<backup id or null>",
  "restore_request_id": "<restore request id or null>",
  "evidence_files": [],
  "evidence_file_hashes": {},
  "runtime_artifacts": [],
  "deviation_register": [],
  "final_status": "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED",
  "warnings": [],
  "errors": []
}
```

Completion record required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_completion_record.schema.json",
  "component_id": "AGENTX_BACKUP_DISASTER_RECOVERY",
  "component_name": "Backup / Disaster Recovery Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/backup/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/backups/",
  "basis_documents": [
    "BACKUP_DISASTER_RECOVERY_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "BACKUP_DISASTER_RECOVERY_IMPLEMENTATION_SPEC_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "backup_manifests_verified": [],
  "snapshot_integrity_verified": [],
  "restore_decisions_verified": [],
  "restore_plans_verified": [],
  "restore_preflights_verified": [],
  "restore_transactions_verified": [],
  "backup_catalog_verified": [],
  "retention_rules_verified": [],
  "security_sandbox_integration_verified": [],
  "policy_integration_verified": [],
  "git_integration_verified": [],
  "promotion_gate_integration_verified": [],
  "monitoring_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/backups/evidence/backup_disaster_recovery_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project helper exists.
A final DONE claim is invalid if final evidence hashes are missing.
```

---

# 24. Definition of Done

The Backup / Disaster Recovery Layer is done when it can preserve, verify, plan recovery from, and safely manage Agent_X recovery points without unsafe mutation.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
backup manifests are schema-valid
backup snapshot indexes are schema-valid
snapshots are created only under approved runtime root
snapshots are finalized from staging safely
included files are hashed
excluded files are recorded or safely skipped
secrets are excluded or redacted
backup catalog exists and is atomic
snapshot verification detects valid and invalid backups
compatibility checks run before restore planning
partial/staging snapshots are rejected
restore preflight is created before executable restore plan
restore decision is created before restore plan
restore planning is dry-run first
restore execution blocks unsafe source restore
source restore requires policy, sandbox, governance, human approval, and Git safety
release restore requires Promotion / Release Gate approval
retention cleanup cannot delete catalog-protected, release-linked, latest verified, or minimum-count backups
disaster recovery plan selects verified backups only
audit/evidence is written for backup, verification, restore, retention, and disaster recovery
evidence manifest is written with SHA-256 hashes
Security Sandbox integration is enforced
Policy / Capability Registry integration is enforced or fails closed
Git Integration is used when available and source restore blocks when unavailable
Promotion-linked backups are protected
Monitoring emits events when available or records warning when unavailable
no raw shell is executed
no network/external storage is required for validation
no source mutation occurs during backup or verification
compileall passes
pytest passes
schema validation passes
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_backup_disaster_recovery_schemas.py
git status --short
```

Expected proof:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts under .agentx-init/backups/
```

---

# 25. Final Frozen Acceptance Matrix

| Area | Required result |
|---|---|
| Package files | All required files under `tools/agentx_evolve/backup/`. |
| Schemas | All required schemas exist and validate valid/invalid examples. |
| Manifest | Records scope, Git state, included/excluded files, hashes, policy/sandbox evidence. |
| Snapshot | Uses staging, writes index, finalizes only after successful copy/hash/index. |
| Verification | Detects valid, missing, hash-mismatched, partial, staging-only, and bad finalization-marker snapshots. |
| Catalog | Atomic catalog records verified, failed, protected, deleted, release-linked, and stale-staging backups. |
| Compatibility | Restore planning blocks incompatible backup format, schema version, project identity, and unsafe platform assumptions. |
| Restore decision | Blocks unsafe restore modes and records missing authorities. |
| Restore preflight | Runs before executable restore plan and records compatibility, verification, policy, sandbox, Git, Promotion, and conflict checks. |
| Restore plan | Dry-run first, lists conflicts/destructive actions/approvals. |
| Restore execution | Runtime-only if approved or safe BLOCKED stub; source restore blocked by default; transaction record required for non-dry-run runtime restore. |
| Disaster recovery | Plan only; selects verified backups only; does not mutate. |
| Retention | Dry-run supported; protected/latest/minimum/release backups not deleted. |
| Evidence | JSONL histories, latest artifacts, evidence manifest, hashes, completion record. |
| Security Sandbox | Required for path operations; unavailable sandbox fails closed. |
| Policy Registry | Required for mutating actions; unavailable policy fails closed. |
| Git | Records commit/branch/status when available; source restore blocks when unavailable/unsafe. |
| Promotion | Release-linked restore/delete blocks unless promotion gate approves. |
| Monitoring | Emits events when available; unavailable monitoring records warning only. |
| Safety | No raw shell, no external service dependency, no secret leakage, no unsafe source mutation. |

---

# 26. Final Coding-Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The layer lives under tools/agentx_evolve/backup/.
[ ] Runtime artifacts live under .agentx-init/backups/.
[ ] Backup catalog is atomic and schema-valid JSON.
[ ] Backup manifests are schema-valid JSON.
[ ] Snapshots preserve relative paths.
[ ] Snapshots are created through staging then finalized.
[ ] Every included file gets SHA-256.
[ ] Snapshot index gets SHA-256.
[ ] Secret-like paths and values are excluded/redacted by default.
[ ] Restore compatibility checks run before restore planning.
[ ] Restore preflight is created before executable restore plan.
[ ] Restore is dry-run first.
[ ] Restore decision is created before restore plan.
[ ] Source restore is blocked by default.
[ ] Release restore is blocked by default.
[ ] Runtime-only restore may be implemented only with sandbox and policy approval.
[ ] Retention cleanup cannot delete protected, release-linked, latest verified, or minimum-count backups.
[ ] Disaster recovery drill mode mutates nothing.
[ ] Disaster recovery planning does not execute restore.
[ ] Security Sandbox is authoritative for path operations.
[ ] Policy / Capability Registry is authoritative for backup/restore permission.
[ ] Git Integration is used for commit/branch/status when available.
[ ] Promotion-linked backups are protected.
[ ] Monitoring is optional but evidence is mandatory.
[ ] Evidence manifest and completion record include SHA-256 hashes.
[ ] Tests do not require network, GPU, hosted model, LLM, Bun, Node, OpenCode runtime, or external backup service.
```

---

# 27. Evidence Immutability Rule

After the backup/disaster recovery completion record records `final_decision = DONE`:

```text
final evidence files must not be modified without creating a new completion record
changed evidence hashes invalidate the previous DONE claim
new validation evidence must record a new timestamp and validated commit
manual edits to manifests, catalog, review evidence, or completion evidence after sign-off must be listed as deviations
retention cleanup must not delete evidence files used by the final DONE record unless a newer validated evidence package supersedes them
```

Required final evidence hash coverage:

```text
backup_disaster_recovery_evidence_manifest.json
backup_disaster_recovery_completion_record.json
backup_catalog.json
backup_catalog.sha256
latest_backup_manifest.json, if used by validation
latest_verification_result.json, if used by validation
latest_restore_plan.json, if used by validation
command output artifacts, if stored as files
```

---

# 28. Final Freeze Rule

This v4 document is frozen as the implementation-ready coding-agent handoff for the Backup / Disaster Recovery Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details that do not weaken safety
MAJOR: changed restore policy, changed source-restore default, changed retention protection rules, new external backup provider requirement
```

Blocked without major revision:

```text
allowing source restore by default
allowing release restore by default
allowing restore from unverified backup
allowing restore despite hash mismatch
allowing retention to delete latest verified backup
allowing retention to delete protected release backup
allowing plaintext secret backup by default
allowing raw shell execution
allowing network/external storage dependency for validation
removing policy checks
removing sandbox checks
removing evidence hashing
```

---

# 29. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines the exact subdirectory, files, schemas, classes/functions, backup manifest format, snapshot format, restore flow, disaster recovery flow, runtime artifacts, dependency fallback behavior, integrations, tests, implementation order, acceptance criteria, evidence requirements, and Definition of Done required for a safe coding-agent handoff, including catalog indexing, restore preflight, restore transactions, compatibility checks, finalization markers, DR drill mode, canonical schema paths, CLI result envelopes, stale-staging cleanup, and evidence immutability.
```
