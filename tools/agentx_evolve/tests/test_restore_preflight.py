from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    BACKUP_STATUS_VERIFIED,
    BackupCatalog,
    BackupManifest,
    RestoreRequest,
)
from agentx_evolve.backup.restore_preflight import _orig_build_restore_preflight_record as build_restore_preflight_record


class TestBuildRestorePreflightRecord:
    def test_no_manifest_adds_blocker(self):
        request = RestoreRequest(
            restore_request_id="req1", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
        )
        preflight = build_restore_preflight_record(request, manifest=None, catalog=None)
        assert len(preflight.blockers) > 0
        assert preflight.verified_backup is False

    def test_unverified_manifest_adds_blocker(self):
        request = RestoreRequest(
            restore_request_id="req2", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root="/tmp",
            snapshot_path="/tmp/snap", status="CREATED",
        )
        preflight = build_restore_preflight_record(request, manifest=manifest, catalog=None)
        assert preflight.verified_backup is False

    def test_verified_manifest_passes_check(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "catalog").mkdir(parents=True, exist_ok=True)
        request = RestoreRequest(
            restore_request_id="req3", backup_id="b1",
            requested_at="2025-01-01T00:00:00.000000Z",
            requested_by_role="admin",
        )
        manifest = BackupManifest(
            backup_id="b1", repo_root=str(tmp_path),
            snapshot_path="/tmp/snap", status=BACKUP_STATUS_VERIFIED,
        )
        catalog = BackupCatalog(
            catalog_id="cat1", updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test", repo_root_fingerprint="/tmp",
            backup_format_version="1.0",
        )
        preflight = build_restore_preflight_record(request, manifest=manifest, catalog=catalog)
        assert preflight.verified_backup is True
