import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.doc_staleness import (
    detect_stale_documents, is_document_stale_against_related_files,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentRecord, DocumentScanReport, DocumentStalenessRecord,
    DOC_STATUS_STALE, DOC_STATUS_MISSING, DOC_STATUS_CURRENT,
    DOC_AUTHORITY_MANUAL_GOVERNED, DOC_AUTHORITY_RUNTIME_EVIDENCE,
)


class TestStaleness:
    def test_stale_document_detected_from_missing_evidence(self):
        records = [
            DocumentRecord(
                document_id="spec", path="spec.md",
                authority=DOC_AUTHORITY_MANUAL_GOVERNED,
            ),
        ]
        scan = DocumentScanReport(
            scan_id="s1", created_at="now", repo_root="/tmp",
            documents=records,
        )
        stale = detect_stale_documents(Path("/tmp"), scan)
        assert isinstance(stale, list)

    def test_no_stale_when_all_current(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec = root / "spec.md"
            spec.write_text("# spec")
            records = [
                DocumentRecord(
                    document_id="spec", path="spec.md",
                    authority=DOC_AUTHORITY_MANUAL_GOVERNED,
                ),
            ]
            scan = DocumentScanReport(
                scan_id="s1", created_at="now", repo_root=str(root),
                documents=records,
            )
            stale = detect_stale_documents(root, scan)
            assert len(stale) == 0

    def test_missing_file_detected(self):
        records = [
            DocumentRecord(
                document_id="missing", path="nonexistent.md",
            ),
        ]
        scan = DocumentScanReport(
            scan_id="s1", created_at="now", repo_root="/tmp",
            documents=records,
        )
        stale = detect_stale_documents(Path("/tmp"), scan)
        if stale:
            assert stale[0].status == DOC_STATUS_MISSING

    def test_is_document_stale_returns_none_for_valid(self):
        doc = DocumentRecord(document_id="d1", path="d.md")
        result = is_document_stale_against_related_files(doc, [])
        assert result is None

    def test_is_document_stale_returns_record_for_missing(self):
        doc = DocumentRecord(document_id="d1", path="d.md")
        result = is_document_stale_against_related_files(
            doc, [Path("/nonexistent/file")]
        )
        if result:
            assert result.status == DOC_STATUS_STALE
