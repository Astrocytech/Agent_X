import pytest
import tempfile
import os
from pathlib import Path

from agentx_evolve.docs_sync.doc_scanner import scan_documentation, scan_document_file
from agentx_evolve.docs_sync.doc_models import DocumentScanReport


@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs").mkdir()
        (root / "docs" / "readme.md").write_text("# Readme\n\ncontent")
        (root / "docs" / "contract.md").write_text("document_id: TEST\n\nContract content")
        (root / "docs" / "spec.md").write_text("# Spec\n\nSpec content")
        (root / "excluded_dir").mkdir()
        (root / "excluded_dir" / "ignored.md").write_text("ignored")
        yield root


class TestScanner:
    def test_scanner_finds_markdown_documents(self, temp_repo):
        report = scan_documentation(temp_repo)
        assert isinstance(report, DocumentScanReport)
        assert len(report.documents) >= 2
        paths = [d.path for d in report.documents]
        assert any("readme.md" in p for p in paths)

    def test_scanner_skips_excluded_paths(self, temp_repo):
        report = scan_documentation(temp_repo, exclude_paths=["excluded_dir"])
        paths = [d.path for d in report.documents]
        assert all("excluded_dir" not in p for p in paths)

    def test_scanner_does_not_mutate_files(self, temp_repo):
        original_contents = {}
        for f in temp_repo.rglob("*"):
            if f.is_file():
                original_contents[str(f)] = f.read_bytes()

        scan_documentation(temp_repo)

        for f in temp_repo.rglob("*"):
            if f.is_file():
                assert f.read_bytes() == original_contents[str(f)], f"file mutated: {f}"

    def test_scanner_returns_scan_id(self, temp_repo):
        report = scan_documentation(temp_repo)
        assert report.scan_id.startswith("scan_")
        assert report.created_at is not None

    def test_scanner_detects_python_files(self, temp_repo):
        (temp_repo / "module.py").write_text("# test module")
        report = scan_documentation(temp_repo)
        paths = [d.path for d in report.documents]
        assert any("module.py" in p for p in paths)

    def test_scanner_handles_empty_repo(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            report = scan_documentation(root)
            assert isinstance(report, DocumentScanReport)
            assert len(report.documents) == 0
