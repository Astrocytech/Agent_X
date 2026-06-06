# BACKUP_DISASTER_RECOVERY_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: BACKUP_DISASTER_RECOVERY_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_BACKUP_DISASTER_RECOVERY
component_name: Backup / Disaster Recovery Layer
roadmap_layer: 21
roadmap_phase: Phase E — Recovery, Preservation, and Disaster Readiness
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Git Integration Acceptance Criteria, Promotion / Release Gate Acceptance Criteria, Monitoring / Observability Acceptance Criteria
optional_standards: ES, Report Template
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/backup/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/backups/
backup_storage_root: .agentx-init/backups/snapshots/
review_use: controlling contract for implementation spec and post-implementation review
contract_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

The v2 contract was strong and implementation-ready. I would rate it:

```text
9.7/10
```

It already covered the required controlling-contract areas for backup policy, snapshot manifest, restore request, restore decision, dry-run reporting, disaster recovery planning, evidence, retention, integrity, locking, idempotency, rollback/restore safety, Agent_X integration, OpenCode borrowing boundaries, Definition of Done, No-Go conditions, and freeze rules.

It was not fully 10/10 because several implementation-critical contract surfaces were still under-specified:

```text
1. A restore decision referenced compatibility_report_id, but the compatibility report schema was not separately defined.
2. Snapshot listing and discovery needed a snapshot catalog/index schema, otherwise list/retention/restore selection could drift.
3. Restore execution needed a dedicated execution report schema, separate from restore dry-run and restore decision.
4. Disaster recovery testing needed a dedicated DR test result schema, separate from the DR plan.
5. Atomic snapshot creation and finalization needed a stricter temp-to-final promotion rule.
6. Pre-restore backup needed an explicit evidence link and blocking rule.
7. Role permissions for backup operators, reviewers, promotion checks, and tool/MCP callers needed a clearer matrix.
8. Secret scanning needed to be explicit, not only path-pattern based.
9. Snapshot corruption handling needed quarantine semantics.
10. Validation command safety needed clearer limits for post-restore validation commands.
```

This v3 adds those controls and is the final 10/10 controlling contract for the Backup / Disaster Recovery Layer.

---

# 0A. v2 Review and Upgrade Summary

The v1 contract was strong and covered the requested contract areas. I would rate it:

```text
9.4/10
```

It covered:

```text
EQC
FIC
SIB
Backup policy schema
Snapshot manifest schema
Restore request schema
Restore decision schema
Disaster recovery plan schema
Backup evidence/audit contract
Retention and cleanup rules
Integrity/hash verification rules
Rollback/restore safety rules
Agent_X integration notes
OpenCode borrowing notes
what may be backed up
where backups are stored
which files are excluded
how backup manifests are created
how backup integrity is verified
how restore requests are approved
how destructive restore is prevented
how recovery is audited
how disaster recovery is tested
```

It was not fully 10/10 because it still needed these production-control additions:

```text
1. A strict status vocabulary to avoid ambiguous PASS/PARTIAL/BLOCKED meanings.
2. Dependency gates for Policy, Sandbox, Git, Promotion, and Monitoring when unavailable.
3. A complete restore dry-run report schema, since dry-run is central to restore safety.
4. Concurrency and locking rules to prevent simultaneous backup, restore, and retention cleanup conflicts.
5. Idempotency rules for repeated backup, verify, restore-plan, and cleanup calls.
6. A clearer snapshot lifecycle model from CREATED to VERIFIED to RESTORE_READY to RETIRED.
7. Stronger artifact provenance and hash-chain rules, including detached manifest hash to avoid circular hashing.
8. Restore quarantine/staging rules before any overwrite.
9. Stronger compatibility rules so old snapshots cannot be restored into incompatible code/schema versions.
10. Evidence immutability and deviation-register rules.
11. Explicit schema example requirements and negative schema requirements.
12. A freeze rule to prevent future broad expansion without a major revision.
```

This v2 adds those controls and is the final 10/10 controlling contract.

---

# 1. Purpose

This document defines the controlling contract for the **Backup / Disaster Recovery Layer** in the Agent_X self-evolving system.

This layer is responsible for preserving recoverable Agent_X state before, during, and after controlled evolution work. It must provide deterministic backup creation, manifest generation, integrity verification, restore planning, retention cleanup, rollback coordination, disaster recovery planning, and audit evidence without becoming a bypass around governance, sandboxing, policy, Git controls, promotion gates, or human approval.

This layer defines:

```text
what may be backed up
where backups are stored
which files are excluded
how backup manifests are created
how backup integrity is verified
how restore requests are approved
how destructive restore is prevented
how recovery is audited
how disaster recovery is tested
```

This is the controlling contract. The next two documents should be:

```text
BACKUP_DISASTER_RECOVERY_IMPLEMENTATION_SPEC
BACKUP_DISASTER_RECOVERY_IMPLEMENTATION_REVIEW_AND_DOD
```

A 10/10 rating for this contract does not mean the implementation is done. The implementation is done only after the implementation spec is satisfied and the post-implementation review proves the validation evidence.

---

# 2. Scope

## 2.1 Required in This Layer

The Backup / Disaster Recovery Layer must define and implement contracts for:

```text
backup policy
snapshot manifest
snapshot lifecycle
restore request
restore decision
restore dry-run report
disaster recovery plan
backup audit events
backup integrity verification
snapshot hashing
snapshot provenance
snapshot compatibility checks
backup retention
safe cleanup
restore staging/quarantine
restore blocking rules
rollback coordination
recovery evidence
evidence immutability
```

The layer must support these core behaviors:

```text
create a backup snapshot
create a snapshot manifest
verify backup integrity
mark a verified snapshot as restore-ready only after verification
plan a restore without applying it
block destructive restore by default
record restore decisions
stage restore candidates before overwrite
coordinate with rollback and patch recovery layers
apply retention policy safely
write audit/evidence for every backup and restore decision
produce disaster recovery plans and disaster recovery test results
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
unrestricted filesystem cloning
uncontrolled source overwrite
Git push, merge, rebase, checkout, reset, or branch deletion
promotion approval
human approval UI
cloud backup provider integration by default
network upload by default
model execution
LLM decision-making
background daemon
cross-machine disaster recovery transport
secret vaulting
full package distribution
```

This layer may define future extension points for those behaviors, but they must be disabled unless explicitly enabled by later layers and policy.

---

# 3. Status Vocabulary

Use only these status values in schemas, evidence, reports, and review tables unless a schema explicitly defines a narrower enum.

