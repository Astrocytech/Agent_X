import pytest
from pathlib import Path
from agentx_evolve.docs_sync.doc_models import (
    DocumentRecord, DocumentScanReport, DocumentDriftRecord,
    DocumentSyncOperation, DocumentSyncPlan, DocumentSyncResult,
    DocumentLinkRecord, DocumentStalenessRecord,
    DocumentationSyncEvidenceManifest, DocumentationSyncReviewReport,
    GeneratedDocumentSection, GeneratedSectionRegistry,
    DocumentationSyncCommandResult, DocumentationSyncLockRecord,
    DocumentationSyncTraceabilityMatrix, DocumentationSyncDeviation,
    DocumentationSyncControllerResult, DocumentationSyncCompletionRecord,
    DOC_AUTHORITY_MANUAL_GOVERNED, DOC_TYPE_CONTRACT,
    DOC_OP_BLOCKED_MANUAL_DOC, DOC_STATUS_CURRENT,
    utc_now_iso, new_id, sha256_file, sha256_bytes, to_dict, is_valid_status,
)


class TestDocumentRecord:
    def test_document_record_instantiates(self):
        rec = DocumentRecord(
            document_id="test-doc-1",
            path="docs/test.md",
            document_type=DOC_TYPE_CONTRACT,
            authority=DOC_AUTHORITY_MANUAL_GOVERNED,
        )
        assert rec.document_id == "test-doc-1"
        assert rec.path == "docs/test.md"
        assert rec.document_type == DOC_TYPE_CONTRACT
        assert rec.authority == DOC_AUTHORITY_MANUAL_GOVERNED
        assert rec.schema_version == "1.0"
        assert rec.schema_id == "documentation_record.schema.json"
        assert rec.protected is False
        assert rec.warnings == []
        assert rec.errors == []

    def test_document_record_to_dict(self):
        rec = DocumentRecord(document_id="d1", path="p1")
        d = to_dict(rec)
        assert d["document_id"] == "d1"
        assert d["path"] == "p1"


class TestScanReport:
    def test_scan_report_instantiates(self):
        report = DocumentScanReport(
            scan_id="scan-1",
            created_at="2026-01-01T00:00:00Z",
            repo_root="/tmp",
        )
        assert report.scan_id == "scan-1"
        assert report.repo_root == "/tmp"
        assert report.documents == []


class TestDriftRecord:
    def test_drift_record_instantiates(self):
        rec = DocumentDriftRecord(
            drift_id="drift-1",
            created_at="2026-01-01T00:00:00Z",
            document_id="doc-1",
            path="path/to/doc",
            drift_type="MISSING_SCHEMA",
            status="DRIFTED",
        )
        assert rec.drift_id == "drift-1"
        assert rec.severity == "MEDIUM"


class TestSyncOperation:
    def test_document_sync_operation_instantiates(self):
        op = DocumentSyncOperation(
            operation_id="op-1",
            operation_type=DOC_OP_BLOCKED_MANUAL_DOC,
            target_path="/path/to/doc",
            target_authority=DOC_AUTHORITY_MANUAL_GOVERNED,
            allowed_to_apply=False,
            reason="protected",
        )
        assert op.operation_id == "op-1"
        assert op.allowed_to_apply is False


class TestSyncPlan:
    def test_document_sync_plan_instantiates(self):
        plan = DocumentSyncPlan(
            plan_id="plan-1",
            created_at="2026-01-01T00:00:00Z",
            source_scan_id="scan-1",
        )
        assert plan.plan_id == "plan-1"
        assert plan.operations == []


class TestSyncResult:
    def test_document_sync_result_instantiates(self):
        result = DocumentSyncResult(
            result_id="result-1",
            created_at="2026-01-01T00:00:00Z",
            plan_id="plan-1",
        )
        assert result.result_id == "result-1"


