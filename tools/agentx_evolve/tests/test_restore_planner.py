import json
from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_DRY_RUN_ONLY,
    RESTORE_MODE_DRY_RUN,
    RESTORE_MODE_RUNTIME_ONLY,
    RESTORE_STATUS_BLOCKED,
    BackupManifest,
    BackupSnapshotRecord,
    RestoreRequest,
)
from agentx_evolve.backup.restore_planner import (
    _orig_create_restore_decision as create_restore_decision,
    _orig_plan_restore as plan_restore,
)
from agentx_evolve.backup.restore_preflight import _orig_build_restore_preflight_record as build_restore_preflight_record


class TestCreateRestoreDecision:
    def test_blocks_when_preflight_has_blockers(self):
        request = RestoreRequest(
            restore_request_id="req1", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
        )
        preflight = build_restore_preflight_record(request, manifest=None, catalog=None)
        decision = create_restore_decision(request, preflight)
        assert decision.decision == DECISION_BLOCK

    def test_blocks_source_restore_in_v1(self):
        request = RestoreRequest(
            restore_request_id="req2", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
            restore_mode="SOURCE_RESTORE",
            dry_run=False,
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root="/tmp",
            snapshot_path="/tmp/snap", status="VERIFIED",
        )
        preflight = build_restore_preflight_record(request, manifest=manifest, catalog=None)
        decision = create_restore_decision(request, preflight)
        assert decision.decision == DECISION_BLOCK

    def test_allows_runtime_restore(self):
        request = RestoreRequest(
            restore_request_id="req3", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
            restore_mode=RESTORE_MODE_RUNTIME_ONLY,
            dry_run=False,
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root="/tmp",
            snapshot_path="/tmp/snap", status="VERIFIED",
        )
        preflight = build_restore_preflight_record(request, manifest=manifest, catalog=None)
        decision = create_restore_decision(request, preflight)
        assert decision.decision == DECISION_ALLOW

    def test_dry_run_returns_dry_run_only(self):
        request = RestoreRequest(
            restore_request_id="req4", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
            restore_mode=RESTORE_MODE_DRY_RUN,
            dry_run=True,
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root="/tmp",
            snapshot_path="/tmp/snap", status="VERIFIED",
        )
        preflight = build_restore_preflight_record(request, manifest=manifest, catalog=None)
        decision = create_restore_decision(request, preflight)
        assert decision.decision == DECISION_DRY_RUN_ONLY


class TestPlanRestore:
    def test_plan_is_blocked_when_decision_blocks(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "restore_plans").mkdir(parents=True, exist_ok=True)
        request = RestoreRequest(
            restore_request_id="req_p1", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
            restore_mode="SOURCE_RESTORE",
            dry_run=False,
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root=str(tmp_path),
            snapshot_path=str(tmp_path / "snap"), status="VERIFIED",
        )
        preflight = build_restore_preflight_record(request, manifest=manifest, catalog=None)
        decision = create_restore_decision(request, preflight)
        plan = plan_restore(request, manifest, decision, repo_root=tmp_path)
        assert plan.status == RESTORE_STATUS_BLOCKED

    def test_plan_has_files_when_allowed(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "restore_plans").mkdir(parents=True, exist_ok=True)
        request = RestoreRequest(
            restore_request_id="req_p2", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
            restore_mode=RESTORE_MODE_RUNTIME_ONLY,
            dry_run=True,
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root=str(tmp_path),
            snapshot_path=str(tmp_path / "snap"), status="VERIFIED",
        )
        preflight = build_restore_preflight_record(request, manifest=manifest, catalog=None)
        decision = create_restore_decision(request, preflight)
        plan = plan_restore(request, manifest, decision, repo_root=tmp_path)
        assert plan.status != RESTORE_STATUS_BLOCKED
