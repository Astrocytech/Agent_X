import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.promotion_controller import (
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


def test_check_promotion_ready_no_manifest():
    ready, blockers = check_promotion_ready(None, None)
    assert ready is False
    assert "Evidence manifest is missing" in blockers
    assert "Review report is missing" in blockers


def test_check_promotion_ready_manifest_no_hash():
    manifest = OrchestratorEvidenceManifest(manifest_id="m-1", evidence_manifest_sha256="")
    ready, blockers = check_promotion_ready(manifest, None)
    assert ready is False
    assert "Evidence manifest hash is missing" in blockers


def test_check_promotion_ready_manifest_no_files():
    manifest = OrchestratorEvidenceManifest(
        manifest_id="m-1",
        evidence_manifest_sha256="abc123",
        evidence_files=[],
    )
    ready, blockers = check_promotion_ready(manifest, None)
    assert ready is False
    assert "has no evidence files" in blockers[0]


def test_check_promotion_ready_review_no_hash():
    manifest = OrchestratorEvidenceManifest(
        manifest_id="m-1",
        evidence_manifest_sha256="abc123",
        evidence_files=["f1"],
    )
    report = OrchestratorReviewReport(review_report_id="rr-1", review_report_sha256="")
    ready, blockers = check_promotion_ready(manifest, report)
    assert ready is False
    assert "Review report hash is missing" in blockers


def test_check_promotion_ready_with_blockers():
    manifest = OrchestratorEvidenceManifest(
        manifest_id="m-1",
        evidence_manifest_sha256="abc123",
        evidence_files=["f1"],
    )
    report = OrchestratorReviewReport(
        review_report_id="rr-1",
        review_report_sha256="def456",
        blockers=["Policy violation"],
    )
    ready, blockers = check_promotion_ready(manifest, report)
    assert ready is False
    assert "Policy violation" in blockers


def test_check_promotion_ready_all_good():
    manifest = OrchestratorEvidenceManifest(
        manifest_id="m-1",
        evidence_manifest_sha256="abc123",
        evidence_files=["f1"],
    )
    report = OrchestratorReviewReport(
        review_report_id="rr-1",
        review_report_sha256="def456",
    )
    ready, blockers = check_promotion_ready(manifest, report)
    assert ready is True
    assert blockers == []


def test_create_promotion_gate_record():
    record = create_promotion_gate_record("r-1")
    assert record.run_id == "r-1"
    assert record.promotion_status == GATE_STATUS_PENDING
    assert record.promotion_target == "next_layer"
    assert record.promotion_record_id.startswith("pg-")


def test_create_promotion_gate_record_custom_target():
    record = create_promotion_gate_record("r-1", promotion_target="production")
    assert record.promotion_target == "production"


def test_request_promotion_decision_no_fn():
    record = create_promotion_gate_record("r-1")
    result = request_promotion_decision(record)
    assert result.promotion_status == GATE_STATUS_APPROVED
    assert result.promotion_decision == GATE_STATUS_APPROVED


def test_request_promotion_decision_fn_approves():
    record = create_promotion_gate_record("r-1")

    def gate_fn(**kwargs):
        return {"decision": "APPROVED"}

    result = request_promotion_decision(record, promotion_gate_fn=gate_fn)
    assert result.promotion_status == GATE_STATUS_APPROVED


def test_request_promotion_decision_fn_denies():
    record = create_promotion_gate_record("r-1")

    def gate_fn(**kwargs):
        return {"decision": "DENIED", "reason": "Not ready"}

    result = request_promotion_decision(record, promotion_gate_fn=gate_fn)
    assert result.promotion_status == GATE_STATUS_DENIED
    assert "Not ready" in result.errors[-1]


def test_request_promotion_decision_fn_raises():
    record = create_promotion_gate_record("r-1")

    def gate_fn(**kwargs):
        raise RuntimeError("Gate crashed")

    result = request_promotion_decision(record, promotion_gate_fn=gate_fn)
    assert result.promotion_status == GATE_STATUS_DENIED
    assert "Promotion gate error" in result.errors[-1]
