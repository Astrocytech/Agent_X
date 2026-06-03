import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.sync_reporter import (
    build_documentation_sync_review_report,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentScanReport, DocumentRecord, DocumentDriftRecord,
    DocumentLinkRecord, DocumentStalenessRecord, DocumentSyncPlan,
    DocumentSyncOperation, DocumentSyncResult,
    DOC_AUTHORITY_MANUAL_GOVERNED, DOC_AUTHORITY_GENERATED,
    DOC_TYPE_CONTRACT, DOC_TYPE_README,
    CENTRAL_STATUS_PASS, CENTRAL_STATUS_PARTIAL, CENTRAL_STATUS_FAIL,
    SEVERITY_BLOCKER, SEVERITY_HIGH,
)


class TestReporter:
    def test_review_report_with_no_drifts(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        docs = [DocumentRecord(document_id="d1", path="d.md")]
        scan.documents = docs
        report = build_documentation_sync_review_report(scan, [], [], [])
        assert report.final_verdict == CENTRAL_STATUS_PASS
        assert report.scan_status == CENTRAL_STATUS_PASS
        assert report.drift_status == CENTRAL_STATUS_PASS

    def test_review_report_with_blocker_drift(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        drifts = [
            DocumentDriftRecord(
                drift_id="d1", created_at="now",
                document_id="doc1", path="p.md",
                drift_type="DONE_WITHOUT_EVIDENCE", status="DRIFTED",
                severity=SEVERITY_BLOCKER,
            ),
        ]
        report = build_documentation_sync_review_report(scan, drifts, [], [])
        assert report.final_verdict == CENTRAL_STATUS_FAIL
        assert report.drift_status == CENTRAL_STATUS_FAIL
        assert len(report.blockers) > 0

    def test_review_report_with_high_drift(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        drifts = [
            DocumentDriftRecord(
                drift_id="d1", created_at="now",
                document_id="doc1", path="p.md",
                drift_type="MISSING_SCHEMA", status="DRIFTED",
                severity=SEVERITY_HIGH,
            ),
        ]
        report = build_documentation_sync_review_report(scan, drifts, [], [])
        assert report.final_verdict == CENTRAL_STATUS_PASS
        assert report.drift_status == CENTRAL_STATUS_PARTIAL
        assert len(report.high_issues) > 0

    def test_review_report_with_broken_links(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        links = [
            DocumentLinkRecord(
                link_id="l1", source_path="s.md", target="missing.md",
                status=CENTRAL_STATUS_FAIL,
            ),
        ]
        report = build_documentation_sync_review_report(scan, [], links, [])
        assert report.final_verdict == CENTRAL_STATUS_FAIL
        assert report.link_status == CENTRAL_STATUS_FAIL
        assert len(report.blockers) > 0

    def test_review_report_with_missing_documents(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        stales = [
            DocumentStalenessRecord(
                staleness_id="s1", document_id="m1", path="m.md",
                status="MISSING", staleness_reason="file not found",
            ),
        ]
        report = build_documentation_sync_review_report(scan, [], [], stales)
        assert report.final_verdict == CENTRAL_STATUS_FAIL
        assert report.staleness_status == CENTRAL_STATUS_FAIL

    def test_review_report_with_sync_plan_blocked_ops(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        blocked = [
            DocumentSyncOperation(
                operation_id="op1", operation_type="BLOCKED_MANUAL_DOC",
                target_path="contract.md", target_authority="MANUAL_GOVERNED",
                allowed_to_apply=False,
                reason="manual doc blocked",
            ),
        ]
        plan = DocumentSyncPlan(plan_id="p1", created_at="now", source_scan_id="s1",
                                operations=[], blocked_operations=blocked, summary={})
        report = build_documentation_sync_review_report(scan, [], [], [], plan)
        assert report.manual_doc_protection_status == CENTRAL_STATUS_PASS

    def test_review_report_created_at_is_string(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        report = build_documentation_sync_review_report(scan, [], [], [])
        assert isinstance(report.created_at, str)
        assert len(report.created_at) > 0

    def test_review_report_with_all_components(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        docs = [DocumentRecord(document_id="d1", path="d.md", document_type=DOC_TYPE_CONTRACT)]
        scan.documents = docs
        report = build_documentation_sync_review_report(scan, [], [], [])
        assert report.scan_status == CENTRAL_STATUS_PASS

    def test_review_report_non_blocking_followups(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        stales = [
            DocumentStalenessRecord(
                staleness_id="s1", document_id="d1", path="d.md",
                status="STALE", staleness_reason="outdated hash",
            ),
        ]
        report = build_documentation_sync_review_report(scan, [], [], stales)
        assert report.final_verdict == CENTRAL_STATUS_PASS
        assert report.staleness_status == CENTRAL_STATUS_PARTIAL
        assert len(report.non_blocking_followups) > 0