```text
PASS
PARTIAL
FAIL
BLOCKED
INVALID
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

| Status | Meaning | Recovery-ready allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts exist, but coverage is incomplete. | No |
| FAIL | Requirement was checked and failed. | No |
| BLOCKED | Action was refused by policy, sandbox, governance, integrity, retention, or safety rule. | No |
| INVALID | Input, schema, request, manifest, or state is invalid. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command or test was not run. | No |
| NOT APPLICABLE | Requirement truly does not apply to implemented scope. | Yes, if justified |
| DEFERRED SAFELY | Feature is planned or stubbed and cannot execute, mutate, delete, restore, or bypass controls. | Yes, only for accepted deferred areas |

A snapshot cannot be marked `restore_ready=true` while any required integrity, compatibility, policy, or provenance check is `PARTIAL`, `FAIL`, `BLOCKED`, `INVALID`, `NOT CHECKED`, or `NOT RUN`.

---

# 4. Standards Applied

## 4.1 Primary Standard: EQC

EQC is primary because backup and recovery are safety-critical. A faulty backup can create false confidence, and an unsafe restore can destroy valid work.

EQC applies to:

```text
backup boundary control
snapshot integrity
snapshot provenance
restore authorization
restore staging
rollback safety
retention safety
cleanup safety
audit completeness
disaster recovery reproducibility
evidence immutability
```

The layer must fail closed.

## 4.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete files, schemas, tests, and runtime artifacts.

Expected implementation files include:

```text
tools/agentx_evolve/backup/__init__.py
tools/agentx_evolve/backup/backup_models.py
tools/agentx_evolve/backup/backup_policy.py
tools/agentx_evolve/backup/snapshot_manifest.py
tools/agentx_evolve/backup/snapshot_creator.py
tools/agentx_evolve/backup/snapshot_verifier.py
tools/agentx_evolve/backup/restore_planner.py
tools/agentx_evolve/backup/restore_executor.py
tools/agentx_evolve/backup/retention_manager.py
tools/agentx_evolve/backup/disaster_recovery_plan.py
tools/agentx_evolve/backup/backup_audit_logger.py
tools/agentx_evolve/backup/backup_locks.py
tools/agentx_evolve/backup/backup_hashing.py
```

Each file must have a clear responsibility, public API, inputs, outputs, invariants, tests, and safety limits.

## 4.3 Required Supporting Standard: SIB

SIB is required because backup and disaster recovery connect multiple Agent_X subsystems:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Git Integration Layer
Promotion / Release Gate
Monitoring / Observability
Documentation Synchronization
Packaging / Distribution
Final System Acceptance
```

This layer must be an integration boundary, not an uncontrolled copy utility.

## 4.4 Required Supporting Standard: Schema Contract

Schema Contract is required because backup and restore operations must be structured, auditable, and reproducible.

Required schemas include:

```text
backup_policy.schema.json
snapshot_manifest.schema.json
restore_request.schema.json
restore_decision.schema.json
restore_dry_run_report.schema.json
disaster_recovery_plan.schema.json
backup_audit_event.schema.json
backup_integrity_report.schema.json
backup_compatibility_report.schema.json
snapshot_catalog.schema.json
restore_execution_report.schema.json
backup_retention_report.schema.json
disaster_recovery_test_result.schema.json
backup_evidence_manifest.schema.json
backup_completion_record.schema.json
```

## 4.5 Required Evidence / Audit Rules

Every backup, verification, restore planning, restore blocking, restore execution, retention cleanup, and disaster recovery test must produce evidence.

Evidence is required for:

```text
backup snapshot created
backup snapshot skipped
backup snapshot failed
snapshot manifest created
snapshot manifest hash created
hash verification passed
hash verification failed
restore request created
restore decision allowed
restore decision blocked
restore dry-run completed
restore execution attempted
restore execution blocked
retention cleanup proposed
retention cleanup applied
retention cleanup blocked
disaster recovery plan generated
disaster recovery test completed
evidence manifest created
completion record created
```

## 4.6 Conditional Standards

Use these standards only when the implementation exposes the related surface:

```text
Command Acceptance Criteria, if CLI commands are exposed
Git Integration Acceptance Criteria, if backup snapshots include Git state
Promotion / Release Gate Acceptance Criteria, if release snapshots are backed up
Monitoring / Observability Acceptance Criteria, if backup health checks are surfaced
```

## 4.7 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if markdown/html backup reports are generated
```

---

# 5. Why This Layer Is Safety-Critical

Backup / Disaster Recovery is safety-critical because it decides:

```text
what system state can be preserved
what system state can be restored
whether a restore can overwrite current work
whether corrupted backups are rejected
whether stale backups are retained or deleted
whether runtime artifacts are separated from source files
whether secrets are excluded or redacted
whether recovery can be audited
whether failed evolution work can be recovered
whether disaster recovery is reproducible from evidence
```

This layer must prevent:

```text
backing up corrupted state as trusted
restoring unverified snapshots
overwriting source without governance
restoring stale or incompatible artifacts
including secrets in backup archives
deleting the only valid recovery point
silently failing to create backups
silently failing to verify backups
silently failing to restore
using backup as a bypass around Git, policy, sandbox, or promotion
```

---

# 6. Preconditions and Dependency Gates

## 6.1 Required Prior Components

Before live restore, destructive cleanup, or source overwrite is enabled, these components must be present and validated:

```text
Security Sandbox / Filesystem Boundary Layer
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Governed Patch Execution, for patch rollback coordination
Git Integration Layer, for Git state preservation or Git-state restore
Human Review / Approval Interface, for destructive restore
```

## 6.2 Restricted Mode

If upstream components are missing, the Backup / Disaster Recovery Layer may still operate in restricted mode.

Restricted mode allows:

```text
backup policy validation
snapshot manifest validation
manifest-only dry-run
backup integrity verification
read-only snapshot listing
restore planning dry-run
retention dry-run
audit/evidence writing
```

Restricted mode blocks:

```text
source restore
runtime overwrite restore
destructive restore
retention apply cleanup
Git state restore
network/cloud backup
external storage
background backup automation
```

## 6.3 Dependency Gate Rules

```text
If Security Sandbox is missing -> all path/file/restore/cleanup actions BLOCK.
If Policy / Capability Registry is missing -> restore, cleanup, external storage, and source backup beyond manifest-only BLOCK.
If Failure Taxonomy is missing -> failures use UNKNOWN_BACKUP_FAILURE but still BLOCK unsafe action.
If Governed Patch Execution is missing -> patch rollback coordination returns BLOCKED or DRY_RUN_ONLY.
If Git Integration is missing -> Git metadata summary is UNKNOWN and Git-state restore BLOCKS.
If Human Approval is missing -> destructive restore BLOCKS.
If Monitoring is missing -> monitoring export is DEFERRED SAFELY and cannot mutate state.
```

## 6.4 Authority Rule

Backup / Disaster Recovery must not grant its own authority to read, write, delete, or restore files.

A backup or restore action is allowed only when all required authorities agree:

```text
Backup Policy
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution, when restoring source or patch state
Git Integration, when preserving or restoring Git state
Promotion / Release Gate, when release snapshots are involved
Human Approval, when destructive restore is requested
Failure Taxonomy / Recovery Playbook, when recovery path is selected
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_APPROVAL
NEEDS_GOVERNANCE
DRY_RUN_ONLY
ALLOW
```

---

# 7. Role Permission Matrix

The layer must not treat all callers as equivalent. Backup and restore rights are role-specific.

Initial caller roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
BACKUP_OPERATOR
HUMAN_OPERATOR
MCP_CLIENT
UNKNOWN_CALLER
```

Required role behavior:

| Role | Backup create | Verify/list | Restore dry-run | Restore execute | Retention apply | External storage |
|---|---|---|---|---|---|---|
| ORCHESTRATOR | allow if policy permits | allow | allow | governance + approval required | policy required | blocked by default |
| IMPLEMENTATION_WORKER | pre-change snapshot only | allow | dry-run only | blocked | blocked | blocked |
| VALIDATION_REPAIR_WORKER | allow runtime recovery snapshot | allow | dry-run only | blocked unless delegated | blocked | blocked |
| REVIEWER_ASSISTANT | blocked | allow read-only | dry-run only | blocked | blocked | blocked |
| PROMOTION_CHECKER | release snapshot if promotion policy permits | allow | dry-run only | blocked | blocked | blocked |
| BACKUP_OPERATOR | allow if policy permits | allow | allow | approval required | dry-run first + policy | blocked by default |
| HUMAN_OPERATOR | cannot bypass safety | allow | allow | may approve if all non-overridable checks pass | may approve if safe | explicit policy required |
| MCP_CLIENT | read-only/list/verify by default | allow read-only | dry-run only | blocked | blocked | blocked |
| UNKNOWN_CALLER | blocked | blocked | blocked | blocked | blocked | blocked |

