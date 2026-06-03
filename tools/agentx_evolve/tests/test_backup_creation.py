from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from agentx_evolve.backup.backup_models import (
    BackupManifest,
    BackupPolicy,
    BackupSnapshotRecord,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
)
from agentx_evolve.backup.snapshot_creator import (
    _orig_create_backup_snapshot as create_backup_snapshot,
)


class TestBackupCreation:
    def test_create_backup_snapshot_returns_manifest(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "staging").mkdir(parents=True)
        (tmp_path / ".agentx-init" / "backups" / "snapshots").mkdir(parents=True)
        policy = BackupPolicy()
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            repo_root=str(tmp_path),
        )
        result = create_backup_snapshot(manifest, policy=policy, repo_root=tmp_path)
        assert result.backup_id == manifest.backup_id
        assert result.status == "STAGED"

    def test_create_backup_snapshot_sets_snapshot_record(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "staging").mkdir(parents=True)
        (tmp_path / ".agentx-init" / "backups" / "snapshots").mkdir(parents=True)
        policy = BackupPolicy()
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            repo_root=str(tmp_path),
        )
        result = create_backup_snapshot(manifest, policy=policy, repo_root=tmp_path)
        assert result.snapshot_record is not None
        assert isinstance(result.snapshot_record, BackupSnapshotRecord)
        assert result.snapshot_record.backup_id == result.backup_id

    def test_create_backup_snapshot_includes_file_records(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "staging").mkdir(parents=True)
        (tmp_path / ".agentx-init" / "backups" / "snapshots").mkdir(parents=True)
        (tmp_path / "test_file.txt").write_text("hello")
        policy = BackupPolicy()
        source_root = tmp_path
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            repo_root=str(tmp_path),
            backup_scope=["SOURCE"],
        )
        result = create_backup_snapshot(manifest, source_root=source_root, policy=policy, repo_root=tmp_path)
        file_records = [r for r in result.file_records if r.included]
        assert len(file_records) >= 1
        rel_paths = [r.relative_path for r in file_records]
        assert "test_file.txt" in rel_paths

    def test_create_backup_snapshot_respects_exclusions(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "staging").mkdir(parents=True)
        (tmp_path / ".agentx-init" / "backups" / "snapshots").mkdir(parents=True)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("repo config")
        policy = BackupPolicy(excluded_paths=[".git"])
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            repo_root=str(tmp_path),
        )
        result = create_backup_snapshot(manifest, policy=policy, repo_root=tmp_path)
        git_excluded = [r for r in result.excluded_records if ".git" in r.relative_path]
        assert len(git_excluded) >= 1

    def test_serializes_to_dict(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "staging").mkdir(parents=True)
        (tmp_path / ".agentx-init" / "backups" / "snapshots").mkdir(parents=True)
        policy = BackupPolicy()
        manifest = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            repo_root=str(tmp_path),
        )
        result = create_backup_snapshot(manifest, policy=policy, repo_root=tmp_path)
        d = to_dict(result)
        assert isinstance(d, dict)
        assert d["backup_id"] == manifest.backup_id
