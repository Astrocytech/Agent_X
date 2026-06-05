import pytest
from agentx_evolve.backup.backup_recovery import (
    BackupRecord, BackupManifest, BackupManager,
    BK_SCHEMA_VERSION, BK_PENDING, BK_COMPLETED, BK_FAILED,
    ALL_BACKUP_STATUSES,
    BC_AUDIT_HISTORY, BC_IMPLEMENTATION_SESSIONS, BC_ROLLBACK_SNAPSHOTS,
    BC_APPROVALS, BC_PROMOTION_RECORDS, BC_POLICIES,
    BC_MODEL_RUN_METADATA, BC_TOOL_CALL_HISTORY, BC_EVALUATION_RESULTS,
    ALL_BACKUP_CATEGORIES,
    RS_CORRUPTED_LATEST_ARTIFACT, RS_MALFORMED_JSONL, RS_MISSING_ROLLBACK_SNAPSHOT,
    RS_INTERRUPTED_PATCH_SESSION, RS_INTERRUPTED_VALIDATION, RS_PARTIAL_TOOL_CALL_RECORD,
    RS_STALE_LOCK, RS_FAILED_MIGRATION, RS_LOST_POLICY_FILE,
    ALL_RECOVERY_SCENARIOS,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_bk_schema_version():
    assert BK_SCHEMA_VERSION == "1.0"

def test_all_backup_statuses():
    assert BK_PENDING in ALL_BACKUP_STATUSES
    assert BK_COMPLETED in ALL_BACKUP_STATUSES
    assert BK_FAILED in ALL_BACKUP_STATUSES
    assert len(ALL_BACKUP_STATUSES) == 3

def test_all_backup_categories():
    assert BC_AUDIT_HISTORY in ALL_BACKUP_CATEGORIES
    assert BC_IMPLEMENTATION_SESSIONS in ALL_BACKUP_CATEGORIES
    assert BC_ROLLBACK_SNAPSHOTS in ALL_BACKUP_CATEGORIES
    assert BC_APPROVALS in ALL_BACKUP_CATEGORIES
    assert BC_PROMOTION_RECORDS in ALL_BACKUP_CATEGORIES
    assert BC_POLICIES in ALL_BACKUP_CATEGORIES
    assert BC_MODEL_RUN_METADATA in ALL_BACKUP_CATEGORIES
    assert BC_TOOL_CALL_HISTORY in ALL_BACKUP_CATEGORIES
    assert BC_EVALUATION_RESULTS in ALL_BACKUP_CATEGORIES
    assert len(ALL_BACKUP_CATEGORIES) == 9

def test_all_recovery_scenarios():
    assert RS_CORRUPTED_LATEST_ARTIFACT in ALL_RECOVERY_SCENARIOS
    assert RS_MALFORMED_JSONL in ALL_RECOVERY_SCENARIOS
    assert RS_MISSING_ROLLBACK_SNAPSHOT in ALL_RECOVERY_SCENARIOS
    assert RS_INTERRUPTED_PATCH_SESSION in ALL_RECOVERY_SCENARIOS
    assert RS_INTERRUPTED_VALIDATION in ALL_RECOVERY_SCENARIOS
    assert RS_PARTIAL_TOOL_CALL_RECORD in ALL_RECOVERY_SCENARIOS
    assert RS_STALE_LOCK in ALL_RECOVERY_SCENARIOS
    assert RS_FAILED_MIGRATION in ALL_RECOVERY_SCENARIOS
    assert RS_LOST_POLICY_FILE in ALL_RECOVERY_SCENARIOS
    assert len(ALL_RECOVERY_SCENARIOS) == 9

# ---------------------------------------------------------------------------
# BackupRecord
# ---------------------------------------------------------------------------

def test_backup_record_defaults():
    r = BackupRecord()
    assert r.schema_version == "1.0"
    assert r.backup_id == ""
    assert r.category == ""
    assert r.status == BK_PENDING
    assert r.source_paths == []
    assert r.backup_paths == []
    assert r.checksum == ""
    assert r.size_bytes == 0

def test_backup_record_custom():
    r = BackupRecord(backup_id="bk_001", category=BC_AUDIT_HISTORY,
                     checksum="abc123", size_bytes=1024)
    assert r.backup_id == "bk_001"
    assert r.category == "audit_history"
    assert r.checksum == "abc123"
    assert r.size_bytes == 1024

def test_backup_record_to_dict():
    r = BackupRecord(backup_id="bk_001")
    d = r.to_dict()
    assert d["backup_id"] == "bk_001"

# ---------------------------------------------------------------------------
# BackupManifest
# ---------------------------------------------------------------------------

def test_backup_manifest_defaults():
    m = BackupManifest()
    assert m.schema_version == "1.0"
    assert m.manifest_id == ""
    assert m.backups == []
    assert m.total_backups == 0
    assert m.total_size_bytes == 0

def test_backup_manifest_add_backup():
    m = BackupManifest()
    r = BackupRecord(backup_id="bk_001", size_bytes=512)
    m.add_backup(r)
    assert m.total_backups == 1
    assert m.total_size_bytes == 512

def test_backup_manifest_add_multiple():
    m = BackupManifest()
    m.add_backup(BackupRecord(backup_id="bk_001", size_bytes=256))
    m.add_backup(BackupRecord(backup_id="bk_002", size_bytes=768))
    assert m.total_backups == 2
    assert m.total_size_bytes == 1024

def test_backup_manifest_to_dict():
    m = BackupManifest(manifest_id="bkm_001")
    d = m.to_dict()
    assert d["manifest_id"] == "bkm_001"

# ---------------------------------------------------------------------------
# BackupManager
# ---------------------------------------------------------------------------

def test_backup_manager_defaults():
    mgr = BackupManager()
    assert mgr.list_backups() == []
    manifest = mgr.get_manifest()
    assert manifest.manifest_id.startswith("bkm-")

def test_backup_manager_create_backup():
    mgr = BackupManager()
    r = mgr.create_backup(BC_AUDIT_HISTORY, source_paths=["/tmp/audit.log"])
    assert r.backup_id.startswith("bk-")
    assert r.category == BC_AUDIT_HISTORY
    assert r.status == BK_PENDING
    assert r.source_paths == ["/tmp/audit.log"]

def test_backup_manager_complete_backup():
    mgr = BackupManager()
    r = mgr.create_backup(BC_POLICIES)
    assert mgr.complete_backup(r.backup_id, backup_paths=["/backup/policies.json"],
                                checksum="def456", size_bytes=2048) is True
    assert r.status == BK_COMPLETED
    assert r.backup_paths == ["/backup/policies.json"]
    assert r.checksum == "def456"
    assert r.size_bytes == 2048
    assert r.completed_at != ""

def test_backup_manager_complete_nonexistent():
    mgr = BackupManager()
    assert mgr.complete_backup("nonexistent") is False

def test_backup_manager_fail_backup():
    mgr = BackupManager()
    r = mgr.create_backup(BC_MODEL_RUN_METADATA)
    assert mgr.fail_backup(r.backup_id, errors=["Disk full"]) is True
    assert r.status == BK_FAILED
    assert r.errors == ["Disk full"]

def test_backup_manager_fail_nonexistent():
    mgr = BackupManager()
    assert mgr.fail_backup("nonexistent") is False

def test_backup_manager_get_backup():
    mgr = BackupManager()
    r = mgr.create_backup(BC_AUDIT_HISTORY)
    assert mgr.get_backup(r.backup_id) is r

def test_backup_manager_get_nonexistent():
    mgr = BackupManager()
    assert mgr.get_backup("nonexistent") is None

def test_backup_manager_list_by_category():
    mgr = BackupManager()
    mgr.create_backup(BC_AUDIT_HISTORY)
    mgr.create_backup(BC_POLICIES)
    mgr.create_backup(BC_AUDIT_HISTORY)
    assert len(mgr.list_backups(BC_AUDIT_HISTORY)) == 2
    assert len(mgr.list_backups(BC_POLICIES)) == 1
    assert len(mgr.list_backups(BC_APPROVALS)) == 0

def test_backup_manager_list_all():
    mgr = BackupManager()
    mgr.create_backup(BC_AUDIT_HISTORY)
    mgr.create_backup(BC_POLICIES)
    assert len(mgr.list_backups()) == 2

def test_backup_manager_clear():
    mgr = BackupManager()
    mgr.create_backup(BC_AUDIT_HISTORY)
    mgr.clear()
    assert mgr.list_backups() == []

def test_backup_manager_manifest():
    mgr = BackupManager()
    mgr.create_backup(BC_AUDIT_HISTORY)
    mgr.create_backup(BC_POLICIES)
    manifest = mgr.get_manifest()
    assert manifest.total_backups == 2

# ---------------------------------------------------------------------------
# BackupManager can_restore
# ---------------------------------------------------------------------------

def test_can_restore_completed():
    mgr = BackupManager()
    r = mgr.create_backup(BC_AUDIT_HISTORY, source_paths=["/tmp/data"])
    mgr.complete_backup(r.backup_id, backup_paths=["/backup/data"])
    ok, msg = mgr.can_restore(r.backup_id)
    assert ok is True
    assert msg == "Ready to restore"

def test_can_restore_nonexistent():
    mgr = BackupManager()
    ok, msg = mgr.can_restore("nonexistent")
    assert ok is False
    assert "not found" in msg

def test_can_restore_pending():
    mgr = BackupManager()
    r = mgr.create_backup(BC_AUDIT_HISTORY)
    ok, msg = mgr.can_restore(r.backup_id)
    assert ok is False
    assert "PENDING" in msg

def test_can_restore_no_paths():
    mgr = BackupManager()
    r = mgr.create_backup(BC_AUDIT_HISTORY)
    mgr.complete_backup(r.backup_id)
    ok, msg = mgr.can_restore(r.backup_id)
    assert ok is False
    assert "No backup paths" in msg

# ---------------------------------------------------------------------------
# BackupManager recovery scenarios
# ---------------------------------------------------------------------------

def test_check_recovery_scenario():
    mgr = BackupManager()
    strategy = mgr.check_recovery_scenario(RS_CORRUPTED_LATEST_ARTIFACT)
    assert strategy == "Use previous artifact version from history"

def test_check_recovery_scenario_unknown():
    mgr = BackupManager()
    strategy = mgr.check_recovery_scenario("unknown")
    assert strategy == "UNKNOWN_SCENARIO"

def test_all_recovery_scenarios_have_strategies():
    mgr = BackupManager()
    for scenario in ALL_RECOVERY_SCENARIOS:
        strategy = mgr.check_recovery_scenario(scenario)
        assert strategy != "UNKNOWN_SCENARIO", f"Missing strategy for {scenario}"
        assert strategy != "No recovery strategy defined"
