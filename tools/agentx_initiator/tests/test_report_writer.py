from agentx_initiator.core.report_writer import render_report


def test_render_status_report():
    context = {
        "repo_scan": type("obj", (object,), {"root": "/test", "total_files": 5, "source_files": 3, "doc_files": 1, "test_files": 1, "layers": []})(),
        "governance_checks": [],
        "passed": 0,
        "failed": 0,
    }
    result = render_report("status_report.md.j2", context)
    assert "Agent_X Status Report" in result
