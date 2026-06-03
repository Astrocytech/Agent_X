import pytest
from agentx_evolve.tools.tool_models import ToolReviewReport


def test_review_report_records_findings():
    r = ToolReviewReport(
        review_report_id="rr-1",
        reviewed_commit="abc123",
        findings=["all tools registered"],
        final_verdict="PASS",
    )
    assert r.review_report_id == "rr-1"
    assert r.reviewed_commit == "abc123"
    assert r.findings == ["all tools registered"]
    assert r.final_verdict == "PASS"


def test_review_report_defaults():
    r = ToolReviewReport()
    assert r.final_verdict == "NOT_DONE"
    assert r.findings == []
    assert r.blockers == []


def test_review_report_blockers():
    r = ToolReviewReport(
        review_report_id="rr-2",
        blockers=["missing schema"],
        final_verdict="FAIL",
    )
    assert r.blockers == ["missing schema"]
    assert r.final_verdict == "FAIL"


def test_review_report_component():
    r = ToolReviewReport()
    assert r.component_id == "ToolMCPAdapter"


def test_review_report_empty():
    r = ToolReviewReport()
    assert r.review_report_id == ""