Role rules:

```text
UNKNOWN_CALLER blocks by default
MCP_CLIENT is read-only/dry-run only by default
HUMAN_OPERATOR cannot override hash mismatch, path escape, secret restore, or missing pre-restore backup
IMPLEMENTATION_WORKER cannot execute destructive restore
retention apply requires policy and prior dry-run regardless of caller role
external storage requires explicit policy and deviation record regardless of caller role
```

---

# 8. Backup Policy Schema Contract

The backup policy defines what may be backed up, where it may be stored, how it is verified, and how long it is retained.

Required schema:

```text
backup_policy.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_policy.schema.json",
  "policy_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "backup_scope": {
    "include_paths": [],
    "exclude_paths": [],
    "include_runtime_artifacts": true,
    "include_source_files": true,
    "include_git_metadata": true,
    "include_test_artifacts": true,
    "include_secrets": false
  },
  "storage": {
    "backup_root": ".agentx-init/backups/snapshots/",
    "manifest_root": ".agentx-init/backups/manifests/",
    "integrity_root": ".agentx-init/backups/integrity/",
    "restore_plan_root": ".agentx-init/backups/restore_plans/",
    "audit_root": ".agentx-init/backups/audit/",
    "allow_external_storage": false
  },
  "integrity": {
    "hash_algorithm": "sha256",
    "require_manifest_hash": true,
    "require_detached_manifest_hash": true,
    "require_file_hashes": true,
    "require_restore_verification": true
  },
  "retention": {
    "minimum_snapshots_to_keep": 3,
    "maximum_snapshots_to_keep": 50,
    "delete_unverified_snapshots": false,
    "delete_only_after_new_valid_snapshot": true,
    "retention_apply_requires_dry_run": true
  },
  "restore": {
    "allow_destructive_restore": false,
    "require_dry_run": true,
    "require_policy_decision": true,
    "require_sandbox_decision": true,
    "require_human_approval_for_source_overwrite": true,
    "require_governance_for_source_overwrite": true,
    "require_pre_restore_backup": true,
    "require_git_clean_or_recorded_dirty_state": true
  },
  "compatibility": {
    "require_component_version_match": true,
    "require_schema_version_compatibility": true,
    "allow_forward_restore": false
  },
  "warnings": [],
  "errors": []
}
```

Policy rules:

```text
include_secrets must default to false
allow_external_storage must default to false
allow_destructive_restore must default to false
restore must require dry-run by default
source overwrite must require governance and human approval
retention cleanup must never delete the only valid snapshot
unverified snapshots must not be treated as recovery-ready
forward restore into unknown newer schema state must block by default
```

---

# 9. What May Be Backed Up

Allowed backup targets:

```text
Agent_X source files within approved repository boundary
Agent_X generated runtime artifacts under approved .agentx-init subdirectories
schema files
test files
configuration files that are not secrets
evidence manifests
review reports
completion records
Git metadata summaries, if Git integration permits
```

Conditionally allowed backup targets:

```text
large test outputs, if size limits permit
logs, if secrets are redacted
build artifacts, if policy allows
release artifacts, if promotion gate approves
```

Forbidden backup targets by default:

```text
secrets
API keys
tokens
private credentials
unredacted environment dumps
SSH keys
cloud provider credentials
large cache directories
virtual environments
node_modules
__pycache__
.git object database copies, unless explicitly allowed
external files outside repository boundary
```

