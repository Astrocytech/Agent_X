import json
from pathlib import Path

from tools.agentx_evolve.final_acceptance.artifact_writer import (
    runtime_root, ensure_runtime_root, atomic_write_json,
    write_json_artifact, is_within_runtime_root, reject_path_traversal,
)


class TestRuntimeRoot:
    def test_returns_correct_path(self, tmp_path: Path):
        root = runtime_root(tmp_path)
        assert root == tmp_path / ".agentx-init" / "final_acceptance"

    def test_does_not_exist_by_default(self, tmp_path: Path):
        assert not runtime_root(tmp_path).exists()


class TestEnsureRuntimeRoot:
    def test_creates_directory(self, tmp_path: Path):
        path = ensure_runtime_root(tmp_path)
        assert path.exists()
        assert path.is_dir()

    def test_idempotent(self, tmp_path: Path):
        p1 = ensure_runtime_root(tmp_path)
        p2 = ensure_runtime_root(tmp_path)
        assert p1 == p2
        assert p1.exists()

    def test_nested_repo(self, tmp_path: Path):
        nested = tmp_path / "deep" / "repo"
        path = ensure_runtime_root(nested)
        assert path.exists()


class TestAtomicWriteJson:
    def test_writes_json_file(self, tmp_path: Path):
        path = tmp_path / "test.json"
        atomic_write_json(path, {"key": "value"})
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["key"] == "value"

    def test_overwrites_existing(self, tmp_path: Path):
        path = tmp_path / "test.json"
        atomic_write_json(path, {"v": 1})
        atomic_write_json(path, {"v": 2})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["v"] == 2

    def test_empty_dict(self, tmp_path: Path):
        path = tmp_path / "empty.json"
        atomic_write_json(path, {})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data == {}

    def test_creates_parent_dirs(self, tmp_path: Path):
        path = tmp_path / "a" / "b" / "c" / "nested.json"
        atomic_write_json(path, {"x": 1})
        assert path.exists()

    def test_sort_keys(self, tmp_path: Path):
        path = tmp_path / "sorted.json"
        atomic_write_json(path, {"b": 2, "a": 1})
        content = path.read_text(encoding="utf-8")
        assert '"a"' in content
        assert '"b"' in content

    def test_nested_dict(self, tmp_path: Path):
        path = tmp_path / "nested.json"
        atomic_write_json(path, {"outer": {"inner": [1, 2, 3]}})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["outer"]["inner"] == [1, 2, 3]

    def test_list_top_level(self, tmp_path: Path):
        path = tmp_path / "list.json"
        atomic_write_json(path, {"items": [1, 2, 3]})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["items"] == [1, 2, 3]


class TestWriteJsonArtifact:
    def test_writes_under_runtime_root(self, tmp_path: Path):
        path = write_json_artifact(tmp_path, "test_artifact.json", {"a": 1})
        assert path.exists()
        assert ".agentx-init" in str(path)
        assert path.name == "test_artifact.json"

    def test_creates_runtime_root(self, tmp_path: Path):
        write_json_artifact(tmp_path, "x.json", {"x": 1})
        assert runtime_root(tmp_path).exists()

    def test_readable_content(self, tmp_path: Path):
        write_json_artifact(tmp_path, "data.json", {"msg": "hello"})
        content = (runtime_root(tmp_path) / "data.json").read_text(encoding="utf-8")
        assert "hello" in content

    def test_multiple_artifacts(self, tmp_path: Path):
        write_json_artifact(tmp_path, "a.json", {"i": 1})
        write_json_artifact(tmp_path, "b.json", {"i": 2})
        root = runtime_root(tmp_path)
        assert (root / "a.json").exists()
        assert (root / "b.json").exists()


class TestIsWithinRuntimeRoot:
    def test_path_inside_root(self, tmp_path: Path):
        inside = runtime_root(tmp_path) / "artifact.json"
        assert is_within_runtime_root(tmp_path, inside)

    def test_path_outside_root(self, tmp_path: Path):
        outside = tmp_path / "outside.json"
        assert not is_within_runtime_root(tmp_path, outside)

    def test_runtime_root_itself(self, tmp_path: Path):
        rt = runtime_root(tmp_path)
        assert is_within_runtime_root(tmp_path, rt)

    def test_deeply_nested_inside(self, tmp_path: Path):
        deep = runtime_root(tmp_path) / "a" / "b" / "c" / "file.json"
        assert is_within_runtime_root(tmp_path, deep)

    def test_symlink_outside(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        outside = tmp_path / "outside_link"
        try:
            outside.symlink_to(tmp_path / "..")
        except OSError:
            pass


class TestRejectPathTraversal:
    def test_allowed_path(self, tmp_path: Path):
        inside = runtime_root(tmp_path) / "artifact.json"
        reject_path_traversal(tmp_path, inside)

    def test_rejects_outside_path(self, tmp_path: Path):
        outside = tmp_path / "outside.json"
        try:
            reject_path_traversal(tmp_path, outside)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_rejects_system_path(self, tmp_path: Path):
        try:
            reject_path_traversal(tmp_path, Path("/etc/passwd"))
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
