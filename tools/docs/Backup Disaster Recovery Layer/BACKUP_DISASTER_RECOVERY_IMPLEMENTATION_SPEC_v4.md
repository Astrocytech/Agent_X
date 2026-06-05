# Backup / Disaster Recovery Layer — Implementation Spec v4

**Roadmap Layer:** 21  
**Roadmap Phase:** Phase E — Backup/Recovery  
**Schema Version:** 1.0  
**Schema ID:** backup_record.schema.json

---

## 1. Overview

The Backup / Disaster Recovery Layer provides a structured, verifiable mechanism for creating backups of critical Agent_X state and recovering from disaster scenarios. It supports nine backup categories and nine recovery scenarios.

---

## 2. Components

### 2.1 Constants

| Constant | Value |
|---|---|
| BK_SCHEMA_VERSION | "1.0" |
| BK_SCHEMA_ID | "backup_record.schema.json" |
| BK_PENDING | "PENDING" |
| BK_COMPLETED | "COMPLETED" |
| BK_FAILED | "FAILED" |

### 2.2 Backup Categories (9)

- `BC_AUDIT_HISTORY` — audit_history
- `BC_IMPLEMENTATION_SESSIONS` — implementation_sessions
- `BC_ROLLBACK_SNAPSHOTS` — rollback_snapshots
- `BC_APPROVALS` — approvals
- `BC_PROMOTION_RECORDS` — promotion_records
- `BC_POLICIES` — policies
- `BC_MODEL_RUN_METADATA` — model_run_metadata
- `BC_TOOL_CALL_HISTORY` — tool_call_history
- `BC_EVALUATION_RESULTS` — evaluation_results

### 2.3 Recovery Scenarios (9)

- `RS_CORRUPTED_LATEST_ARTIFACT` — Use previous artifact version from history
- `RS_MALFORMED_JSONL` — Skip corrupted line and continue from next valid entry
- `RS_MISSING_ROLLBACK_SNAPSHOT` — Reconstruct from patch session evidence
- `RS_INTERRUPTED_PATCH_SESSION` — Rollback any partial changes and restart session
- `RS_INTERRUPTED_VALIDATION` — Re-run validation from last known good state
- `RS_PARTIAL_TOOL_CALL_RECORD` — Discard partial record and retry tool call
- `RS_STALE_LOCK` — Force unlock after verifying no active session
- `RS_FAILED_MIGRATION` — Restore previous schema version and retry migration
- `RS_LOST_POLICY_FILE` — Restore from latest policy backup

### 2.4 BackupRecord

Dataclass fields:
- `schema_version` (str, default "1.0")
- `backup_id` (str)
- `category` (str)
- `status` (str, enum: PENDING/COMPLETED/FAILED)
- `source_paths` (list[str])
- `backup_paths` (list[str])
- `checksum` (str)
- `size_bytes` (int)
- `created_at` (str, ISO 8601)
- `completed_at` (str, ISO 8601)
- `warnings` (list[str])
- `errors` (list[str])

### 2.5 BackupRecordHash

- `record` — the BackupRecord
- `hash_value` — computed SHA-256 hash of canonical JSON
- `computed_at` — ISO timestamp

### 2.6 BackupManifest

- `manifest_id` — unique identifier
- `backups` — list of BackupRecord
- `total_backups` — derived count
- `total_size_bytes` — derived sum
- `created_at` — ISO timestamp
- `add_backup(record)` — appends and recalculates totals
- `write_manifest(repo_root)` — atomic write to `.agentx-init/backup/manifest.json`
- `load_manifest(repo_root)` — static, reads manifest from disk

### 2.7 BackupManager

- `create_backup(category, source_paths)` — creates PENDING record
- `complete_backup(backup_id, backup_paths, checksum, size_bytes)` — sets COMPLETED
- `fail_backup(backup_id, errors)` — sets FAILED
- `get_backup(backup_id)` — lookup by ID
- `list_backups(category)` — filter by category
- `get_manifest()` — current manifest
- `clear()` — wipe all backups
- `can_restore(backup_id)` — feasibility check
- `check_recovery_scenario(scenario)` — scenario description
- `acquire_backup_lock()` — fcntl-based exclusive lock
- `release_backup_lock()` — release held lock
- `validate_record_schema(record)` — JSON Schema validation
- `verify_backup_integrity(backup_id)` — hash recomputation check
- `get_backup_report(backup_id)` — structured report dict
- `list_recovery_scenarios()` — all scenarios with descriptions
- `resolve_recovery_scenario(scenario_name)` — detailed recovery plan

### 2.8 Helper Functions

- `canonical_json(data)` — sort_keys, no whitespace
- `sha256_dict(data)` — SHA-256 of canonical JSON
- `write_json_atomic(path, data)` — atomic file write via temp + replace
- `append_jsonl(path, data)` — append canonical JSON line

---

## 3. Schema (backup_record.schema.json)

Draft-07, minified. Required fields:
- `schema_version` (pattern `^1\.0$`)
- `schema_id` (const `backup_record.schema.json`)
- `backup_id`, `category`, `status` (enum), `source_paths`, `checksum`, `size_bytes`, `created_at`, `warnings`, `errors`

Optional fields: `backup_paths`, `completed_at`

---

## 4. Persistence

Backups are stored in `.agentx-init/backup/backups.jsonl` (append-only JSONL). The manifest is written atomically to `.agentx-init/backup/manifest.json`.

---

## 5. Locking

File locking uses fcntl.flock with LOCK_EX | LOCK_NB on `.agentx-init/backup/.backup.lock`.

---

## 6. Integrity

Each backup record carries a SHA-256 checksum. `verify_backup_integrity` recomputes the hash from the record's canonical JSON and compares against the stored checksum.