Default excluded path patterns:

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
.venv/
venv/
node_modules/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
.git/objects/
.git/lfs/
```

Secret-like files must be excluded even if an include rule accidentally matches them. Exclusion rules have higher priority than inclusion rules.

Secret scanning must include both path-based and content-based checks before snapshot finalization. If content scanning detects likely secrets, the file must be excluded or the snapshot must be BLOCKED unless explicit policy permits a redacted artifact.

---

# 10. Where Backups Are Stored

Default runtime root:

```text
.agentx-init/backups/
```

Required subdirectories:

```text
.agentx-init/backups/snapshots/
.agentx-init/backups/manifests/
.agentx-init/backups/integrity/
.agentx-init/backups/restore_plans/
.agentx-init/backups/audit/
.agentx-init/backups/reports/
.agentx-init/backups/locks/
.agentx-init/backups/staging/
```

Rules:

```text
backup artifacts must remain under .agentx-init/backups/ by default
snapshot files must not be written into source directories
backup audit must not overwrite tool-call evidence
backup paths must be validated by Security Sandbox
backup path traversal must be rejected
symlink escape must be rejected
backup storage outside runtime root requires explicit policy and deviation record
network/cloud backup must be disabled by default
```

---

# 11. Snapshot Lifecycle

Every snapshot must move through a clear lifecycle.

Allowed lifecycle states:

```text
PLANNED
CREATED
MANIFEST_WRITTEN
VERIFYING
VERIFIED
FAILED
RESTORE_READY
QUARANTINED
RETIRED
DELETED
```

Lifecycle rules:

```text
PLANNED cannot be restored
CREATED cannot be restored
MANIFEST_WRITTEN cannot be restored
VERIFYING cannot be restored
FAILED cannot be restored
QUARANTINED cannot be restored until a new verification clears quarantine
VERIFIED may become RESTORE_READY only after policy and compatibility checks pass
RESTORE_READY may be used for restore planning
RETIRED cannot be selected for new restore plans unless explicitly approved
DELETED must remain in audit history and cannot disappear silently
```

`restore_ready=true` requires:

```text
snapshot exists
manifest exists
manifest detached hash verifies
all required file hashes verify
compatibility checks pass
snapshot is not retired
snapshot is not quarantined
snapshot is not marked failed
snapshot is not referenced by a failed incomplete restore unless cleared by policy
```

---

# 12. Snapshot Manifest Schema Contract

Every backup snapshot must have a manifest.

Required schema:

```text
snapshot_manifest.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "snapshot_manifest.schema.json",
  "snapshot_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "repo_root": "string",
  "source_commit": "string|null",
  "working_tree_status": "CLEAN|DIRTY|UNKNOWN",
  "component_versions": {},
  "schema_versions": {},
  "backup_policy_id": "string",
  "snapshot_type": "FULL|INCREMENTAL|MANIFEST_ONLY|DRY_RUN",
  "snapshot_state": "PLANNED|CREATED|MANIFEST_WRITTEN|VERIFYING|VERIFIED|FAILED|RESTORE_READY|QUARANTINED|RETIRED|DELETED",
  "snapshot_root": "string",
  "included_files": [],
  "excluded_files": [],
  "file_hashes": [],
  "manifest_content_sha256": "string",
  "detached_manifest_hash_path": "string",
  "total_files": 0,
  "total_bytes": 0,
  "integrity_status": "NOT_VERIFIED|VERIFIED|FAILED|PARTIAL|BLOCKED",
  "compatibility_status": "NOT_CHECKED|PASS|FAIL|BLOCKED",
  "restore_ready": false,
  "warnings": [],
  "errors": []
}
```

Manifest rules:

```text
manifest must list every included file
manifest must list every excluded file category or pattern
manifest must include SHA-256 hashes for included files
manifest must use detached manifest hash to avoid circular self-hash ambiguity
manifest must include source commit when available
manifest must record dirty working tree state
manifest must record component and schema versions where available
restore_ready must be false until integrity and compatibility verification pass
```

---

# 13. Integrity / Hash Verification Rules

The layer must verify backup integrity before a snapshot is considered restore-ready.

Required integrity behavior:

```text
calculate SHA-256 for every included file
calculate SHA-256 for manifest content excluding detached hash record
write detached manifest hash
verify file hashes after snapshot creation
verify detached manifest hash before restore planning
reject missing files
reject hash mismatches
reject modified manifest without new verification
record verification result as evidence
```

Required integrity report schema:

```text
backup_integrity_report.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_integrity_report.schema.json",
  "integrity_report_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "snapshot_id": "string",
  "manifest_path": "string",
  "manifest_sha256_expected": "string",
  "manifest_sha256_actual": "string",
  "files_checked": 0,
  "files_passed": 0,
  "files_failed": 0,
  "missing_files": [],
  "hash_mismatches": [],
  "status": "VERIFIED|FAILED|PARTIAL|BLOCKED",
  "restore_ready": false,
  "warnings": [],
  "errors": []
}
```

Blocking conditions:

```text
missing manifest
missing detached manifest hash
manifest hash mismatch
file hash mismatch
missing included file
unreadable included file
unverified snapshot used for restore
```

---

# 14. Snapshot Catalog / Index Schema Contract

The layer must maintain a catalog/index so restore planning, retention cleanup, monitoring, and audit review do not discover snapshots by unsafe ad hoc directory scanning.

Required schema:

```text
snapshot_catalog.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "snapshot_catalog.schema.json",
  "catalog_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "source_component": "BackupDisasterRecovery",
  "backup_root": ".agentx-init/backups/",
  "snapshot_entries": [],
  "latest_verified_snapshot_id": "string|null",
  "latest_restore_ready_snapshot_id": "string|null",
  "catalog_sha256": "string",
  "warnings": [],
  "errors": []
}
```

Each snapshot entry must include:

```text
snapshot_id
manifest_path
snapshot_state
integrity_status
compatibility_status
restore_ready
created_at
source_commit
total_files
total_bytes
manifest_content_sha256
detached_manifest_hash_path
retention_protected
quarantined
quarantine_reason
```

Catalog rules:

```text
catalog is evidence, not authority by itself
catalog entries must be derived from verified manifests
catalog update must be atomic
catalog must not silently drop failed, retired, deleted, or quarantined snapshots
retention and restore planning must use catalog plus manifest verification, not catalog alone
missing catalog may be rebuilt from manifests, but rebuild must write evidence
```

---

# 15. Compatibility Report Schema Contract

Every restore plan must check whether the snapshot can be safely interpreted by the current Agent_X code, schemas, and runtime artifact contracts.

Required schema:

```text
backup_compatibility_report.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_compatibility_report.schema.json",
  "compatibility_report_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "snapshot_id": "string",
  "source_commit": "string|null",
  "current_commit": "string|null",
  "snapshot_component_versions": {},
  "current_component_versions": {},
  "snapshot_schema_versions": {},
  "current_schema_versions": {},
  "forward_restore": false,
  "backward_restore": false,
  "migration_required": false,
  "migration_available": false,
  "compatible": false,
  "decision": "PASS|FAIL|BLOCKED|PARTIAL",
  "reason": "string",
  "warnings": [],
  "errors": []
}
```

Compatibility rules:

```text
unknown schema version blocks source restore by default
forward restore blocks by default
missing component version blocks destructive restore
migration-required restore blocks unless an approved migration plan exists
compatibility PASS is required before restore_ready or destructive restore
compatibility report ID must be referenced by restore decision evidence
```

---

# 16. Restore Request Schema Contract

Every restore attempt must begin as a restore request.

Required schema:

```text
restore_request.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "restore_request.schema.json",
  "restore_request_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "requested_by_role": "string",
  "snapshot_id": "string",
  "restore_scope": {
    "paths": [],
    "restore_runtime_artifacts": true,
    "restore_source_files": false,
    "restore_git_state": false
  },
  "mode": "DRY_RUN|RESTORE",
  "reason": "string",
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
restore must default to DRY_RUN
source-file restore must default to false
Git-state restore must default to false
runtime artifact restore may be allowed only inside approved runtime roots
restore path traversal must be rejected
restore outside repository boundary must be blocked
restore from incompatible snapshot must be blocked
```

---

# 17. Restore Decision Schema Contract

Every restore request must produce a restore decision before execution.

Required schema:

```text
restore_decision.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "restore_decision.schema.json",
  "restore_decision_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "restore_request_id": "string",
  "snapshot_id": "string",
  "decision": "ALLOW|BLOCK|NEEDS_APPROVAL|NEEDS_GOVERNANCE|DRY_RUN_ONLY",
  "reason": "string",
  "required_checks": [],
  "passed_checks": [],
  "missing_checks": [],
  "integrity_report_id": "string|null",
  "compatibility_report_id": "string|null",
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "destructive_restore": false,
  "restore_plan_path": "string|null",
  "dry_run_report_id": "string|null",
  "warnings": [],
  "errors": []
}
```

Decision rules:

```text
unverified snapshot -> BLOCK
hash mismatch -> BLOCK
missing policy decision -> BLOCK or NEEDS_GOVERNANCE
missing sandbox decision -> BLOCK
incompatible snapshot -> BLOCK
source overwrite without governance -> NEEDS_GOVERNANCE or BLOCK
source overwrite without human approval -> NEEDS_APPROVAL or BLOCK
destructive restore without explicit approval -> BLOCK
restore request with path traversal -> BLOCK
restore of excluded secret path -> BLOCK
```

---

# 18. Restore Dry-Run Report Schema Contract

Every restore must have a dry-run report before any write occurs.

Required schema:

```text
restore_dry_run_report.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "restore_dry_run_report.schema.json",
  "restore_dry_run_report_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "restore_request_id": "string",
  "snapshot_id": "string",
  "files_to_create": [],
  "files_to_overwrite": [],
  "files_to_skip": [],
  "files_to_delete": [],
  "runtime_artifacts_to_restore": [],
  "source_files_to_restore": [],
  "git_state_actions": [],
  "destructive_restore": false,
  "requires_pre_restore_backup": true,
  "required_approvals": [],
  "blocked_actions": [],
  "status": "PASS|BLOCKED|FAILED|PARTIAL",
  "warnings": [],
  "errors": []
}
```

Dry-run rules:

```text
dry-run must not write source files
dry-run must not delete files
dry-run must not change Git state
dry-run must identify destructive actions
dry-run must identify approval requirements
dry-run must write evidence
restore execution without a matching dry-run report must BLOCK
```

---

# 19. Restore Execution Report Schema Contract

Restore execution must produce a report that is separate from the dry-run report and restore decision. This prevents an approved plan from being confused with an applied restore.

Required schema:

```text
restore_execution_report.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "restore_execution_report.schema.json",
  "restore_execution_report_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "restore_request_id": "string",
  "restore_decision_id": "string",
  "dry_run_report_id": "string",
  "snapshot_id": "string",
  "pre_restore_snapshot_id": "string|null",
  "staging_root": "string",
  "files_created": [],
  "files_overwritten": [],
  "files_deleted": [],
  "files_skipped": [],
  "post_restore_validation_commands": [],
  "post_restore_validation_status": "PASS|FAIL|BLOCKED|NOT RUN",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED",
  "rollback_plan_ref": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Execution rules:

