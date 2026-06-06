import pytest
import tempfile
import json
from pathlib import Path

from agentx_evolve.docs_sync.evidence_writer import (
    write_scan_report, write_drift_report, write_link_report,
    write_staleness_report, write_sync_plan, write_sync_result,
    write_evidence_manifest, write_command_result, write_completion_record,
    sha256_evidence_file, write_json_atomic,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentScanReport, DocumentDriftRecord, DocumentLinkRecord,
    DocumentStalenessRecord, DocumentSyncPlan, DocumentSyncResult,
    DocumentationSyncEvidenceManifest, DocumentationSyncCommandResult,
    DocumentationSyncCompletionRecord,
)


class TestEvidence:
    def test_evidence_manifest_written(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root=str(root))
            write_scan_report(root, scan)

            manifest = DocumentationSyncEvidenceManifest(
                created_at="now",
                scan_report_path=".agentx-init/docs_sync/documentation_scan_result.json",
            )
            result = write_evidence_manifest(root, manifest)
            assert result["status"] == "written"

            manifest_path = root / ".agentx-init/docs_sync/documentation_evidence_manifest.json"
            assert manifest_path.exists()

    def test_evidence_manifest_contains_sha256_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = DocumentationSyncEvidenceManifest(
                created_at="now",
                evidence_file_hashes=[{"path": "test.json", "sha256": "abc123"}],
            )
            write_evidence_manifest(root, manifest)
            path = root / ".agentx-init/docs_sync/documentation_evidence_manifest.json"
            data = json.loads(path.read_text())
            assert "evidence_file_hashes" in data

    def test_review_report_written(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            report_path = root / ".agentx-init/docs_sync/documentation_review_report.json"
            report_path.parent.mkdir(parents=True)
            payload = {"final_verdict": "PASS"}
            write_json_atomic(report_path, payload)
            assert report_path.exists()
            data = json.loads(report_path.read_text())
            assert data["final_verdict"] == "PASS"

    def test_runtime_artifacts_written_under_docs_sync_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root=str(root))
            write_scan_report(root, scan)
            path = root / ".agentx-init/docs_sync/documentation_scan_result.json"
            assert path.exists()

    def test_write_drift_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            drifts = [
                DocumentDriftRecord(
                    drift_id="d1", created_at="now",
                    document_id="doc1", path="doc.md",
                    drift_type="MISSING_SCHEMA", status="DRIFTED",
                ),
            ]
            result = write_drift_report(root, drifts)
            assert result["status"] == "written"

    def test_write_link_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            links = [
                DocumentLinkRecord(link_id="l1", source_path="s.md", target="t.md"),
            ]
            result = write_link_report(root, links)
            assert result["status"] == "written"

    def test_write_staleness_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stales = [
                DocumentStalenessRecord(
                    staleness_id="s1", document_id="d1", path="p.md",
                ),
            ]
            result = write_staleness_report(root, stales)
            assert result["status"] == "written"

    def test_sha256_evidence_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.txt"
            path.write_text("hello")
            h = sha256_evidence_file(path)
            assert len(h) == 64
            assert isinstance(h, str)
