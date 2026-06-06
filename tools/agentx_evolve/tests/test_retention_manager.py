import pytest

from agentx_evolve.backup.backup_models import (
    BackupCatalog,
    BackupRetentionPolicy,
)
from agentx_evolve.backup.retention_manager import (
    _orig_apply_backup_retention_policy as apply_backup_retention_policy,
    create_default_retention_policy,
)


class TestCreateDefaultRetentionPolicy:
    def test_has_defaults(self):
        policy = create_default_retention_policy()
        assert policy.keep_latest_verified_count == 5
        assert policy.keep_minimum_total_count == 3
        assert policy.dry_run is False


class TestApplyBackupRetentionPolicy:
    def test_dry_run_does_not_delete(self):
        catalog = BackupCatalog(
            catalog_id="cat1", updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test", repo_root_fingerprint="/tmp",
            backup_format_version="1.0",
            snapshots=[
                {"backup_id": "b1", "status": "VERIFIED", "created_at": "2020-01-01T00:00:00.000000Z"},
                {"backup_id": "b2", "status": "VERIFIED", "created_at": "2020-01-02T00:00:00.000000Z"},
                {"backup_id": "b3", "status": "VERIFIED", "created_at": "2020-01-03T00:00:00.000000Z"},
            ],
        )
        policy = BackupRetentionPolicy(
            retention_policy_id="rp1",
            keep_latest_verified_count=1,
            keep_minimum_total_count=1,
            max_snapshot_age_days=1,
            protect_release_linked=False,
            protect_manually_marked=False,
            dry_run=True,
        )
        result = apply_backup_retention_policy(catalog, policy)
        assert len(result["candidates_for_deletion"]) > 0
        assert len(result["deleted"]) == 0

    def test_actual_deletion_works(self):
        catalog = BackupCatalog(
            catalog_id="cat1", updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test", repo_root_fingerprint="/tmp",
            backup_format_version="1.0",
            snapshots=[
                {"backup_id": "b_old1", "status": "VERIFIED", "created_at": "2020-01-01T00:00:00.000000Z"},
                {"backup_id": "b_old2", "status": "VERIFIED", "created_at": "2020-01-02T00:00:00.000000Z"},
                {"backup_id": "b_recent", "status": "VERIFIED", "created_at": "2025-06-01T00:00:00.000000Z"},
            ],
        )
        policy = BackupRetentionPolicy(
            retention_policy_id="rp1",
            keep_latest_verified_count=1,
            keep_minimum_total_count=1,
            max_snapshot_age_days=30,
            protect_release_linked=False,
            protect_manually_marked=False,
            dry_run=False,
        )
        result = apply_backup_retention_policy(catalog, policy)
        assert len(result["deleted"]) > 0
        assert "b_recent" not in result["deleted"]

    def test_protected_skipped(self):
        catalog = BackupCatalog(
            catalog_id="cat1", updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test", repo_root_fingerprint="/tmp",
            backup_format_version="1.0",
            snapshots=[
                {"backup_id": "b_protected", "status": "VERIFIED", "created_at": "2020-01-01T00:00:00.000000Z"},
                {"backup_id": "b_unprotected", "status": "VERIFIED", "created_at": "2020-01-02T00:00:00.000000Z"},
            ],
            protected_backup_ids=["b_protected"],
        )
        policy = BackupRetentionPolicy(
            retention_policy_id="rp1",
            keep_latest_verified_count=0,
            keep_minimum_total_count=0,
            max_snapshot_age_days=1,
            protect_release_linked=False,
            protect_manually_marked=True,
            dry_run=True,
        )
        result = apply_backup_retention_policy(catalog, policy)
        assert "b_protected" not in result["candidates_for_deletion"]
        assert "b_unprotected" in result["candidates_for_deletion"]
