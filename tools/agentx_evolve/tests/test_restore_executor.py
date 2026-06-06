from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    RESTORE_STATUS_BLOCKED,
    RESTORE_STATUS_RESTORED,
    BackupFileRecord,
    BackupManifest,
    RestorePlan,
)
from agentx_evolve.backup.restore_executor import _orig_execute_restore_plan as execute_restore_plan


class TestExecuteRestorePlan:
    def test_blocked_plan_returns_blocked(self):
        plan = RestorePlan(
            restore_plan_id="plan1", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            blocked_reasons=["policy denied"],
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root="/tmp", snapshot_path="/tmp",
        )
        result = execute_restore_plan(plan, manifest)
        assert result.status == RESTORE_STATUS_BLOCKED

    def test_dry_run_plan_restores_virtually(self):
        plan = RestorePlan(
            restore_plan_id="plan2", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            dry_run=True,
            files_to_restore=["/tmp/f1.txt"],
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root="/tmp", snapshot_path="/tmp",
        )
        result = execute_restore_plan(plan, manifest)
        assert result.status == RESTORE_STATUS_RESTORED
        assert "/tmp/f1.txt" in result.restored_files

    def test_restore_copies_files(self, tmp_path: Path):
        snap = tmp_path / "snap"
        snap.mkdir(parents=True)
        (snap / "f1.txt").write_text("restored content")

        target = tmp_path / "target"
        target.mkdir(parents=True)

        manifest = BackupManifest(
            backup_id="b1",
            repo_root=str(tmp_path),
            snapshot_path=str(snap),
            file_records=[
                BackupFileRecord(
                    relative_path="f1.txt", original_path=str(target / "f1.txt"),
                    backup_path=str(snap / "f1.txt"),
                    file_size_bytes=16, included=True, path_type="file",
                ),
            ],
        )
        plan = RestorePlan(
            restore_plan_id="plan3", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            dry_run=False,
            files_to_restore=[str(target / "f1.txt")],
        )
        result = execute_restore_plan(plan, manifest)
        assert result.status == RESTORE_STATUS_RESTORED
        assert (target / "f1.txt").exists()
        assert (target / "f1.txt").read_text() == "restored content"

    def test_missing_snapshot_dir_fails(self, tmp_path: Path):
        manifest = BackupManifest(
            backup_id="b1",
            repo_root=str(tmp_path),
            snapshot_path=str(tmp_path / "nonexistent"),
        )
        plan = RestorePlan(
            restore_plan_id="plan4", restore_request_id="req1",
            backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
            dry_run=False,
        )
        result = execute_restore_plan(plan, manifest)
        assert result.status in (RESTORE_STATUS_BLOCKED, "FAILED")
