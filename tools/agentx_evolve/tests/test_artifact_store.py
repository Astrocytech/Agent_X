import os
import stat
import tempfile
from pathlib import Path

import pytest

from agentx_evolve.artifacts.artifact_store import (
    ArtifactEscapeError,
    ArtifactOverwriteError,
    ArtifactPathTraversalError,
    MvpArtifactStore,
)


class TestMvpArtifactStore:
    def setup_method(self):
        self._tmp = Path(tempfile.mkdtemp(prefix="test_art_"))
        self.store = MvpArtifactStore(self._tmp)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_write_and_read_artifact(self):
        rec = self.store.write("run-1", "action-1", "test.json", {"key": "value"})
        assert rec["hash"]
        content = self.store.read(rec["path"])
        assert content is not None
        assert '"key": "value"' in content

    def test_hash_is_deterministic(self):
        rec1 = self.store.write("run-1", "action-1", "data_a.txt", "hello")
        rec2 = self.store.write("run-1", "action-1", "data_b.txt", "hello")
        assert rec1["hash"] == rec2["hash"]

    def test_write_denies_existing_artifact_by_default(self):
        self.store.write("run-1", "action-1", "same.json", {"x": 1})
        with pytest.raises(ArtifactOverwriteError):
            self.store.write("run-1", "action-1", "same.json", {"y": 2})

    def test_write_versions_existing_artifact_when_requested(self):
        r1 = self.store.write("run-1", "action-1", "ver.json", {"x": 1}, overwrite_policy="deny")
        r2 = self.store.write("run-1", "action-1", "ver.json", {"x": 2}, overwrite_policy="version")
        assert r2["name"] != r1["name"]

    def test_original_content_preserved_after_versioned_write(self):
        r1 = self.store.write("run-1", "action-1", "keep.json", {"orig": "data"}, overwrite_policy="deny")
        r2 = self.store.write("run-1", "action-1", "keep.json", {"new": "data"}, overwrite_policy="version")
        r1_content = self.store.read(r1["path"])
        r2_content = self.store.read(r2["path"])
        assert r1_content is not None
        assert r2_content is not None
        assert '"orig": "data"' in r1_content
        assert '"new": "data"' in r2_content

    def test_validate_ref_fails_for_wrong_hash(self):
        rec = self.store.write("run-1", "action-1", "hash_check.json", {"data": 1})
        ref = {"path": rec["path"], "hash": "0" * 64}
        assert not self.store.validate_ref(ref)

    def test_validate_ref_fails_for_missing_file(self):
        ref = {"path": str(self._tmp / "nonexistent.json"), "hash": "0" * 64}
        assert not self.store.validate_ref(ref)

    def test_failed_artifact_retained(self):
        rec = self.store.retain_failed("run-1", "action-1", "crash.txt", {"error": "test"})
        assert rec["hash"]
        content = self.store.read(rec["path"])
        assert content is not None
        assert "failed_" in rec["name"]

    def test_artifact_name_rejects_path_traversal(self):
        with pytest.raises(ArtifactPathTraversalError):
            self.store.write("run-1", "action-1", "../../etc/passwd", "data")

    def test_artifact_write_rejects_workspace_escape(self):
        with pytest.raises(ArtifactEscapeError):
            self.store.write("run-1", "../../../tmp", "file.txt", "data")

    def test_artifact_write_rejects_symlink_escape(self):
        outside = Path(tempfile.mkdtemp(prefix="outside_"))
        link_path = self._tmp / "escape_link"
        os.symlink(str(outside), str(link_path))
        with pytest.raises(ArtifactEscapeError):
            self.store.write("run-1", "../escape_link", "file.txt", "data")

    def test_classify_artifact(self):
        rec = self.store.write("run-1", "action-1", "report.json", {}, artifact_type="report")
        typ = self.store.classify(rec["path"])
        assert typ == "report"

    def test_export_replay_manifest(self):
        self.store.write("run-1", "action-1", "a.json", {"x": 1})
        self.store.write("run-1", "action-2", "b.json", {"y": 2})
        manifest = self.store.export_replay_manifest("run-1")
        assert len(manifest) == 2
