import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.runtime.artifacts import ArtifactWriter
from agentx_evolve.security.sandbox_policy import default_sandbox_policy, is_runtime_path


class TestRuntimeArtifactBoundary:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.repo_root = self.tmpdir / "repo"
        self.repo_root.mkdir()
        self.run_dir = self.repo_root / ".agentx-init" / "runs" / "test-run"
        self.run_dir.mkdir(parents=True)
        self.writer = ArtifactWriter(self.run_dir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_runtime_artifacts_write_to_approved_locations_only(self):
        path = self.writer.atomic_write("test_artifact.json", {"key": "value"})
        assert path.exists()
        assert str(path).startswith(str(self.run_dir))

    def test_source_files_are_not_written_to_runtime_paths(self):
        policy = default_sandbox_policy(self.repo_root)
        runtime_path = self.repo_root / ".agentx-init" / "runs" / "data.json"
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        runtime_path.write_text("{}")
        assert is_runtime_path(runtime_path, self.repo_root, policy)

    def test_runtime_artifacts_are_schema_valid(self):
        path = self.writer.atomic_write("metadata.json", {
            "schema_version": "1.0",
            "run_id": "run-1",
            "status": "COMPLETED",
        })
        data = json.loads(path.read_text())
        assert "schema_version" in data
        assert data["schema_version"] == "1.0"
        assert data["status"] == "COMPLETED"
