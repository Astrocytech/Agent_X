from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import BackupCatalog
from agentx_evolve.backup.disaster_recovery_planner import _orig_build_disaster_recovery_plan as build_disaster_recovery_plan


class TestBuildDisasterRecoveryPlan:
    def test_no_catalog_rejects(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "disaster_recovery").mkdir(parents=True, exist_ok=True)
        plan = build_disaster_recovery_plan(catalog=None, trigger="test", repo_root=tmp_path)
        assert plan.selected_backup_id is None
        assert len(plan.rejected_backup_ids) > 0

    def test_selects_latest_verified(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "disaster_recovery").mkdir(parents=True, exist_ok=True)
        catalog = BackupCatalog(
            catalog_id="cat1", updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test", repo_root_fingerprint="/tmp",
            backup_format_version="1.0",
            latest_verified_backup_id="bck_verified_1",
            snapshots=[{"backup_id": "bck_verified_1", "status": "VERIFIED", "created_at": "2025-01-01T00:00:00.000000Z"}],
        )
        plan = build_disaster_recovery_plan(catalog=catalog, trigger="test", repo_root=tmp_path)
        assert plan.selected_backup_id == "bck_verified_1"

    def test_rejects_deleted_backup(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "disaster_recovery").mkdir(parents=True, exist_ok=True)
        catalog = BackupCatalog(
            catalog_id="cat1", updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test", repo_root_fingerprint="/tmp",
            backup_format_version="1.0",
            latest_verified_backup_id="bck_deleted_1",
            deleted_backup_ids=["bck_deleted_1"],
            snapshots=[{"backup_id": "bck_deleted_1", "status": "VERIFIED", "created_at": "2025-01-01T00:00:00.000000Z"}],
        )
        plan = build_disaster_recovery_plan(catalog=catalog, trigger="test", repo_root=tmp_path)
        assert plan.selected_backup_id is None

    def test_has_default_steps(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "disaster_recovery").mkdir(parents=True, exist_ok=True)
        plan = build_disaster_recovery_plan(
            catalog=BackupCatalog(
                catalog_id="cat1", updated_at="2025-01-01T00:00:00.000000Z",
                project_id="test", repo_root_fingerprint="/tmp",
                backup_format_version="1.0",
                latest_verified_backup_id="bck_v1",
                snapshots=[{"backup_id": "bck_v1", "status": "VERIFIED", "created_at": "2025-01-01T00:00:00.000000Z"}],
            ),
            trigger="test",
            repo_root=tmp_path,
        )
        assert len(plan.recovery_steps) > 0
        assert len(plan.validation_steps) > 0
        assert len(plan.rollback_steps) > 0
        assert len(plan.required_approvals) > 0
