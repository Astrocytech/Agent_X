import json
import pathlib

from agentx_evolve.runtime.artifacts import ArtifactWriter, make_placeholder
from agentx_evolve.runtime.session import RunSession


class TestArtifactWriter:
    def test_atomic_write_dict(self, tmp_path):
        writer = ArtifactWriter(tmp_path)
        data = {"hello": "world", "nested": {"a": 1}}
        path = writer.atomic_write("test.json", data)
        assert path.exists()
        assert json.loads(path.read_text()) == data

    def test_atomic_write_string(self, tmp_path):
        writer = ArtifactWriter(tmp_path)
        path = writer.atomic_write("output.txt", "plain text")
        assert path.exists()
        assert path.read_text() == "plain text"

    def test_atomic_write_list(self, tmp_path):
        writer = ArtifactWriter(tmp_path)
        path = writer.atomic_write("list.json", [1, 2, 3])
        assert path.exists()
        assert json.loads(path.read_text()) == [1, 2, 3]

    def test_writes_metadata(self, tmp_path):
        run = RunSession("test", run_root=str(tmp_path))
        run.ensure_run_dir()
        writer = ArtifactWriter(run.run_dir)
        path = writer.write_metadata(run)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["command"] == "test"
        assert data["run_id"] == run.run_id

    def test_writes_config(self, tmp_path):
        run = RunSession("chat", run_root=str(tmp_path))
        run.ensure_run_dir()
        writer = ArtifactWriter(run.run_dir)
        config = {"provider": "mock", "model": "mock/deterministic"}
        path = writer.write_config(config)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["provider"] == "mock"

    def test_placeholder_not_applicable(self):
        p = make_placeholder("chat mode does not produce patches")
        assert p["schema_version"] == "agentx.artifact_placeholder.v1"
        assert p["status"] == "NOT_APPLICABLE"
        assert "chat" in p["reason"]

    def test_writes_structured_plan_placeholder(self, tmp_path):
        run = RunSession("chat", run_root=str(tmp_path))
        run.ensure_run_dir()
        writer = ArtifactWriter(run.run_dir)
        path = writer.write_structured_plan(None)
        data = json.loads(path.read_text())
        assert data["schema_version"] == "agentx.artifact_placeholder.v1"

    def test_multiple_artifacts(self, tmp_path):
        writer = ArtifactWriter(tmp_path)
        writer.atomic_write("a.json", {"n": 1})
        writer.atomic_write("b.json", {"n": 2})
        writer.atomic_write("c.json", {"n": 3})
        assert (tmp_path / "a.json").exists()
        assert (tmp_path / "b.json").exists()
        assert (tmp_path / "c.json").exists()

    def test_ensure_dir_creates(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c"
        writer = ArtifactWriter(deep)
        writer.ensure_dir()
        assert deep.exists()
