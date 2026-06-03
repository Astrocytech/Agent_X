import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _load_schema(name: str) -> dict:
    path = SCHEMA_DIR / name
    with open(path) as f:
        return json.load(f)


class TestBackupAuditEventSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_audit_event.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_audit_event.schema.json",
            "audit_id": "audit_001",
            "timestamp": "2025-01-01T00:00:00.000000Z",
            "source_component": "BackupDisasterRecovery",
            "event_type": "backup_created",
            "status": "SUCCESS",
            "message": "Backup created",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_audit_event.schema.json")
        data = {"event_type": "test"}
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

    def test_bad_source_component_rejects(self):
        schema = _load_schema("backup_audit_event.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_audit_event.schema.json",
            "audit_id": "audit_001",
            "timestamp": "2025-01-01T00:00:00.000000Z",
            "source_component": "WrongComponent",
            "event_type": "backup_created",
            "status": "SUCCESS",
            "message": "Backup created",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupCatalogSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_catalog.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_catalog.schema.json",
            "catalog_id": "cat_001",
            "updated_at": "2025-01-01T00:00:00.000000Z",
            "project_id": "agentx",
            "repo_root_fingerprint": "abc123",
            "backup_format_version": "1.0",
            "snapshots": [],
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_catalog.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={"catalog_id": "cat_001"}, schema=schema)


class TestBackupCliResultSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_cli_result.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_cli_result.schema.json",
            "command_name": "build_backup_manifest",
            "command_id": "cmd_001",
            "started_at": "2025-01-01T00:00:00.000000Z",
            "completed_at": "2025-01-01T00:01:00.000000Z",
            "status": "SUCCESS",
            "exit_code": 0,
            "message": "Manifest built",
            "data": {},
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_bad_status_rejects(self):
        schema = _load_schema("backup_cli_result.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_cli_result.schema.json",
            "command_name": "build_backup_manifest",
            "command_id": "cmd_001",
            "started_at": "2025-01-01T00:00:00.000000Z",
            "completed_at": "2025-01-01T00:01:00.000000Z",
            "status": "UNKNOWN_STATUS",
            "exit_code": 0,
            "message": "Test",
            "data": {},
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupCompletionRecordSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_completion_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_completion_record.schema.json",
            "component_id": "AGENTX_BACKUP_DISASTER_RECOVERY",
            "validated_commit": "abc123",
            "validated_at": "2025-01-01T00:00:00.000000Z",
            "final_decision": "DONE",
            "commands_run": [],
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_completion_record.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)

    def test_bad_component_id_rejects(self):
        schema = _load_schema("backup_completion_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_completion_record.schema.json",
            "component_id": "WRONG_COMPONENT",
            "validated_commit": "abc123",
            "validated_at": "2025-01-01T00:00:00.000000Z",
            "final_decision": "DONE",
            "commands_run": [],
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupEvidenceManifestSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_evidence_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_evidence_manifest.schema.json",
            "evidence_manifest_id": "em_001",
            "component_id": "AGENTX_BACKUP_DISASTER_RECOVERY",
            "created_at": "2025-01-01T00:00:00.000000Z",
            "evidence_files": [],
            "evidence_file_hashes": {},
            "final_status": "PASS",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_evidence_manifest.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestBackupFileRecordSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_file_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_file_record.schema.json",
            "relative_path": "src/main.py",
            "original_path": "/repo/src/main.py",
            "backup_path": "/backup/src/main.py",
            "file_size_bytes": 1024,
            "included": True,
            "path_type": "file",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_file_record.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={"relative_path": "test"}, schema=schema)

    def test_bad_path_type_rejects(self):
        schema = _load_schema("backup_file_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_file_record.schema.json",
            "relative_path": "src/main.py",
            "original_path": "/repo/src/main.py",
            "backup_path": "/backup/src/main.py",
            "file_size_bytes": 1024,
            "included": True,
            "path_type": "block_device",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupLockRecordSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_lock_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_lock_record.schema.json",
            "lock_record_id": "lr_001",
            "lock_name": "backup_lock",
            "lock_id": "lock_001",
            "acquired_at": "2025-01-01T00:00:00.000000Z",
            "stale_after_seconds": 300,
            "owner_component": "BackupDisasterRecovery",
            "status": "ACQUIRED",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_bad_status_rejects(self):
        schema = _load_schema("backup_lock_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_lock_record.schema.json",
            "lock_record_id": "lr_001",
            "lock_name": "backup_lock",
            "lock_id": "lock_001",
            "acquired_at": "2025-01-01T00:00:00.000000Z",
            "stale_after_seconds": 300,
            "owner_component": "BackupDisasterRecovery",
            "status": "INVALID_STATUS",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupManifestSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_manifest.schema.json",
            "backup_id": "bck_001",
            "created_at": "2025-01-01T00:00:00.000000Z",
            "source_component": "BackupDisasterRecovery",
            "repo_root": "/repo",
            "snapshot_path": "/snapshots/bck_001",
            "file_records": [],
            "status": "CREATED",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_manifest.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)

    def test_bad_status_rejects(self):
        schema = _load_schema("backup_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_manifest.schema.json",
            "backup_id": "bck_001",
            "created_at": "2025-01-01T00:00:00.000000Z",
            "source_component": "BackupDisasterRecovery",
            "repo_root": "/repo",
            "snapshot_path": "/snapshots/bck_001",
            "file_records": [],
            "status": "INVALID_STATUS",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

    def test_bad_git_status_summary_rejects(self):
        schema = _load_schema("backup_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_manifest.schema.json",
            "backup_id": "bck_001",
            "created_at": "2025-01-01T00:00:00.000000Z",
            "source_component": "BackupDisasterRecovery",
            "repo_root": "/repo",
            "snapshot_path": "/snapshots/bck_001",
            "file_records": [],
            "status": "CREATED",
            "git_status_summary": "INVALID",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupPolicySchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_policy.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_policy.schema.json",
            "policy_id": "pol_001",
            "allowed_backup_roots": ["."],
            "allowed_restore_roots": [".agentx-init"],
            "excluded_paths": [".git"],
            "excluded_globs": ["*.tmp"],
            "excluded_secret_patterns": [".env"],
            "require_git_status": True,
            "require_hashes": True,
            "require_manifest_validation": True,
            "require_restore_dry_run": True,
            "allow_source_backup": True,
            "allow_source_restore": False,
            "allow_runtime_restore": False,
            "allow_release_restore": False,
            "allow_secret_backup_plaintext": False,
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_policy.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={"policy_id": "pol_001"}, schema=schema)


class TestBackupRecordSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_record.schema.json",
            "backup_id": "bck_001",
            "category": "IMPLEMENTATION_SESSIONS",
            "status": "COMPLETED",
            "source_paths": [],
            "checksum": "abc123",
            "size_bytes": 1024,
            "created_at": "2025-01-01T00:00:00",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_record.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)

    def test_bad_status_rejects(self):
        schema = _load_schema("backup_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_record.schema.json",
            "backup_id": "bck_001",
            "category": "IMPLEMENTATION_SESSIONS",
            "status": "INVALID",
            "source_paths": [],
            "checksum": "abc123",
            "size_bytes": 1024,
            "created_at": "2025-01-01T00:00:00",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupRetentionPolicySchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_retention_policy.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_retention_policy.schema.json",
            "retention_policy_id": "rp_001",
            "keep_latest_verified_count": 5,
            "keep_minimum_total_count": 3,
            "protect_release_linked": True,
            "protect_manually_marked": True,
            "dry_run": False,
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_retention_policy.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={"retention_policy_id": "rp_001"}, schema=schema)

    def test_zero_count_rejects(self):
        schema = _load_schema("backup_retention_policy.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_retention_policy.schema.json",
            "retention_policy_id": "rp_001",
            "keep_latest_verified_count": 0,
            "keep_minimum_total_count": 0,
            "protect_release_linked": True,
            "protect_manually_marked": True,
            "dry_run": False,
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestBackupSnapshotIndexSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_snapshot_index.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_snapshot_index.schema.json",
            "snapshot_index_id": "si_001",
            "backup_id": "bck_001",
            "created_at": "2025-01-01T00:00:00.000000Z",
            "snapshot_path": "/snapshots/bck_001",
            "file_records": [],
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_snapshot_index.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestBackupSnapshotRecordSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_snapshot_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_snapshot_record.schema.json",
            "snapshot_id": "ss_001",
            "backup_id": "bck_001",
            "snapshot_path": "/snapshots/bck_001",
            "finalized": True,
            "file_count": 10,
            "total_size_bytes": 10240,
            "protected": False,
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_snapshot_record.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestBackupVerificationResultSchema:
    def test_valid_accepts(self):
        schema = _load_schema("backup_verification_result.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_verification_result.schema.json",
            "verification_id": "vr_001",
            "backup_id": "bck_001",
            "verified_at": "2025-01-01T00:00:00.000000Z",
            "manifest_path": "/manifests/bck_001.json",
            "snapshot_path": "/snapshots/bck_001",
            "status": "PASS",
            "files_checked": 10,
            "files_passed": 10,
            "files_failed": 0,
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("backup_verification_result.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)

    def test_bad_status_rejects(self):
        schema = _load_schema("backup_verification_result.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_verification_result.schema.json",
            "verification_id": "vr_001",
            "backup_id": "bck_001",
            "verified_at": "2025-01-01T00:00:00.000000Z",
            "manifest_path": "/manifests/bck_001.json",
            "snapshot_path": "/snapshots/bck_001",
            "status": "INVALID_STATUS",
            "files_checked": 10,
            "files_passed": 10,
            "files_failed": 0,
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)
