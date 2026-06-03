from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_PARTIAL,
    VALIDATION_STATUS_PASS,
    BackupFileRecord,
    BackupManifest,
    BackupSnapshotRecord,
)
from agentx_evolve.backup.snapshot_verifier import (
    verify_backup_by_id,
    _orig_verify_backup_snapshot as verify_backup_snapshot,
)


def _make_manifest(snapshot_dir: Path) -> BackupManifest:
    return BackupManifest(
        backup_id="bck_v1",
        repo_root=str(snapshot_dir.parent),
        snapshot_path=str(snapshot_dir),
        file_records=[
            BackupFileRecord(
                relative_path="f1.txt", original_path="/r/f1.txt",
                backup_path=str(snapshot_dir / "f1.txt"),
                file_size_bytes=5,                 sha256="2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
                included=True, path_type="file",
            ),
            BackupFileRecord(
                relative_path="f2.txt", original_path="/r/f2.txt",
                backup_path=str(snapshot_dir / "f2.txt"),
                file_size_bytes=5,                 sha256="486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65260e9cb8a7",
                included=True, path_type="file",
            ),
        ],
    )


class TestVerifyBackupSnapshot:
    def test_passes_when_all_match(self, tmp_path: Path):
        snap = tmp_path / "snap"
        snap.mkdir(parents=True)
        (snap / "f1.txt").write_text("hello")
        (snap / "f2.txt").write_text("world")
        manifest = _make_manifest(snap)
        result = verify_backup_snapshot(manifest)
        assert result.status == VALIDATION_STATUS_PASS
        assert result.files_checked == 2
        assert result.files_passed == 2
        assert result.files_failed == 0

    def test_fails_on_missing_file(self, tmp_path: Path):
        snap = tmp_path / "snap"
        snap.mkdir(parents=True)
        (snap / "f1.txt").write_text("hello")
        manifest = _make_manifest(snap)
        result = verify_backup_snapshot(manifest)
        assert result.status in (VALIDATION_STATUS_FAIL, VALIDATION_STATUS_PARTIAL)
        assert result.files_failed >= 1

    def test_fails_on_hash_mismatch(self, tmp_path: Path):
        snap = tmp_path / "snap"
        snap.mkdir(parents=True)
        (snap / "f1.txt").write_text("hello")
        (snap / "f2.txt").write_text("WRONG")
        manifest = _make_manifest(snap)
        result = verify_backup_snapshot(manifest)
        assert result.status in (VALIDATION_STATUS_FAIL, VALIDATION_STATUS_PARTIAL)
        assert len(result.hash_mismatches) >= 1

    def test_missing_snapshot_dir(self, tmp_path: Path):
        manifest = _make_manifest(tmp_path / "nonexistent")
        result = verify_backup_snapshot(manifest)
        assert result.status == VALIDATION_STATUS_FAIL


class TestVerifyBackupById:
    def test_returns_none_for_missing(self, tmp_path: Path):
        result = verify_backup_by_id("nonexistent", repo_root=tmp_path)
        assert result is None