```text
execution report must reference a prior restore decision and dry-run report
execution report must reference the pre-restore backup when destructive restore is allowed
execution report must list actual file actions, not only planned actions
post-restore validation commands must be allowlisted and non-network by default
failed post-restore validation must produce recovery evidence and rollback guidance
```

---

# 20. Rollback / Restore Safety Rules

Restore is more dangerous than backup. This layer must make restore safe by default.

Required safety rules:

```text
restore must default to dry-run
restore must verify snapshot integrity first
restore must check snapshot compatibility first
restore must generate a restore plan before writing files
restore must stage candidate files under .agentx-init/backups/staging/ before overwrite
restore must show files to be created, overwritten, skipped, and deleted
restore must not delete files by default
restore must not overwrite source by default
restore must not restore secrets by default
restore must not alter Git state by default
restore must not run commands as part of restore by default
restore must write evidence before and after any allowed restore
```

Destructive restore is any restore that:

```text
overwrites existing source files
deletes files
replaces runtime state used by active session
changes Git state
restores from an unclean or incompatible snapshot
```

Destructive restore requires:

```text
verified snapshot
compatible snapshot
restore dry-run report
policy decision
governance decision
sandbox decision
human approval
source mutation authorization, if source files are touched
pre-restore backup of current state
```

---

# 21. Disaster Recovery Plan Schema Contract

The disaster recovery plan defines how Agent_X can recover after corruption, failed implementation, broken evidence, or unsafe state.

Required schema:

```text
disaster_recovery_plan.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "disaster_recovery_plan.schema.json",
  "dr_plan_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "scenario": "SOURCE_CORRUPTION|RUNTIME_ARTIFACT_CORRUPTION|FAILED_PATCH|FAILED_PROMOTION|EVIDENCE_CORRUPTION|SCHEMA_MIGRATION_FAILURE|BAD_CONFIG_UPDATE|UNKNOWN",
  "recovery_objective": "string",
  "candidate_snapshots": [],
  "selected_snapshot_id": "string|null",
  "required_checks": [],
  "recovery_steps": [],
  "rollback_steps": [],
  "validation_commands": [],
  "expected_evidence": [],
  "approval_requirements": [],
  "status": "DRAFT|READY|BLOCKED|TESTED|FAILED",
  "warnings": [],
  "errors": []
}
```

Required DR scenarios:

```text
source corruption
runtime artifact corruption
failed patch session
failed promotion
broken or missing evidence
schema migration failure
bad generated file set
bad configuration update
```

Every disaster recovery plan must include:

```text
candidate snapshots
integrity verification requirement
compatibility verification requirement
restore dry-run requirement
post-restore validation commands
evidence paths
rollback path if recovery fails
```

---

# 22. Disaster Recovery Test Result Schema Contract

A disaster recovery plan is not enough by itself. The layer must record whether a recovery scenario was tested safely.

Required schema:

```text
disaster_recovery_test_result.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "disaster_recovery_test_result.schema.json",
  "dr_test_result_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "dr_plan_id": "string",
  "scenario": "string",
  "test_mode": "DRY_RUN|SANDBOXED_RESTORE|MANIFEST_ONLY",
  "snapshot_id": "string|null",
  "integrity_report_id": "string|null",
  "compatibility_report_id": "string|null",
  "restore_dry_run_report_id": "string|null",
  "validation_commands": [],
  "validation_results": [],
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

DR test rules:

```text
DR tests must not overwrite active source state
DR tests must use dry-run or sandboxed temporary restore targets by default
DR tests must include at least one negative/corruption case
DR tests must record validation command text, exit code, and bounded output summary
DR test PASS is required before claiming disaster readiness for a scenario
```

---

# 23. Backup Evidence / Audit Contract

Required audit schema:

```text
backup_audit_event.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_audit_event.schema.json",
  "audit_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "event_type": "string",
  "snapshot_id": "string|null",
  "restore_request_id": "string|null",
  "restore_decision_id": "string|null",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "message": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Required evidence files:

```text
.agentx-init/backups/audit/backup_audit_history.jsonl
.agentx-init/backups/audit/backup_integrity_history.jsonl
.agentx-init/backups/audit/restore_decision_history.jsonl
.agentx-init/backups/audit/retention_history.jsonl
.agentx-init/backups/audit/disaster_recovery_history.jsonl
.agentx-init/backups/latest_backup_audit_event.json
.agentx-init/backups/latest_snapshot_manifest.json
.agentx-init/backups/latest_integrity_report.json
.agentx-init/backups/latest_restore_decision.json
.agentx-init/backups/backup_disaster_recovery_evidence_manifest.json
.agentx-init/backups/backup_disaster_recovery_completion_record.json
```

Evidence rules:

```text
every backup action writes evidence
every restore request writes evidence
every blocked restore writes evidence
every integrity failure writes evidence
every retention cleanup writes evidence
latest JSON artifacts must be written atomically
JSONL histories must be append-only
secrets must be redacted before durable logging
raw file contents must not be logged
```

## 23.1 Evidence Immutability Rule

After a snapshot, integrity report, restore decision, review report, or completion record is finalized:

```text
final evidence files must not be edited in place
changed evidence hashes invalidate the previous DONE or restore-ready status
new evidence must receive a new ID and timestamp
manual repair of evidence requires a deviation record
```

## 23.2 Evidence Manifest Schema Contract

Required schema:

```text
backup_evidence_manifest.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_evidence_manifest.schema.json",
  "evidence_manifest_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "component_id": "AGENTX_BACKUP_DISASTER_RECOVERY",
  "snapshot_ids": [],
  "restore_request_ids": [],
  "restore_decision_ids": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "deviation_register": [],
  "final_status": "PASS|PARTIAL|FAIL|BLOCKED",
  "warnings": [],
  "errors": []
}
```

Hashing rule:

