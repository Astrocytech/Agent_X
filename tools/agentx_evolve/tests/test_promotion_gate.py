import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.promotion_gate import (
    check_promotion_ready,
    create_promotion_gate_record,
    request_promotion_decision,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestratorEvidenceManifest,
    OrchestratorReviewReport,
    PromotionGateRecord,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    GATE_STATUS_PENDING,
    GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED,
)


class TestCheckPromotionReadyWithManifestAndReport:
    def test_check_promotion_ready_with_manifest_and_report(self):
        manifest = OrchestratorEvidenceManifest(
            manifest_id="m-1",
            run_id="run-1",
            evidence_files=["file1.py"],
            evidence_manifest_sha256="abc123",
        )
        report = OrchestratorReviewReport(
            review_report_id="r-1",
            review_report_sha256="def456",
        )
        ready, blockers = check_promotion_ready(manifest, report)
        assert ready is True
        assert blockers == []


class TestCheckPromotionReadyBlockedMissingManifest:
    def test_check_promotion_ready_blocked_missing_manifest(self):
        ready, blockers = check_promotion_ready(None, OrchestratorReviewReport(review_report_id="r-1"))
        assert ready is False
        assert any("manifest is missing" in b.lower() for b in blockers)


class TestCheckPromotionReadyBlockedMissingHash:
    def test_check_promotion_ready_blocked_missing_hash(self):
        manifest = OrchestratorEvidenceManifest(
            manifest_id="m-1",
            run_id="run-1",
            evidence_files=["file1.py"],
        )
        report = OrchestratorReviewReport(
            review_report_id="r-1",
            review_report_sha256="def456",
        )
        ready, blockers = check_promotion_ready(manifest, report)
        assert ready is False
        assert any("hash" in b.lower() for b in blockers)


class TestCheckPromotionReadyBlockedReportBlockers:
    def test_check_promotion_ready_blocked_report_blockers(self):
        manifest = OrchestratorEvidenceManifest(
            manifest_id="m-1",
            run_id="run-1",
            evidence_files=["file1.py"],
            evidence_manifest_sha256="abc123",
        )
        report = OrchestratorReviewReport(
            review_report_id="r-1",
            review_report_sha256="def456",
            blockers=["Review found issues", "Quality gate not met"],
        )
        ready, blockers = check_promotion_ready(manifest, report)
        assert ready is False
        assert "Review found issues" in blockers
        assert "Quality gate not met" in blockers


class TestCreatePromotionGateRecord:
    def test_create_promotion_gate_record(self):
        record = create_promotion_gate_record("run-1", promotion_target="production")
        assert record.promotion_record_id.startswith("pg-")
        assert record.run_id == "run-1"
        assert record.promotion_target == "production"
        assert record.promotion_status == GATE_STATUS_PENDING


class TestRequestPromotionDecisionWithAdapter:
    def test_request_promotion_decision_with_adapter(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )

        def approve_adapter(**kw):
            return {"decision": GATE_STATUS_APPROVED}

        result = request_promotion_decision(record, approve_adapter)
        assert result.promotion_status == GATE_STATUS_APPROVED
        assert result.promotion_decision == GATE_STATUS_APPROVED

    def test_request_promotion_decision_with_adapter_denies(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )

        def deny_adapter(**kw):
            return {"decision": GATE_STATUS_DENIED, "reason": "not ready"}

        result = request_promotion_decision(record, deny_adapter)
        assert result.promotion_status == GATE_STATUS_DENIED
        assert result.promotion_decision == GATE_STATUS_DENIED
        assert any("not ready" in e for e in result.errors)


class TestRequestPromotionDecisionWithoutAdapterDefaultsApproved:
    def test_request_promotion_decision_without_adapter_defaults_approved(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )
        result = request_promotion_decision(record, None)
        assert result.promotion_status == GATE_STATUS_APPROVED
        assert result.promotion_decision == GATE_STATUS_APPROVED


class TestRequestPromotionDecisionHandlesAdapterError:
    def test_request_promotion_decision_handles_adapter_error(self):
        record = PromotionGateRecord(
            promotion_record_id="pg-1",
            run_id="run-1",
        )

        def broken_adapter(**kw):
            raise Exception("gate crashed")

        result = request_promotion_decision(record, broken_adapter)
        assert result.promotion_status == GATE_STATUS_DENIED
        assert result.promotion_decision == GATE_STATUS_DENIED
        assert any("gate error" in e.lower() for e in result.errors)
