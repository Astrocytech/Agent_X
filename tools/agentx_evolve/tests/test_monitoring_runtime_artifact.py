import pytest
from pathlib import Path
from agentx_evolve.monitoring.monitoring_utils import write_runtime_artifact, read_runtime_artifact


class TestRuntimeArtifact:
    def test_write_and_read_artifact(self, tmp_path: Path):
        data = {"key": "value", "number": 42}
        path = tmp_path / "runtime" / "artifact.json"
        result = write_runtime_artifact(path, data)
        assert result == path
        assert path.exists()
        loaded = read_runtime_artifact(path)
        assert loaded == data

    def test_read_nonexistent_artifact(self, tmp_path: Path):
        path = tmp_path / "nonexistent.json"
        result = read_runtime_artifact(path)
        assert result is None

    def test_write_multiple_artifacts(self, tmp_path: Path):
        paths = []
        for i in range(3):
            p = tmp_path / f"artifact_{i}.json"
            paths.append(p)
            write_runtime_artifact(p, {"index": i})
        for i, p in enumerate(paths):
            assert p.exists()
            assert read_runtime_artifact(p) == {"index": i}

    def test_write_artifact_overwrites(self, tmp_path: Path):
        path = tmp_path / "overwrite.json"
        write_runtime_artifact(path, {"version": 1})
        write_runtime_artifact(path, {"version": 2})
        assert read_runtime_artifact(path) == {"version": 2}

    def test_write_artifact_creates_parent_dirs(self, tmp_path: Path):
        path = tmp_path / "a" / "b" / "c" / "deep.json"
        write_runtime_artifact(path, {"deep": True})
        assert path.exists()
        assert read_runtime_artifact(path) == {"deep": True}