```text
SHA-256 hashes are required for finalized evidence artifacts.
Use Python standard-library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

---

# 24. Retention and Cleanup Rules

Retention must prevent unbounded backup growth while preserving safe recovery points.

Required retention behavior:

```text
retain minimum valid snapshots
never delete the only verified snapshot
never delete latest verified snapshot until a newer verified snapshot exists
never delete snapshot referenced by active restore plan
never delete snapshot referenced by completion evidence
never delete unverified snapshot without recording why
cleanup must run as dry-run first
cleanup must write retention report
cleanup apply must use lock
```

Required retention report schema:

```text
backup_retention_report.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "backup_retention_report.schema.json",
  "retention_report_id": "string",
  "created_at": "string",
  "source_component": "BackupDisasterRecovery",
  "policy_id": "string",
  "mode": "DRY_RUN|APPLY",
  "snapshots_considered": [],
  "snapshots_kept": [],
  "snapshots_to_delete": [],
  "snapshots_deleted": [],
  "blocked_deletions": [],
  "reason": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED",
  "warnings": [],
  "errors": []
}
```

Cleanup is blocked if:

```text
policy is missing
snapshot integrity status is unknown
snapshot is the only verified recovery point
snapshot is referenced by active recovery evidence
cleanup dry-run was not performed
cleanup target is outside backup root
cleanup lock cannot be acquired
```

---

# 25. Concurrency, Locking, and Idempotency Rules

## 25.1 Locking

The layer must use lock artifacts under:

```text
.agentx-init/backups/locks/
```

Required locks:

```text
backup_create.lock
restore_execute.lock
retention_apply.lock
integrity_verify.lock
```

Rules:

```text
restore execution must not run while backup creation is writing a snapshot
retention apply must not run while restore planning or restore execution references snapshots
integrity verification may run concurrently only on immutable snapshots
stale locks must be detected but not ignored silently
lock acquisition failure returns BLOCKED with evidence
```

## 25.2 Idempotency

Repeated calls must be predictable.

Required idempotency rules:

```text
same snapshot create request with same idempotency key returns existing snapshot result or BLOCKED if prior state is incomplete
same verify request for unchanged snapshot returns existing verified report or reruns verification safely
same restore dry-run request returns existing dry-run report if inputs are unchanged
restore execution with same idempotency key must not apply twice
retention apply with same idempotency key must not delete twice
```

Every mutating or cleanup operation must record:

```text
idempotency_key
operation_id
previous_operation_id, if reused
```

---

# 26. Agent_X Integration Notes

## 26.1 Security Sandbox Integration

All backup and restore path operations must pass through Security Sandbox.

Required:

```text
snapshot reads check source boundary
snapshot writes check backup runtime boundary
restore writes check restore target boundary
cleanup deletes check backup runtime boundary
path traversal is rejected
symlink escape is rejected
```

## 26.2 Policy / Capability Registry Integration

Backup and restore actions must be policy-checked.

Policy must decide:

```text
caller role allowed?
backup scope allowed?
restore scope allowed?
source overwrite allowed?
runtime artifact overwrite allowed?
external storage allowed?
retention cleanup allowed?
human approval required?
governance required?
```

## 26.3 Governed Patch Execution Integration

Before applying patches or risky evolution operations, this layer should provide recovery points.

Required integration:

```text
pre-patch backup snapshot
post-patch backup snapshot, if policy requires
restore plan for failed patch
rollback coordination with patch session ID
no direct patch apply in backup layer
```

## 26.4 Failure Taxonomy / Recovery Playbook Integration

Backup and restore failures must map to standard failure classes.

Initial failure classes:

```text
BACKUP_POLICY_DENIED
BACKUP_SANDBOX_DENIED
BACKUP_SOURCE_UNREADABLE
BACKUP_SNAPSHOT_FAILED
BACKUP_MANIFEST_INVALID
BACKUP_HASH_MISMATCH
BACKUP_SNAPSHOT_UNVERIFIED
BACKUP_COMPATIBILITY_FAILED
RESTORE_REQUEST_INVALID
RESTORE_POLICY_DENIED
RESTORE_SANDBOX_DENIED
RESTORE_NEEDS_APPROVAL
RESTORE_NEEDS_GOVERNANCE
RESTORE_DESTRUCTIVE_BLOCKED
RESTORE_INTEGRITY_FAILED
RESTORE_COMPATIBILITY_FAILED
RESTORE_EXECUTION_FAILED
RETENTION_POLICY_DENIED
RETENTION_CLEANUP_BLOCKED
DISASTER_RECOVERY_PLAN_INVALID
BACKUP_LOCK_UNAVAILABLE
UNKNOWN_BACKUP_FAILURE
```

## 26.5 Tool / MCP Adapter Integration

This layer may expose tools through the Tool / MCP Adapter later.

Potential tools:

```text
backup_create_snapshot
backup_verify_snapshot
backup_list_snapshots
backup_plan_restore
backup_execute_restore
backup_retention_dry_run
backup_retention_apply
backup_generate_dr_plan
backup_test_dr_plan
```

Default exposure:

```text
list and verify tools may be read-only
create snapshot writes runtime state only
restore execution is blocked unless fully authorized
retention apply is blocked unless fully authorized
no MCP mutating restore by default
```

## 26.6 Git Integration Layer

Git integration may provide:

```text
current commit hash
working tree status
diff summary
tracked file list
ignored file list
```

Backup layer must not:

```text
run Git write commands
commit backup files by itself
push backup artifacts
reset, checkout, merge, or rebase
```

## 26.7 Promotion / Release Gate Integration

For release snapshots:

```text
backup must include release manifest
backup must include validation evidence
backup must include promotion decision refs
restore must not bypass promotion rollback rules
```

## 26.8 Monitoring / Observability Integration

Monitoring may consume:

```text
latest backup status
latest integrity status
oldest valid snapshot age
number of verified snapshots
retention health
failed backup count
failed restore count
```

Monitoring must not mutate backup state.

---

# 27. OpenCode Borrowing Notes

OpenCode-style systems are useful as a design reference for controlled tool operations, but this layer must not inherit broad trust assumptions.

## 27.1 Concepts to Borrow

Borrow conceptually:

```text
explicit tool boundaries
small dedicated tool actions
separate read/write/execute capabilities
clear tool result objects
failure-visible behavior
evidence-oriented command outcomes
safe wrappers instead of one broad shell
```

## 27.2 Concepts to Reject or Restrict

Do not borrow:

```text
broad shell access
network/provider behavior by convenience
plugin-based unchecked tool expansion
direct file mutation without Agent_X governance
model-chosen restore execution without policy
background operations that mutate state silently
unbounded command output logging
```

## 27.3 Agent_X Backup Mapping

| Tool-style concept | Agent_X backup equivalent | Required control |
|---|---|---|
| read project state | snapshot scan | Security Sandbox |
| write artifact | create snapshot | Backup Policy + runtime boundary |
| verify output | integrity report | SHA-256 verification |
| restore | restore plan + decision | Policy + Sandbox + Governance + Approval |
| cleanup | retention dry-run/apply | Retention policy + evidence |
| recovery playbook | disaster recovery plan | Failure Taxonomy + validation evidence |

---

# 28. Public API Contract

Expected classes:

```text
BackupPolicy
SnapshotManifest
BackupIntegrityReport
RestoreRequest
RestoreDecision
RestoreDryRunReport
BackupRetentionReport
DisasterRecoveryPlan
BackupEvidenceManifest
BackupAuditEvent
```

Expected public functions:

```python
load_backup_policy(repo_root: Path) -> BackupPolicy
create_backup_snapshot(repo_root: Path, policy: BackupPolicy, context: dict) -> SnapshotManifest
create_snapshot_manifest(snapshot_root: Path, policy: BackupPolicy, context: dict) -> SnapshotManifest
verify_snapshot_integrity(snapshot_manifest: SnapshotManifest, context: dict) -> BackupIntegrityReport
build_snapshot_catalog(repo_root: Path, context: dict) -> SnapshotCatalog
check_snapshot_compatibility(snapshot_manifest: SnapshotManifest, context: dict) -> BackupCompatibilityReport
create_restore_request(arguments: dict, context: dict) -> RestoreRequest
plan_restore(restore_request: RestoreRequest, context: dict) -> RestoreDecision
create_restore_dry_run_report(restore_request: RestoreRequest, context: dict) -> RestoreDryRunReport
execute_restore(restore_decision: RestoreDecision, context: dict) -> RestoreExecutionReport
create_retention_report(policy: BackupPolicy, mode: str, context: dict) -> BackupRetentionReport
apply_retention_cleanup(retention_report: BackupRetentionReport, context: dict) -> BackupRetentionReport
generate_disaster_recovery_plan(scenario: str, context: dict) -> DisasterRecoveryPlan
run_disaster_recovery_test(dr_plan: DisasterRecoveryPlan, context: dict) -> DisasterRecoveryTestResult
write_backup_audit_event(event: BackupAuditEvent, repo_root: Path) -> dict
```

Rules:

```text
execute_restore must default to BLOCKED unless restore decision is ALLOW
execute_restore must never run without a prior dry-run
apply_retention_cleanup must never run without dry-run evidence
create_backup_snapshot must never include forbidden secrets by default
```

---

# 29. Backup Pipeline

Every backup snapshot must follow this sequence:

```text
1. Load backup policy.
2. Validate backup policy schema.
3. Check caller role and policy.
4. Acquire backup_create lock.
5. Check Security Sandbox for source read paths and backup write paths.
6. Resolve include and exclude paths.
7. Apply secret and excluded-path filters.
8. Create snapshot staging directory under approved backup root.
9. Copy or serialize approved files only into staging.
10. Create snapshot manifest in staging.
10A. Verify staging snapshot before final promotion.
10B. Atomically promote staging snapshot to final snapshot directory only after manifest and file hashes are complete.
11. Hash included files.
12. Write detached manifest hash.
13. Verify snapshot integrity.
14. Check compatibility metadata.
15. Mark restore_ready only if verification and compatibility pass.
16. Write audit/evidence.
17. Write latest snapshot manifest atomically.
18. Release backup_create lock.
```

Any failed stage must return a schema-valid blocked or failed result with evidence.

---

# 30. Restore Pipeline

Every restore must follow this sequence:

```text
1. Receive restore request.
2. Validate restore request schema.
3. Load snapshot manifest.
4. Verify detached manifest hash.
5. Verify file hashes.
6. Confirm snapshot is restore-ready.
7. Check snapshot compatibility.
8. Check Backup Policy.
9. Check Policy / Capability Registry.
10. Check Security Sandbox for restore targets.
11. Determine whether restore is destructive.
12. Generate restore dry-run report.
13. Require governance and human approval for destructive restore.
14. Acquire restore_execute lock.
15. Create pre-restore backup of current state.
16. Stage restore candidates under backup staging root.
17. Execute only approved restore actions.
18. Verify restored files.
19. Write restore evidence.
20. Record final restore status.
21. Release restore_execute lock.
```

No skipped stage is allowed unless the restore scope explicitly marks it not applicable and the decision evidence records why.

---

# 31. Disaster Recovery Test Requirements

Disaster recovery must be testable without damaging active source state.

Required DR tests:

```text
create backup snapshot
verify snapshot integrity
reject hash-mismatched snapshot
reject incompatible snapshot
generate restore dry-run
block destructive restore without approval
block restore from unverified snapshot
retain minimum valid snapshots
block deletion of only valid snapshot
generate disaster recovery plan
validate DR plan schema
prove restore execution cannot run without dry-run
prove retention apply cannot run without dry-run
prove lock conflict returns BLOCKED
```

DR tests must not require:

```text
network
GPU
hosted model
LLM
cloud provider
manual interaction
external MCP runtime
```

---

# 32. Runtime Artifact Rules

All backup runtime artifacts must stay under:

```text
.agentx-init/backups/
```

Approved backup runtime paths:

```text
.agentx-init/backups/snapshots/
.agentx-init/backups/manifests/
.agentx-init/backups/integrity/
.agentx-init/backups/restore_plans/
.agentx-init/backups/audit/
.agentx-init/backups/reports/
.agentx-init/backups/locks/
.agentx-init/backups/staging/
```

Rules:

```text
no backup artifact writes outside approved root without deviation
no source file writes during backup creation
no restore writes without approved restore decision
no cleanup deletes outside backup root
atomic writes for latest JSON artifacts
append-only JSONL for histories
```

---

# 33. Security Rules

This layer must enforce:

```text
no secret backup by default
no restore from unverified snapshot
no restore from incompatible snapshot
no destructive restore by default
no source overwrite without governance and approval
no Git write operations
no network/cloud storage by default
no raw shell execution
no path traversal
no symlink escape
no deletion of only valid backup
no silent backup failure
no silent restore failure
no evidence-free cleanup
```

---

# 34. Schema Example Requirements

For each required schema, tests must include:

```text
one valid example that passes
one missing-required-field example that fails
one invalid-enum example that fails
one unsafe/default-denied example where applicable
```

Required examples:

```text
valid_backup_policy
valid_snapshot_manifest
valid_restore_request_dry_run
valid_restore_decision_blocked
valid_restore_dry_run_report
valid_disaster_recovery_plan
valid_backup_audit_event
valid_backup_integrity_report
valid_backup_compatibility_report
valid_snapshot_catalog
valid_restore_execution_report
valid_backup_retention_report
valid_disaster_recovery_test_result
valid_backup_evidence_manifest
valid_backup_completion_record
```

---

# 35. Test Acceptance Criteria

Required tests:

```text
test_backup_policy_schema_accepts_valid_policy
test_backup_policy_schema_rejects_secret_include_by_default
test_snapshot_manifest_schema_accepts_valid_manifest
test_snapshot_manifest_requires_file_hashes
test_snapshot_manifest_requires_detached_manifest_hash
test_create_backup_snapshot_writes_manifest
test_create_backup_snapshot_excludes_secrets
test_verify_snapshot_integrity_passes_valid_snapshot
test_verify_snapshot_integrity_rejects_hash_mismatch
test_restore_request_schema_accepts_dry_run
test_restore_decision_blocks_unverified_snapshot
test_snapshot_catalog_preserves_failed_retired_and_quarantined_entries
test_compatibility_report_blocks_forward_restore_by_default
test_restore_decision_blocks_incompatible_snapshot
test_restore_decision_blocks_destructive_restore_without_approval
test_restore_dry_run_does_not_write_source
test_restore_execute_requires_dry_run
test_restore_execute_uses_staging_before_overwrite
test_restore_execution_report_references_dry_run_and_pre_restore_backup
test_disaster_recovery_test_result_schema_accepts_valid_result
test_retention_keeps_minimum_valid_snapshots
test_retention_blocks_delete_only_valid_snapshot
test_retention_apply_requires_dry_run
test_backup_audit_history_written
test_latest_backup_artifacts_written_atomically
test_backup_evidence_manifest_hashes_written
test_disaster_recovery_plan_schema_accepts_valid_plan
test_disaster_recovery_plan_requires_validation_commands
test_backup_lock_conflict_blocks_mutating_operation
test_idempotent_restore_execution_does_not_apply_twice
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
backup creation tests PASS
integrity verification tests PASS
restore dry-run tests PASS
destructive restore blocking tests PASS
retention safety tests PASS
concurrency/locking tests PASS
idempotency tests PASS
evidence/audit tests PASS
no source mutation from backup tests
```

---

# 36. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] backup policy schema is defined
[ ] snapshot manifest schema is defined
[ ] restore request schema is defined
[ ] restore decision schema is defined
[ ] restore dry-run report schema is defined
[ ] restore execution report schema is defined
[ ] snapshot catalog schema is defined
[ ] compatibility report schema is defined
[ ] disaster recovery plan schema is defined
[ ] disaster recovery test result schema is defined
[ ] evidence manifest schema is defined
[ ] audit/evidence paths are defined
[ ] backup storage root is defined
[ ] excluded paths are defined
[ ] secret exclusion rule is defined
[ ] hash algorithm is defined
[ ] detached manifest hash rule is defined
[ ] restore dry-run rule is defined
[ ] destructive restore block rule is defined
[ ] retention safety rules are defined
[ ] locking rules are defined
[ ] idempotency rules are defined
[ ] Security Sandbox integration is defined
[ ] Policy / Capability Registry integration is defined
[ ] Failure Taxonomy integration is defined
```

