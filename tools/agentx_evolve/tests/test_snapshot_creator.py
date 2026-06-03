from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    BackupManifest,
    BackupPolicy,
    BackupSnapshotRecord,
)
from agentx_evolve.backup.snapshot_creator import (
    build_snapshot_index,
    _orig_create_backup_snapshot as create_backup_snapshot,
    finalize_snapshot,
)


@pytest.fixture
def repo_with_source(tmp_path: Path) -> Path:
    (tmp_path / ".agentx-init" / "backups" / "staging").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".agentx-init" / "backups" / "snapshots").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "src" / "utils.py").write_text("def util(): pass")
    (tmp_path / ".git").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestCreateBackupSnapshot:
    def test_creates_snapshot_with_files(self, repo_with_source: Path):
        manifest = BackupManifest(
            backup_id="bck_s1",
            repo_root=str(repo_with_source),
            snapshot_path="",
        )
        result = create_backup_snapshot(
            manifest, source_root=repo_with_source / "src",
            repo_root=repo_with_source,
        )
        assert result.backup_id == "bck_s1"
        assert result.status == "STAGED"
        assert len(result.file_records) > 0
        assert result.snapshot_record is not None
        assert result.snapshot_record.file_count > 0

    def test_respects_exclusions(self, repo_with_source: Path):
        policy = BackupPolicy(
            excluded_paths=[".git"],
            allowed_backup_roots=["."],
            allowed_restore_roots=[".agentx-init"],
            excluded_globs=[],
            excluded_secret_patterns=[],
            require_git_status=False,
            require_hashes=False,
            require_manifest_validation=False,
            require_restore_dry_run=False,
            allow_source_backup=True,
            allow_source_restore=False,
            allow_runtime_restore=False,
            allow_release_restore=False,
            allow_secret_backup_plaintext=False,
        )
        manifest = BackupManifest(
            backup_id="bck_s2",
            repo_root=str(repo_with_source),
            snapshot_path="",
        )
        result = create_backup_snapshot(
            manifest, source_root=repo_with_source,
            policy=policy, repo_root=repo_with_source,
        )
        git_excluded = [
            r for r in result.excluded_records
            if ".git" in r.relative_path
        ]
        assert len(git_excluded) > 0


class TestFinalizeSnapshot:
    def test_finalizes_and_moves(self, repo_with_source: Path):
        manifest = BackupManifest(
            backup_id="bck_f1",
            repo_root=str(repo_with_source),
            snapshot_path="",
        )
        result = create_backup_snapshot(
            manifest, source_root=repo_with_source / "src",
            repo_root=repo_with_source,
        )
        finalized = finalize_snapshot(result, repo_root=repo_with_source)
        assert finalized.snapshot_record is not None
        assert finalized.snapshot_record.finalized is True
        assert finalized.status == "CREATED"


class TestBuildSnapshotIndex:
    def test_builds_index(self, repo_with_source: Path):
        manifest = BackupManifest(
            backup_id="bck_i1",
            repo_root=str(repo_with_source),
            snapshot_path="/tmp/snap",
        )
        index = build_snapshot_index(manifest)
        assert index.backup_id == "bck_i1"
        assert index.snapshot_index_id.startswith("si_")
        assert index.snapshot_sha256 is not None
