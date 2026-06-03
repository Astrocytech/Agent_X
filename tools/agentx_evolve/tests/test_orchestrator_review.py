import pytest
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestratorReviewReport
)


def test_review_report_defaults():
    r = OrchestratorReviewReport()
    assert r.final_verdict == "NOT_DONE"
    assert r.blockers == []
    assert r.commands_run == []


def test_review_report_records_findings():
    r = OrchestratorReviewReport(
        review_report_id="rr-1",
        reviewed_commit="abc123",
        commands_run=["pytest"],
        blockers=["missing coverage"],
        final_verdict="FAIL",
    )
    assert r.review_report_id == "rr-1"
    assert r.reviewed_commit == "abc123"
    assert r.commands_run == ["pytest"]
    assert r.blockers == ["missing coverage"]
    assert r.final_verdict == "FAIL"


def test_review_report_to_dict():
    r = OrchestratorReviewReport(review_report_id="rr-2")
    d = r.to_dict()
    assert d["review_report_id"] == "rr-2"
    assert d["final_verdict"] == "NOT_DONE"


def test_review_report_compute_hash():
    r = OrchestratorReviewReport(review_report_id="rr-3")
    h = r.compute_hash()
    assert isinstance(h, str)
    assert len(h) == 64


def test_review_report_empty_blockers():
    r = OrchestratorReviewReport(review_report_id="rr-4")
    assert r.blockers == []
