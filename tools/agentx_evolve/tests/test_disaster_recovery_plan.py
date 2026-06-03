from __future__ import annotations

from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    BackupCatalog,
    DisasterRecoveryPlan,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
)
from agentx_evolve.backup.disaster_recovery_planner import (
    _orig_build_disaster_recovery_plan as build_disaster_recovery_plan,
)


class TestDisasterRecoveryPlan:
    def test_builds_dr_plan_with_catalog(self):
        catalog = BackupCatalog(
            catalog_id=new_id("cat"),
            updated_at=utc_now_iso(),
            latest_verified_backup_id="bck_verified_001",
        )
        plan = build_disaster_recovery_plan(catalog, trigger="test_trigger")
        assert isinstance(plan, DisasterRecoveryPlan)
        assert plan.trigger == "test_trigger"
        assert plan.selected_backup_id == "bck_verified_001"

    def test_builds_dr_plan_without_catalog(self):
        plan = build_disaster_recovery_plan(None, trigger="no_catalog")
        assert plan.selected_backup_id is None
        assert any("No backup catalog" in r for r in plan.rejected_backup_ids)

    def test_dr_plan_has_recovery_steps(self):
        catalog = BackupCatalog(
            catalog_id=new_id("cat"),
            updated_at=utc_now_iso(),
            latest_verified_backup_id="bck_002",
        )
        plan = build_disaster_recovery_plan(catalog, trigger="drill")
        assert len(plan.recovery_steps) > 0
        assert len(plan.validation_steps) > 0

    def test_dr_plan_falls_back_to_last_snapshot(self):
        catalog = BackupCatalog(
            catalog_id=new_id("cat"),
            updated_at=utc_now_iso(),
            latest_verified_backup_id=None,
            snapshots=[
                {"backup_id": "bck_old_001", "created_at": "2026-01-01T00:00:00Z", "status": "VERIFIED"},
                {"backup_id": "bck_old_002", "created_at": "2026-01-02T00:00:00Z", "status": "CREATED"},
            ],
        )
        plan = build_disaster_recovery_plan(catalog, trigger="fallback")
        assert plan.selected_backup_id == "bck_old_002" or plan.selected_backup_id == "bck_old_001"

    def test_dr_plan_rejects_deleted_backup(self):
        catalog = BackupCatalog(
            catalog_id=new_id("cat"),
            updated_at=utc_now_iso(),
            latest_verified_backup_id="bck_deleted",
            deleted_backup_ids=["bck_deleted"],
        )
        plan = build_disaster_recovery_plan(catalog, trigger="deleted_check")
        assert plan.selected_backup_id is None

    def test_dr_plan_serializes_to_dict(self):
        catalog = BackupCatalog(
            catalog_id=new_id("cat"),
            updated_at=utc_now_iso(),
            latest_verified_backup_id="bck_003",
        )
        plan = build_disaster_recovery_plan(catalog, trigger="serialize")
        d = to_dict(plan)
        assert isinstance(d, dict)
        assert "disaster_recovery_plan_id" in d
        assert "recovery_steps" in d
