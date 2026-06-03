import json
from pathlib import Path

import pytest

from agentx_evolve.backup.backup_manifest import (
    _orig_build_backup_manifest as build_backup_manifest,
    delete_backup_manifest,
    finalize_manifest_hash,
    list_backup_manifests,
    load_backup_manifest,
    write_backup_manifest,
)
from agentx_evolve.backup.backup_models import (
    GIT_STATUS_CLEAN,
    GIT_STATUS_UNKNOWN,
    BackupFileRecord,
)


class TestBuildBackupManifest:
    def test_builds_manifest_with_defaults(self):
        manifest = build_backup_manifest(backup_id="bck_001")
        assert manifest.backup_id == "bck_001"
        assert manifest.status == "CREATED"
        assert manifest.git_status_summary == GIT_STATUS_UNKNOWN

    def test_accepts_file_records(self):
        records = [
            BackupFileRecord(
                relative_path="f.py", original_path="/repo/f.py",
                backup_path="/bkp/f.py", file_size_bytes=100,
                included=True, path_type="file",
            )
        ]
        manifest = build_backup_manifest(
            backup_id="bck_002", file_records=records,
        )
        assert len(manifest.file_records) == 1


class TestWriteLoadManifest:
    def test_write_and_load(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "manifests").mkdir(parents=True, exist_ok=True)
        manifest = build_backup_manifest(backup_id="bck_w1", repo_root=tmp_path)
        write_backup_manifest(manifest, repo_root=tmp_path)
        loaded = load_backup_manifest("bck_w1", repo_root=tmp_path)
        assert loaded is not None
        assert loaded.backup_id == "bck_w1"

    def test_load_nonexistent(self, tmp_path: Path):
        loaded = load_backup_manifest("nonexistent", repo_root=tmp_path)
        assert loaded is None


class TestListManifests:
    def test_lists_manifests(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "manifests").mkdir(parents=True, exist_ok=True)
        m1 = build_backup_manifest(backup_id="bck_l1", repo_root=tmp_path)
        m2 = build_backup_manifest(backup_id="bck_l2", repo_root=tmp_path)
        write_backup_manifest(m1, repo_root=tmp_path)
        write_backup_manifest(m2, repo_root=tmp_path)
        ids = list_backup_manifests(repo_root=tmp_path)
        assert "bck_l1" in ids
        assert "bck_l2" in ids

    def test_empty_dir(self, tmp_path: Path):
        assert list_backup_manifests(repo_root=tmp_path) == []


class TestFinalizeManifestHash:
    def test_finalize_adds_hash(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "manifests").mkdir(parents=True, exist_ok=True)
        manifest = build_backup_manifest(backup_id="bck_h1", repo_root=tmp_path)
        write_backup_manifest(manifest, repo_root=tmp_path)
        manifest.manifest_sha256 = None
        result = finalize_manifest_hash(manifest, repo_root=tmp_path)
        assert result.manifest_sha256 is not None
        assert len(result.manifest_sha256) == 64


class TestDeleteManifest:
    def test_deletes_existing(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "manifests").mkdir(parents=True, exist_ok=True)
        manifest = build_backup_manifest(backup_id="bck_d1", repo_root=tmp_path)
        write_backup_manifest(manifest, repo_root=tmp_path)
        assert delete_backup_manifest("bck_d1", repo_root=tmp_path) is True
        assert load_backup_manifest("bck_d1", repo_root=tmp_path) is None

    def test_delete_nonexistent(self, tmp_path: Path):
        assert delete_backup_manifest("nonexistent", repo_root=tmp_path) is False
