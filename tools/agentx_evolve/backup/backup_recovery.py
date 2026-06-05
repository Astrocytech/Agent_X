from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict

BK_SCHEMA_VERSION = "1.0"
BK_PENDING = "PENDING"
BK_COMPLETED = "COMPLETED"
BK_FAILED = "FAILED"
ALL_BACKUP_STATUSES = [BK_PENDING, BK_COMPLETED, BK_FAILED]

BC_AUDIT_HISTORY = "audit_history"
BC_IMPLEMENTATION_SESSIONS = "implementation_sessions"
BC_ROLLBACK_SNAPSHOTS = "rollback_snapshots"
BC_APPROVALS = "approvals"
BC_PROMOTION_RECORDS = "promotion_records"
BC_POLICIES = "policies"
BC_MODEL_RUN_METADATA = "model_run_metadata"
BC_TOOL_CALL_HISTORY = "tool_call_history"
BC_EVALUATION_RESULTS = "evaluation_results"
ALL_BACKUP_CATEGORIES = [
    BC_AUDIT_HISTORY, BC_IMPLEMENTATION_SESSIONS, BC_ROLLBACK_SNAPSHOTS,
    BC_APPROVALS, BC_PROMOTION_RECORDS, BC_POLICIES,
    BC_MODEL_RUN_METADATA, BC_TOOL_CALL_HISTORY, BC_EVALUATION_RESULTS,
]

RS_CORRUPTED_LATEST_ARTIFACT = "corrupted_latest_artifact"
RS_MALFORMED_JSONL = "malformed_jsonl_line"
RS_MISSING_ROLLBACK_SNAPSHOT = "missing_rollback_snapshot"
RS_INTERRUPTED_PATCH_SESSION = "interrupted_patch_session"
RS_INTERRUPTED_VALIDATION = "interrupted_validation"
RS_PARTIAL_TOOL_CALL_RECORD = "partial_tool_call_record"
RS_STALE_LOCK = "stale_lock"
RS_FAILED_MIGRATION = "failed_migration"
RS_LOST_POLICY_FILE = "lost_policy_file"
ALL_RECOVERY_SCENARIOS = [
    RS_CORRUPTED_LATEST_ARTIFACT, RS_MALFORMED_JSONL, RS_MISSING_ROLLBACK_SNAPSHOT,
    RS_INTERRUPTED_PATCH_SESSION, RS_INTERRUPTED_VALIDATION, RS_PARTIAL_TOOL_CALL_RECORD,
    RS_STALE_LOCK, RS_FAILED_MIGRATION, RS_LOST_POLICY_FILE,
]


@dataclass
class BackupRecord:
    schema_version: str = BK_SCHEMA_VERSION
    backup_id: str = ""
    category: str = ""
    status: str = BK_PENDING
    source_paths: list[str] = field(default_factory=list)
    backup_paths: list[str] = field(default_factory=list)
    checksum: str = ""
    size_bytes: int = 0
    created_at: str = ""
    completed_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class BackupManifest:
    schema_version: str = BK_SCHEMA_VERSION
    manifest_id: str = ""
    backups: list[BackupRecord] = field(default_factory=list)
    total_backups: int = 0
    total_size_bytes: int = 0
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def add_backup(self, record: BackupRecord) -> None:
        self.backups.append(record)
        self.total_backups = len(self.backups)
        self.total_size_bytes = sum(b.size_bytes for b in self.backups)


class BackupManager:
    def __init__(self):
        self._backups: dict[str, BackupRecord] = {}
        self._manifest: BackupManifest = BackupManifest(
            manifest_id=new_id("bkm"),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def create_backup(self, category: str,
                       source_paths: list[str] | None = None) -> BackupRecord:
        if source_paths is None:
            source_paths = []
        record = BackupRecord(
            backup_id=new_id("bk"),
            category=category,
            status=BK_PENDING,
            source_paths=source_paths,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._backups[record.backup_id] = record
        self._manifest.add_backup(record)
        return record

    def complete_backup(self, backup_id: str, backup_paths: list[str] | None = None,
                         checksum: str = "", size_bytes: int = 0) -> bool:
        record = self._backups.get(backup_id)
        if not record:
            return False
        record.status = BK_COMPLETED
        record.completed_at = datetime.now(timezone.utc).isoformat()
        if backup_paths:
            record.backup_paths = backup_paths
        if checksum:
            record.checksum = checksum
        if size_bytes:
            record.size_bytes = size_bytes
        return True

    def fail_backup(self, backup_id: str, errors: list[str] | None = None) -> bool:
        record = self._backups.get(backup_id)
        if not record:
            return False
        record.status = BK_FAILED
        record.completed_at = datetime.now(timezone.utc).isoformat()
        if errors:
            record.errors = errors
        return True

    def get_backup(self, backup_id: str) -> BackupRecord | None:
        return self._backups.get(backup_id)

    def list_backups(self, category: str | None = None) -> list[BackupRecord]:
        if category:
            return [b for b in self._backups.values() if b.category == category]
        return list(self._backups.values())

    def get_manifest(self) -> BackupManifest:
        return self._manifest

    def clear(self) -> None:
        self._backups.clear()
        self._manifest = BackupManifest(
            manifest_id=new_id("bkm"),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def can_restore(self, backup_id: str) -> tuple[bool, str]:
        record = self._backups.get(backup_id)
        if not record:
            return False, "Backup not found"
        if record.status != BK_COMPLETED:
            return False, f"Backup status is {record.status}, not COMPLETED"
        if not record.backup_paths:
            return False, "No backup paths available for restore"
        return True, "Ready to restore"

    def check_recovery_scenario(self, scenario: str) -> str:
        if scenario not in ALL_RECOVERY_SCENARIOS:
            return "UNKNOWN_SCENARIO"
        known_recoveries = {
            RS_CORRUPTED_LATEST_ARTIFACT: "Use previous artifact version from history",
            RS_MALFORMED_JSONL: "Skip corrupted line and continue from next valid entry",
            RS_MISSING_ROLLBACK_SNAPSHOT: "Reconstruct from patch session evidence",
            RS_INTERRUPTED_PATCH_SESSION: "Rollback any partial changes and restart session",
            RS_INTERRUPTED_VALIDATION: "Re-run validation from last known good state",
            RS_PARTIAL_TOOL_CALL_RECORD: "Discard partial record and retry tool call",
            RS_STALE_LOCK: "Force unlock after verifying no active session",
            RS_FAILED_MIGRATION: "Restore previous schema version and retry migration",
            RS_LOST_POLICY_FILE: "Restore from latest policy backup",
        }
        return known_recoveries.get(scenario, "No recovery strategy defined")
