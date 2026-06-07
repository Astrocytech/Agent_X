from __future__ import annotations

from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_PASS,
    VALIDATION_STATUS_PARTIAL,
    BackupFileRecord,
    BackupManifest,
    new_id,
    resolve_repo_root,
    sha256_file,
    utc_now_iso,
)
from agentx_evolve.backup.snapshot_verifier import _orig_verify_backup_snapshot as verify_backup_snapshot


class TestIntegrityVerification:
    def test_verify_missing_snapshot_dir_fails(self, tmp_path: Path):
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            snapshot_path=str(tmp_path / "nonexistent"),
        )
        result = verify_backup_snapshot(manifest, repo_root=tmp_path)
        assert result.status == VALIDATION_STATUS_FAIL
        assert result.files_checked == 0

    def test_verify_all_passed(self, tmp_path: Path):
        snap_dir = tmp_path / "snapshots" / "bck_001"
        snap_dir.mkdir(parents=True)
        (snap_dir / "f1.txt").write_text("content1")
        fhash = sha256_file(snap_dir / "f1.txt")
        record = BackupFileRecord(
            relative_path="f1.txt",
            original_path="f1.txt",
            backup_path=str(snap_dir / "f1.txt"),
            file_size_bytes=8,
            sha256=fhash,
            included=True,
            path_type="file",
        )
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            snapshot_path=str(snap_dir),
            file_records=[record],
        )
        result = verify_backup_snapshot(manifest, repo_root=tmp_path)
        assert result.status == VALIDATION_STATUS_PASS
        assert result.files_passed == 1

    def test_verify_hash_mismatch_fails(self, tmp_path: Path):
        snap_dir = tmp_path / "snapshots" / "bck_002"
        snap_dir.mkdir(parents=True)
        (snap_dir / "f1.txt").write_text("content1")
        record = BackupFileRecord(
            relative_path="f1.txt",
            original_path="f1.txt",
            backup_path=str(snap_dir / "f1.txt"),
            file_size_bytes=8,
            sha256="0000000000000000000000000000000000000000000000000000000000000000",
            included=True,
            path_type="file",
        )
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            snapshot_path=str(snap_dir),
            file_records=[record],
        )
        result = verify_backup_snapshot(manifest, repo_root=tmp_path)
        assert result.status == VALIDATION_STATUS_FAIL
        assert result.files_failed == 1

    def test_verify_partial_pass(self, tmp_path: Path):
        snap_dir = tmp_path / "snapshots" / "bck_003"
        snap_dir.mkdir(parents=True)
        (snap_dir / "f1.txt").write_text("good")
        fhash = sha256_file(snap_dir / "f1.txt")
        records = [
            BackupFileRecord(
                relative_path="f1.txt", original_path="f1.txt",
                backup_path=str(snap_dir / "f1.txt"),
                file_size_bytes=4, sha256=fhash,
                included=True, path_type="file",
            ),
            BackupFileRecord(
                relative_path="f2.txt", original_path="f2.txt",
                backup_path=str(snap_dir / "f2.txt"),
                file_size_bytes=0, sha256=None,
                included=True, path_type="file",
            ),
        ]
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            snapshot_path=str(snap_dir),
            file_records=records,
        )
        result = verify_backup_snapshot(manifest, repo_root=tmp_path)
        assert result.status in (VALIDATION_STATUS_PASS, VALIDATION_STATUS_PARTIAL)

    def test_verify_skips_directories(self, tmp_path: Path):
        snap_dir = tmp_path / "snapshots" / "bck_004"
        snap_dir.mkdir(parents=True)
        record = BackupFileRecord(
            relative_path="subdir", original_path="subdir",
            backup_path=str(snap_dir / "subdir"),
            file_size_bytes=0, included=True, path_type="directory",
        )
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            snapshot_path=str(snap_dir),
            file_records=[record],
        )
        result = verify_backup_snapshot(manifest, repo_root=tmp_path)
        assert result.files_checked == 0
