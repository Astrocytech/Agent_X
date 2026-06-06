import json
from pathlib import Path

import pytest

from agentx_evolve.backup.backup_catalog import (
    get_backup_ids_by_status,
    get_latest_verified_backup_id,
    is_backup_deleted,
    is_backup_protected,
    load_backup_catalog,
    mark_backup_deleted,
    protect_backup,
    record_stale_staging_path,
    unprotect_backup,
    update_catalog_for_manifest,
    write_backup_catalog,
)
from agentx_evolve.backup.backup_models import (
    BACKUP_STATUS_CREATED,
    BACKUP_STATUS_VERIFIED,
    BackupCatalog,
    BackupManifest,
    BackupSnapshotRecord,
    GIT_STATUS_CLEAN,
)


@pytest.fixture
def empty_catalog() -> BackupCatalog:
    return BackupCatalog(
        catalog_id="test_cat",
        updated_at="2025-01-01T00:00:00.000000Z",
        project_id="test_project",
        repo_root_fingerprint="/tmp/test",
        backup_format_version="1.0",
    )


class TestLoadCatalog:
    def test_returns_default_when_no_file(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "catalog").mkdir(parents=True, exist_ok=True)
        catalog = load_backup_catalog(repo_root=tmp_path)
        assert catalog.catalog_id.startswith("cat_")
        assert catalog.project_id == "agentx"

    def test_loads_existing_catalog(self, tmp_path: Path):
        catalog_dir = tmp_path / ".agentx-init" / "backups" / "catalog"
        catalog_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_catalog.schema.json",
            "catalog_id": "existing_cat",
            "updated_at": "2025-01-01T00:00:00.000000Z",
            "project_id": "test",
            "repo_root_fingerprint": "/tmp/test",
            "backup_format_version": "1.0",
            "snapshots": [],
            "warnings": [],
            "errors": [],
        }
        (catalog_dir / "catalog.json").write_text(json.dumps(data))
        catalog = load_backup_catalog(repo_root=tmp_path)
        assert catalog.catalog_id == "existing_cat"


class TestWriteCatalog:
    def test_writes_and_reads_back(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "catalog").mkdir(parents=True, exist_ok=True)
        catalog = BackupCatalog(
            catalog_id="test_cat",
            updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test",
            repo_root_fingerprint="/tmp/test",
            backup_format_version="1.0",
        )
        write_backup_catalog(catalog, repo_root=tmp_path)
        loaded = load_backup_catalog(repo_root=tmp_path)
        assert loaded.catalog_id == "test_cat"

    def test_sidecar_written(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "catalog").mkdir(parents=True, exist_ok=True)
        catalog = BackupCatalog(
            catalog_id="sidecar_test",
            updated_at="2025-01-01T00:00:00.000000Z",
            project_id="test",
            repo_root_fingerprint="/tmp/test",
            backup_format_version="1.0",
        )
        write_backup_catalog(catalog, repo_root=tmp_path)
        sidecar_path = tmp_path / ".agentx-init" / "backups" / "catalog" / "catalog.sha256"
        assert sidecar_path.exists()
        assert len(sidecar_path.read_text().strip()) == 64


class TestUpdateCatalogForManifest:
    def test_adds_snapshot_entry(self, empty_catalog: BackupCatalog):
        manifest = BackupManifest(
            backup_id="bck_001",
            created_at="2025-01-01T00:00:00.000000Z",
            repo_root="/tmp",
            snapshot_path="/tmp/snap",
            status=BACKUP_STATUS_CREATED,
        )
        cat = update_catalog_for_manifest(manifest, empty_catalog)
        assert len(cat.snapshots) == 1
        assert cat.snapshots[0]["backup_id"] == "bck_001"

    def test_updates_latest_verified(self, empty_catalog: BackupCatalog):
        manifest = BackupManifest(
            backup_id="bck_002",
            created_at="2025-01-01T00:00:00.000000Z",
            repo_root="/tmp",
            snapshot_path="/tmp/snap",
            status=BACKUP_STATUS_VERIFIED,
        )
        cat = update_catalog_for_manifest(manifest, empty_catalog)
        assert cat.latest_verified_backup_id == "bck_002"


