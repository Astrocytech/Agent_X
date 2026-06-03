import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from agentx_evolve.context.cli import (
    _find_repo_root, _load_json, _write_output,
    main,
)


class TestFindRepoRoot:
    def test_finds_git_dir(self, tmp_path, monkeypatch):
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)
        repo = _find_repo_root()
        assert repo == tmp_path

    def test_finds_pyproject_toml(self, tmp_path, monkeypatch):
        (tmp_path / "pyproject.toml").write_text("")
        monkeypatch.chdir(tmp_path)
        repo = _find_repo_root()
        assert repo == tmp_path

    def test_falls_back_to_cwd(self):
        root = _find_repo_root()
        assert root is not None


class TestLoadJson:
    def test_loads_valid_json(self):
        data = {"key": "value"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = _load_json(path)
            assert result == data
        finally:
            Path(path).unlink()

    def test_exits_on_missing_file(self):
        try:
            _load_json("/nonexistent/file.json")
            assert False, "Expected SystemExit"
        except SystemExit:
            pass

    def test_exits_on_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not json")
            path = f.name
        try:
            try:
                _load_json(path)
                assert False, "Expected SystemExit"
            except SystemExit:
                pass
        finally:
            Path(path).unlink()


class TestWriteOutput:
    def test_writes_to_file(self, tmp_path):
        out_path = tmp_path / "out.json"
        _write_output({"a": 1}, str(out_path))
        assert out_path.exists()
        assert json.loads(out_path.read_text()) == {"a": 1}

    def test_prints_to_stdout(self, capsys):
        _write_output({"b": 2}, None)
        captured = capsys.readouterr()
        assert "b" in captured.out


class TestMain:
    def test_no_args_exits(self):
        try:
            main([])
            assert False, "Expected SystemExit"
        except SystemExit:
            pass

    def test_validate_no_file_exits(self):
        try:
            main(["validate", "--file", "/nonexistent.json"])
            assert False, "Expected SystemExit"
        except SystemExit:
            pass

    def test_inspect_default_target(self):
        result = main(["inspect"])
        assert result == 0
