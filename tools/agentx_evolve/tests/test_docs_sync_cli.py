import os
from pathlib import Path
from unittest.mock import patch
from agentx_evolve.docs_sync.cli import (
    _find_repo_root, main,
)


class TestFindRepoRoot:
    def test_finds_git_dir(self, tmp_path, monkeypatch):
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)
        root = _find_repo_root()
        assert root == tmp_path

    def test_finds_pyproject_toml(self, tmp_path, monkeypatch):
        (tmp_path / "pyproject.toml").write_text("")
        monkeypatch.chdir(tmp_path)
        root = _find_repo_root()
        assert root == tmp_path

    def test_falls_back_to_cwd(self):
        root = _find_repo_root()
        assert root is not None


class TestMain:
    def test_no_args_exits(self):
        try:
            main([])
            assert False, "Expected SystemExit"
        except SystemExit:
            pass

    def test_invalid_command(self):
        try:
            main(["invalid"])
            assert False, "Expected SystemExit"
        except SystemExit:
            pass

    def test_scan(self):
        result = main(["scan"])
        assert result == 0

    def test_validate(self):
        result = main(["validate"])
        assert result == 0

    def test_plan(self):
        result = main(["plan"])
        assert result == 0

    def test_sync_default(self):
        result = main(["sync"])
        assert result == 0