class TestLinkRecord:
    def test_document_link_record_instantiates(self):
        rec = DocumentLinkRecord(
            link_id="link-1",
            source_path="src.md",
            target="tgt.md",
        )
        assert rec.link_id == "link-1"


class TestStalenessRecord:
    def test_document_staleness_record_instantiates(self):
        rec = DocumentStalenessRecord(
            staleness_id="stale-1",
            document_id="doc-1",
            path="path/doc.md",
        )
        assert rec.staleness_id == "stale-1"


class TestEvidenceManifest:
    def test_evidence_manifest_instantiates(self):
        m = DocumentationSyncEvidenceManifest(created_at="now")
        assert m.component_id == "AGENTX_DOCUMENTATION_SYNCHRONIZATION"


class TestReviewReport:
    def test_review_report_instantiates(self):
        r = DocumentationSyncReviewReport(created_at="now")
        assert r.final_verdict == "NOT_RUN"


class TestGeneratedSection:
    def test_generated_document_section_instantiates(self):
        s = GeneratedDocumentSection(
            section_id="sec-1",
            target_path="docs/readme.md",
            start_marker="<!-- AGENTX-GENERATED-SECTION:START sec-1 -->",
            end_marker="<!-- AGENTX-GENERATED-SECTION:END sec-1 -->",
        )
        assert s.section_id == "sec-1"


class TestGeneratedSectionRegistry:
    def test_generated_section_registry_instantiates(self):
        reg = GeneratedSectionRegistry(
            registry_id="reg-1",
            created_at="now",
        )
        assert reg.registry_id == "reg-1"


class TestCommandResult:
    def test_command_result_instantiates(self):
        cmd = DocumentationSyncCommandResult(
            command_id="cmd-1",
            name="compileall",
            command="python -m compileall .",
            started_at="start",
            ended_at="end",
            exit_code=0,
        )
        assert cmd.exit_code == 0
        assert cmd.status == "PASS"


class TestLockRecord:
    def test_lock_record_instantiates(self):
        lock = DocumentationSyncLockRecord(
            lock_id="lock-1",
            created_at="now",
        )
        assert lock.lock_id == "lock-1"


class TestTraceabilityMatrix:
    def test_traceability_matrix_instantiates(self):
        tm = DocumentationSyncTraceabilityMatrix(
            matrix_id="tm-1",
            created_at="now",
        )
        assert tm.matrix_id == "tm-1"


class TestDeviation:
    def test_deviation_instantiates(self):
        dev = DocumentationSyncDeviation(
            deviation_id="dev-1",
            created_at="now",
            area="links",
            description="test",
            reason="test reason",
        )
        assert dev.deviation_id == "dev-1"


class TestControllerResult:
    def test_controller_result_instantiates(self):
        cr = DocumentationSyncControllerResult(
            result_id="cr-1",
            created_at="now",
        )
        assert cr.result_id == "cr-1"


class TestCompletionRecord:
    def test_completion_record_instantiates(self):
        cr = DocumentationSyncCompletionRecord(
            validated_commit="abc123",
            validated_at="now",
        )
        assert cr.validated_commit == "abc123"
        assert cr.component_name == "Documentation Synchronization Layer"


class TestHelpers:
    def test_utc_now_iso_returns_string(self):
        now = utc_now_iso()
        assert isinstance(now, str)
        assert "T" in now
        assert now.endswith("Z") or "Z" in now

    def test_new_id_has_prefix(self):
        nid = new_id("test")
        assert nid.startswith("test_")
        assert len(nid) > 10

    def test_sha256_bytes_consistent(self):
        h1 = sha256_bytes("hello")
        h2 = sha256_bytes("hello")
        h3 = sha256_bytes("world")
        assert h1 == h2
        assert h1 != h3

    def test_is_valid_status(self):
        assert is_valid_status("PASS") is True
        assert is_valid_status("INVALID_STATUS") is False
        assert is_valid_status("FAIL") is True
