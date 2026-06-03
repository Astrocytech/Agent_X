from __future__ import annotations

from pathlib import Path

import pytest

from agentx_evolve.backup.backup_models import (
    BACKUP_STATUS_CREATED,
    GIT_STATUS_CLEAN,
    GIT_STATUS_UNKNOWN,
    SCHEMA_VERSION,
    SOURCE_COMPONENT,
    BackupManifest,
    new_id,
    to_dict,
    utc_now_iso,
)


class TestManifestSchema:
    def test_manifest_has_required_fields(self):
        m = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            repo_root="/tmp/test",
        )
        assert m.schema_version == SCHEMA_VERSION
        assert m.schema_id == "backup_manifest.schema.json"
        assert m.backup_id != ""
        assert m.created_at != ""
        assert m.source_component == SOURCE_COMPONENT

    def test_manifest_default_status(self):
        m = BackupManifest()
        assert m.status == BACKUP_STATUS_CREATED

    def test_manifest_serializes_to_dict(self):
        m = BackupManifest(
            backup_id=new_id("bck"),
            created_at=utc_now_iso(),
            repo_root="/tmp",
            git_commit="abc123",
            git_branch="main",
            git_status_summary=GIT_STATUS_CLEAN,
        )
        d = to_dict(m)
        assert d["backup_id"] == m.backup_id
        assert d["git_commit"] == "abc123"
        assert d["git_status_summary"] == GIT_STATUS_CLEAN

    def test_manifest_roundtrip_through_dict(self):
        m = BackupManifest(
            backup_id="bck_roundtrip",
            created_at=utc_now_iso(),
            repo_root="/tmp",
            backup_scope=["SOURCE", "CONFIG"],
        )
        d = to_dict(m)
        restored = BackupManifest(**d)
        assert restored.backup_id == "bck_roundtrip"
        assert restored.backup_scope == ["SOURCE", "CONFIG"]

    def test_manifest_handles_scope_list(self):
        m = BackupManifest(backup_scope=["RUNTIME", "EVIDENCE"])
        assert len(m.backup_scope) == 2

    def test_manifest_handles_empty_file_records(self):
        m = BackupManifest()
        assert m.file_records == []
        assert m.excluded_records == []

    def test_manifest_rejects_invalid_status(self):
        m = BackupManifest(status="INVALID_STATUS")
        assert m.status not in ("CREATED", "VERIFIED", "FAILED")
