from __future__ import annotations
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from agentx_evolve.models.model_models import new_id, to_dict

BK_SCHEMA_VERSION = "1.0"
BK_SCHEMA_ID = "backup_record.schema.json"
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

RECOVERY_SCENARIO_DESCRIPTIONS: dict[str, str] = {
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

RECOVERY_SCENARIO_PLANS: dict[str, dict[str, Any]] = {
    RS_CORRUPTED_LATEST_ARTIFACT: {
        "scenario": RS_CORRUPTED_LATEST_ARTIFACT,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_CORRUPTED_LATEST_ARTIFACT],
        "severity": "HIGH",
        "steps": [
            "Identify the corrupted artifact",
            "Locate the previous valid version from backup history",
            "Replace corrupted artifact with the previous version",
            "Verify integrity of restored artifact",
        ],
    },
    RS_MALFORMED_JSONL: {
        "scenario": RS_MALFORMED_JSONL,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_MALFORMED_JSONL],
        "severity": "MEDIUM",
        "steps": [
            "Identify the corrupted line in the JSONL file",
            "Parse all lines before the corrupted one",
            "Skip the corrupted line and continue from the next valid entry",
            "Log the skipped entry for audit",
        ],
    },
    RS_MISSING_ROLLBACK_SNAPSHOT: {
        "scenario": RS_MISSING_ROLLBACK_SNAPSHOT,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_MISSING_ROLLBACK_SNAPSHOT],
        "severity": "HIGH",
        "steps": [
            "Identify the missing rollback snapshot ID",
            "Search patch session evidence for the snapshot",
            "Reconstruct the rollback point from available evidence",
            "Create a new snapshot from reconstructed state",
        ],
    },
    RS_INTERRUPTED_PATCH_SESSION: {
        "scenario": RS_INTERRUPTED_PATCH_SESSION,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_INTERRUPTED_PATCH_SESSION],
        "severity": "HIGH",
        "steps": [
            "Identify the interrupted patch session",
            "Rollback any partial changes applied",
            "Verify the system is in a clean state",
            "Restart the patch session from the last known good state",
        ],
    },
    RS_INTERRUPTED_VALIDATION: {
        "scenario": RS_INTERRUPTED_VALIDATION,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_INTERRUPTED_VALIDATION],
        "severity": "MEDIUM",
        "steps": [
            "Identify the interrupted validation step",
            "Determine the last known good state",
            "Re-run validation from that state",
            "Compare results with expected outcomes",
        ],
    },
    RS_PARTIAL_TOOL_CALL_RECORD: {
        "scenario": RS_PARTIAL_TOOL_CALL_RECORD,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_PARTIAL_TOOL_CALL_RECORD],
        "severity": "LOW",
        "steps": [
            "Identify the partial tool call record",
            "Discard the incomplete record",
            "Retry the tool call with original parameters",
            "Log the retry attempt",
        ],
    },
    RS_STALE_LOCK: {
        "scenario": RS_STALE_LOCK,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_STALE_LOCK],
        "severity": "MEDIUM",
        "steps": [
            "Detect the stale lock file",
            "Verify no active session holds the lock",
            "Force remove the lock file",
            "Notify that the lock was cleared",
        ],
    },
    RS_FAILED_MIGRATION: {
        "scenario": RS_FAILED_MIGRATION,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_FAILED_MIGRATION],
        "severity": "HIGH",
        "steps": [
            "Identify the failed migration attempt",
            "Restore the previous schema version from backup",
            "Analyze the migration failure cause",
            "Retry migration with corrected logic",
        ],
    },
    RS_LOST_POLICY_FILE: {
        "scenario": RS_LOST_POLICY_FILE,
        "description": RECOVERY_SCENARIO_DESCRIPTIONS[RS_LOST_POLICY_FILE],
        "severity": "HIGH",
        "steps": [
            "Identify the missing policy file",
            "Locate the latest policy backup",
            "Restore the policy file from backup",
            "Verify policy integrity and reload",
        ],
    },
}

BACKUP_LOCK_FILE = ".backup.lock"


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp." + os.urandom(4).hex())
    try:
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")