---

# 37. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] backup policy validates
[ ] snapshot manifest validates
[ ] restore request validates
[ ] restore decision validates
[ ] restore dry-run report validates
[ ] restore execution report validates
[ ] snapshot catalog validates
[ ] compatibility report validates
[ ] disaster recovery plan validates
[ ] disaster recovery test result validates
[ ] backup snapshot can be created
[ ] snapshot integrity can be verified
[ ] hash mismatch is rejected
[ ] incompatible snapshot is rejected
[ ] restore dry-run works
[ ] restore execution requires dry-run
[ ] destructive restore is blocked by default
[ ] retention cleanup preserves minimum valid snapshots
[ ] retention cleanup preserves only valid snapshot
[ ] locks block conflicting operations
[ ] idempotency prevents double restore/delete
[ ] audit/evidence records are written
[ ] no source mutation occurs during backup tests
[ ] completion record exists
```

---

# 38. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_BACKUP_DISASTER_RECOVERY"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  backup_snapshots_verified: []
  restore_dry_runs_verified: []
  destructive_restore_blocks_verified: []
  retention_safety_verified: []
  lock_safety_verified: []
  idempotency_verified: []
  policy_integration_verified: []
  sandbox_integration_verified: []
  failure_taxonomy_integration_verified: []
  git_integration_verified: []
  disaster_recovery_plans_verified: []
  evidence_hashes: []
  deviations_from_contract: []
  unresolved_risks: []
```

