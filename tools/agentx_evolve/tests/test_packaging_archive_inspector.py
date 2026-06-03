import pytest
from pathlib import Path
from agentx_evolve.packaging.archive_inspector import inspect_archive


class TestInspectArchive:
    def test_nonexistent_path(self):
        result = inspect_archive("/nonexistent/archive.tar.gz")
        assert result["exists"] is False
        assert len(result["errors"]) > 0

    def test_unknown_format(self, tmp_path: Path):
        f = tmp_path / "file.xyz"
        f.write_text("hello")
        result = inspect_archive(f)
        assert result["exists"] is True
        assert "Unknown archive format" in str(result["warnings"])