class TestMarkBackupDeleted:
    def test_marks_backup_deleted(self, empty_catalog: BackupCatalog):
        cat = mark_backup_deleted("bck_001", empty_catalog)
        assert "bck_001" in cat.deleted_backup_ids

    def test_removes_from_snapshots(self, empty_catalog: BackupCatalog):
        cat = update_catalog_for_manifest(
            BackupManifest(backup_id="bck_001", created_at="2025-01-01T00:00:00.000000Z",
                          repo_root="/tmp", snapshot_path="/tmp/snap"),
            empty_catalog,
        )
        cat = mark_backup_deleted("bck_001", cat)
        snapshots = [s for s in cat.snapshots if s.get("backup_id") == "bck_001"]
        assert len(snapshots) == 0


class TestRecordStaleStagingPath:
    def test_records_path(self, empty_catalog: BackupCatalog):
        cat = record_stale_staging_path("/tmp/stale", empty_catalog)
        assert "/tmp/stale" in cat.stale_staging_paths

    def test_no_duplicates(self, empty_catalog: BackupCatalog):
        cat = record_stale_staging_path("/tmp/stale", empty_catalog)
        cat = record_stale_staging_path("/tmp/stale", cat)
        assert len(cat.stale_staging_paths) == 1


class TestGetBackupIdsByStatus:
    def test_filters_by_status(self, empty_catalog: BackupCatalog):
        cat = update_catalog_for_manifest(
            BackupManifest(backup_id="b1", created_at="2025-01-01T00:00:00.000000Z",
                          repo_root="/tmp", snapshot_path="/tmp/snap", status=BACKUP_STATUS_CREATED),
            empty_catalog,
        )
        cat = update_catalog_for_manifest(
            BackupManifest(backup_id="b2", created_at="2025-01-02T00:00:00.000000Z",
                          repo_root="/tmp", snapshot_path="/tmp/snap2", status=BACKUP_STATUS_VERIFIED),
            cat,
        )
        verified = get_backup_ids_by_status(cat, BACKUP_STATUS_VERIFIED)
        assert verified == ["b2"]


class TestLatestVerified:
    def test_returns_none_when_no_verified(self, empty_catalog: BackupCatalog):
        assert get_latest_verified_backup_id(empty_catalog) is None


class TestIsBackupDeleted:
    def test_deleted_backup(self, empty_catalog: BackupCatalog):
        cat = mark_backup_deleted("bck_001", empty_catalog)
        assert is_backup_deleted("bck_001", cat) is True

    def test_not_deleted(self, empty_catalog: BackupCatalog):
        assert is_backup_deleted("bck_001", empty_catalog) is False


class TestIsBackupProtected:
    def test_protected_backup(self, empty_catalog: BackupCatalog):
        cat = protect_backup("bck_001", empty_catalog)
        assert is_backup_protected("bck_001", cat) is True

    def test_not_protected(self, empty_catalog: BackupCatalog):
        assert is_backup_protected("bck_001", empty_catalog) is False


class TestProtectUnprotect:
    def test_protect_adds(self, empty_catalog: BackupCatalog):
        cat = protect_backup("bck_001", empty_catalog)
        assert "bck_001" in cat.protected_backup_ids

    def test_unprotect_removes(self, empty_catalog: BackupCatalog):
        cat = protect_backup("bck_001", empty_catalog)
        cat = unprotect_backup("bck_001", cat)
        assert "bck_001" not in cat.protected_backup_ids

    def test_no_duplicate_protect(self, empty_catalog: BackupCatalog):
        cat = protect_backup("bck_001", empty_catalog)
        cat = protect_backup("bck_001", cat)
        assert len(cat.protected_backup_ids) == 1