Required completion artifact:

```text
.agentx-init/backups/backup_disaster_recovery_completion_record.json
```

---

# 39. Deviation Register

Any exception, deferral, external storage path, compatibility override, restore override, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <BDR-DEV-001>
    area: <Backup | Restore | Retention | Evidence | Compatibility | External Storage | Other>
    description: <what differs from the contract>
    reason: <why accepted>
    safety_impact: <none | low | medium | high | critical>
    compensating_control: <test/evidence/control>
    accepted_status: NOT APPLICABLE | DEFERRED SAFELY | NON-BLOCKING FOLLOW-UP
    reviewer_decision: ACCEPTED | REJECTED
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
Secret backup by default cannot be accepted as a deviation.
Unverified restore cannot be accepted as a deviation.
Destructive restore without governance and human approval cannot be accepted as a deviation.
Missing evidence hashes cannot be accepted as a deviation for DONE.
External backup storage requires explicit policy and deviation record.
```

---

# 40. Residual Risks

```yaml
residual_risks:
  - id: "BDR-RISK-001"
    description: "A backup could preserve corrupted state and be mistaken for valid recovery state."
    severity: "critical"
    mitigation: "Snapshots require manifest, detached manifest hash, file hashes, and SHA-256 verification before restore_ready is true."
  - id: "BDR-RISK-002"
    description: "Restore could overwrite valid work."
    severity: "critical"
    mitigation: "Restore defaults to dry-run; destructive restore requires policy, sandbox, governance, human approval, staging, and pre-restore backup."
  - id: "BDR-RISK-003"
    description: "Secrets could be included in backup artifacts."
    severity: "high"
    mitigation: "Secrets are excluded by default; secret-like paths and payloads are blocked or redacted."
  - id: "BDR-RISK-004"
    description: "Retention cleanup could delete the only valid recovery point."
    severity: "critical"
    mitigation: "Cleanup must preserve minimum verified snapshots and block deletion of only valid snapshot."
  - id: "BDR-RISK-005"
    description: "Backup artifacts could be written outside approved runtime roots."
    severity: "high"
    mitigation: "Security Sandbox checks backup paths and blocks traversal or external writes by default."
  - id: "BDR-RISK-006"
    description: "Concurrent backup, restore, and cleanup operations could corrupt recovery evidence."
    severity: "high"
    mitigation: "Lock files and idempotency keys are required for mutating backup, restore, and cleanup operations."
```

---

# 41. Definition of Done

This layer is done when it can preserve and recover Agent_X state safely without bypassing policy, sandbox, governance, Git, or promotion controls.

It must prove:

```text
backup policy validates
snapshot manifests validate
restore requests validate
restore decisions validate
restore dry-run reports validate
restore execution reports validate
snapshot catalog validates
compatibility reports validate
disaster recovery plans validate
disaster recovery test results validate
backup snapshots are created only under approved backup root
forbidden paths and secrets are excluded
file hashes are recorded
snapshot manifests are hashed with detached hash records
snapshot catalog preserves failed, retired, deleted, and quarantined records
compatibility reports block unsafe forward/incompatible restore
integrity verification passes for valid snapshots
integrity verification fails for corrupted snapshots
incompatible snapshots cannot be restored
unverified snapshots cannot be restored
restore defaults to dry-run
restore execution requires dry-run
destructive restore is blocked by default
source overwrite requires governance and human approval
restore stages candidates before overwrite
retention cleanup preserves minimum valid snapshots
retention cleanup blocks deletion of only valid snapshot
lock conflicts fail closed
idempotency prevents double restore/delete
backup audit evidence is written
restore decision evidence is written
disaster recovery test evidence is written
evidence hashes are written
no Git write occurs
no network backup occurs by default
no raw shell is executed
no source mutation occurs during backup creation
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_backup_disaster_recovery_schemas.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 42. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
backup policy schema is missing
snapshot manifest schema is missing
restore request schema is missing
restore decision schema is missing
restore dry-run report schema is missing
restore execution report schema is missing
snapshot catalog schema is missing
compatibility report schema is missing
disaster recovery plan schema is missing
disaster recovery test result schema is missing
backup writes outside approved runtime root
backup includes secrets by default
snapshot lacks file hashes
snapshot lacks detached manifest hash
hash mismatch is ignored
quarantined snapshot can be restored
incompatible snapshot can be restored
unverified snapshot can be restored
restore executes without dry-run
restore writes source without governance
restore writes source without human approval
destructive restore is allowed by default
retention cleanup deletes only valid snapshot
cleanup deletes outside backup root
lock conflict is ignored
restore/delete can apply twice with same idempotency key
Git write operation occurs
network/cloud backup is enabled by default
raw shell executes
backup/restore lacks audit evidence
evidence hashes are missing
```

---

# 43. Final Freeze Rule

This v3 document is frozen as the controlling contract for the Backup / Disaster Recovery Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed restore safety policy, changed backup storage policy, changed retention safety behavior, external/cloud storage default enablement, new required backup category
```

Blocked without major revision:

```text
allowing destructive restore by default
removing dry-run requirement
removing policy check
removing sandbox check for path/file/restore/cleanup actions
allowing secret backup by default
allowing raw shell execution
allowing network/cloud backup by default
allowing Git write by default
removing evidence logging
removing evidence hashes
removing retention protection for only valid snapshot
```

The next document should be:

```text
BACKUP_DISASTER_RECOVERY_IMPLEMENTATION_SPEC
```

---

# 44. Final Rating

This v3 contract is rated:

```text
10/10
```

Reason:

```text
It preserves the full v2 coverage and closes the remaining contract-level gaps: role permission matrix, snapshot catalog/index, explicit compatibility report, restore execution report, disaster recovery test result schema, atomic snapshot staging and promotion, pre-restore backup evidence, secret content scanning, quarantine semantics, post-restore validation limits, stricter tests, Definition of Done, No-Go conditions, and a final freeze rule.
```
