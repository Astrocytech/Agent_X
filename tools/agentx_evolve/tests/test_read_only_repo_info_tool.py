from __future__ import annotations

import pytest
from pathlib import Path
from agentx_evolve.tools.read_only_repo_info_tool import ReadOnlyRepoInfoTool


class TestReadOnlyRepoInfoTool:
    def setup_method(self):
        self.tool = ReadOnlyRepoInfoTool(repo_root="/tmp")

    def test_dot_path_returns_info(self):
        result = self.tool.get_info(".")
        assert result["exists"] is True
        assert result["is_dir"] is True
        assert result["name"] == "tmp"

    def test_path_traversal_absolute_blocked(self):
        result = self.tool.get_info("/etc")
        assert result["status"] == "DENIED"

    def test_path_traversal_dotdot_blocked(self):
        result = self.tool.get_info("../../etc")
        assert result["status"] == "DENIED"

    def test_nonexistent_path_returns_denied(self):
        result = self.tool.get_info("nonexistent_dir_xyz")
        assert result["status"] == "DENIED"

    def test_valid_subdir_returns_info(self):
        result = self.tool.get_info(".")
        assert result["is_dir"] is True

    def test_entries_listed_for_directory(self):
        result = self.tool.get_info(".")
        assert "entries" in result