@dataclass
class BackupRecord:
    schema_version: str = BK_SCHEMA_VERSION
    schema_id: str = BK_SCHEMA_ID
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
class BackupRecordHash:
    record: BackupRecord
    hash_value: str
    computed_at: str

    def to_dict(self) -> dict:
        return {
            "backup_id": self.record.backup_id,
            "hash_value": self.hash_value,
            "computed_at": self.computed_at,
        }


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

    def write_manifest(self, repo_root: str | Path) -> Path:
        repo_root = Path(repo_root)
        manifest_dir = repo_root / ".agentx-init" / "backup"
        manifest_path = manifest_dir / "manifest.json"
        write_json_atomic(manifest_path, self.to_dict())
        return manifest_path

    @staticmethod
    def load_manifest(repo_root: str | Path) -> BackupManifest:
        repo_root = Path(repo_root)
        manifest_path = repo_root / ".agentx-init" / "backup" / "manifest.json"
        if not manifest_path.exists():
            return BackupManifest(
                manifest_id=new_id("bkm"),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        with open(manifest_path) as f:
            data = json.load(f)
        backups = [BackupRecord(**b) for b in data.pop("backups", [])]
        manifest = BackupManifest(**data)
        manifest.backups = backups
        manifest.total_backups = len(backups)
        manifest.total_size_bytes = sum(b.size_bytes for b in backups)
        return manifest


class BackupManager:
    def __init__(self, backup_dir: str | Path | None = None):
        self._backups: dict[str, BackupRecord] = {}
        self._backup_dir = Path(backup_dir) if backup_dir else None
        self._manifest: BackupManifest = BackupManifest(
            manifest_id=new_id("bkm"),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._lock_fd: int | None = None
        self._load_from_disk()

    def _persist_path(self) -> Path | None:
        if self._backup_dir is None:
            return None
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        return self._backup_dir / "backups.jsonl"

    def _lock_path(self) -> Path | None:
        if self._backup_dir is None:
            return None
        return self._backup_dir / BACKUP_LOCK_FILE

    def _load_from_disk(self) -> None:
        p = self._persist_path()
        if p is None or not p.exists():
            return
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                r = BackupRecord(**data)
                self._backups[r.backup_id] = r
            except Exception:
                continue
        for r in self._backups.values():
            self._manifest.add_backup(r)

    def _append_to_disk(self, record: BackupRecord) -> None:
        p = self._persist_path()
        if p is None:
            return
        with open(p, "a") as f:
            f.write(json.dumps(record.to_dict(), default=str) + "\n")

    def acquire_backup_lock(self) -> bool:
        lock_path = self._lock_path()
        if lock_path is None:
            return False
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)
            try:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except ImportError:
                pass
            self._lock_fd = fd
            return True
        except (IOError, OSError):
            return False

    def release_backup_lock(self) -> bool:
        if self._lock_fd is None:
            return False
        try:
            import fcntl
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
        except ImportError:
            pass
        os.close(self._lock_fd)
        self._lock_fd = None
        return True

    @staticmethod
    def _load_schema() -> dict:
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / BK_SCHEMA_ID
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        with open(schema_path) as f:
            return json.load(f)

    def validate_record_schema(self, record: BackupRecord) -> list[str]:
        import jsonschema
        errors: list[str] = []
        try:
            schema = self._load_schema()
            jsonschema.validate(record.to_dict(), schema)
        except FileNotFoundError as e:
            errors.append(str(e))
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
        except json.JSONDecodeError as e:
            errors.append(f"Schema file is invalid JSON: {e}")
        return errors

    def verify_backup_integrity(self, backup_id: str) -> bool:
        record = self._backups.get(backup_id)
        if not record:
            return False
        if not record.checksum:
            return False
        d = record.to_dict()
        d.pop("checksum", None)
        computed = sha256_dict(d)
        return computed == record.checksum

    def get_backup_report(self, backup_id: str) -> dict[str, Any] | None:
        record = self._backups.get(backup_id)
        if not record:
            return None
        d = record.to_dict()
        d.pop("checksum", None)
        record_hash = sha256_dict(d)
        can_restore, restore_msg = self.can_restore(backup_id)
        return {
            "backup_id": record.backup_id,
            "category": record.category,
            "status": record.status,
            "source_paths": list(record.source_paths),
            "backup_paths": list(record.backup_paths),
            "checksum": record.checksum,
            "size_bytes": record.size_bytes,
            "created_at": record.created_at,
            "completed_at": record.completed_at,
            "warnings": list(record.warnings),
            "errors": list(record.errors),
            "hash": {
                "computed_hash": record_hash,
                "stored_hash": record.checksum,
                "integrity_verified": record_hash == record.checksum if record.checksum else False,
            },
            "restore": {
                "can_restore": can_restore,
                "message": restore_msg,
            },
        }

    def list_recovery_scenarios(self) -> dict[str, str]:
        return dict(RECOVERY_SCENARIO_DESCRIPTIONS)

    def resolve_recovery_scenario(self, scenario_name: str) -> dict[str, Any]:
        plan = RECOVERY_SCENARIO_PLANS.get(scenario_name)
        if plan is None:
            return {
                "scenario": scenario_name,
                "description": "Unknown scenario",
                "severity": "UNKNOWN",
                "steps": [],
            }
        return dict(plan)

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
        self._append_to_disk(record)
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
        if size_bytes:
            record.size_bytes = size_bytes
        elif backup_paths:
            record.size_bytes = sum(Path(p).stat().st_size for p in backup_paths if Path(p).exists())
        if checksum:
            record.checksum = checksum
        else:
            d = record.to_dict()
            d.pop("checksum", None)
            record.checksum = sha256_dict(d)
        self._append_to_disk(record)
        return True

    def fail_backup(self, backup_id: str, errors: list[str] | None = None) -> bool:
        record = self._backups.get(backup_id)
        if not record:
            return False
        record.status = BK_FAILED
        record.completed_at = datetime.now(timezone.utc).isoformat()
        if errors:
            record.errors = errors
        self._append_to_disk(record)
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
        p = self._persist_path()
        if p and p.exists():
            p.unlink()

    def can_restore(self, backup_id: str) -> tuple[bool, str]:
        record = self._backups.get(backup_id)
        if not record:
            return False, "Backup not found"
        if record.status != BK_COMPLETED:
            return False, f"Backup status is {record.status}, not COMPLETED"
        if not record.backup_paths:
            return False, "No backup paths available for restore"
        if self._backup_dir is not None:
            for p in record.backup_paths:
                if not Path(p).exists():
                    return False, f"Backup path does not exist on disk: {p}"
        return True, "Ready to restore"

    def check_recovery_scenario(self, scenario: str) -> str:
        if scenario not in ALL_RECOVERY_SCENARIOS:
            return "UNKNOWN_SCENARIO"
        return RECOVERY_SCENARIO_DESCRIPTIONS.get(scenario, "No recovery strategy defined")
