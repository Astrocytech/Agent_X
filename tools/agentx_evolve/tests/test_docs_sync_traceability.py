import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.doc_traceability import (
    build_docs_sync_traceability_matrix,
    validate_docs_sync_traceability_matrix,
    write_docs_sync_traceability_matrix,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentRecord, DocumentScanReport,
)


class TestTraceability:
    def test_traceability_matrix_written(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        matrix = build_docs_sync_traceability_matrix(Path("/tmp"), scan)
        assert "entries" in matrix
        assert "summary" in matrix
        assert matrix["component_id"] == "AGENTX_DOCUMENTATION_SYNCHRONIZATION"

    def test_validate_traceability_matrix_valid(self):
        matrix = {
            "entries": [
                {"requirement_id": "R1", "requirement_text": "test",
                 "implementation_file": "f1", "test_file": "t1",
                 "evidence_artifact": "e1", "status": "PASS"},
            ],
            "summary": {"PASS": 1, "NOT_CHECKED": 0, "total": 1},
        }
        valid, errors = validate_docs_sync_traceability_matrix(matrix)
        assert valid is True

    def test_validate_traceability_matrix_missing_entries(self):
        matrix = {}
        valid, errors = validate_docs_sync_traceability_matrix(matrix)
        assert valid is False

    def test_write_traceability_matrix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            matrix = build_docs_sync_traceability_matrix(root, DocumentScanReport(
                scan_id="s1", created_at="now", repo_root=str(root),
            ))
            result = write_docs_sync_traceability_matrix(root, matrix)
            assert result["status"] == "written"
            path = root / ".agentx-init/docs_sync/documentation_sync_traceability_matrix.json"
            assert path.exists()

    def test_traceability_matrix_includes_requirements(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        matrix = build_docs_sync_traceability_matrix(Path("/tmp"), scan)
        assert len(matrix["entries"]) >= 9
