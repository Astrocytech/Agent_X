import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.report_writer import (
    write_evaluation_report, write_evaluation_report_json,
    write_evaluation_report_md, write_latest_evaluation_run,
    write_latest_evaluation_report,
)
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationReport, EvaluationCaseResult,
    EVAL_PASS, EVAL_FAIL,
)


def make_run(run_id="run-1", suite_id="suite-1"):
    return EvaluationRun(
        run_id=run_id,
        suite_id=suite_id,
        case_results=[
            EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0, message="ok"),
            EvaluationCaseResult(case_id="c2", status=EVAL_FAIL, passed=False, score=0.0, message="fail"),
        ],
        score_summary={"normalized_score": 0.5, "status": "PASS"},
        threshold_summary={"passed": True, "checks": []},
    )


def test_write_evaluation_report(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    assert "report" in result
    assert result["report"]["run_id"] == "run-1"
    assert result["report"]["suite_id"] == "suite-1"


def test_write_evaluation_report_creates_artifacts(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    assert Path(result["json_path"]).exists()
    assert Path(result["md_path"]).exists()
    assert Path(result["latest_path"]).exists()


def test_write_evaluation_report_json(tmp_path):
    report = EvaluationReport(report_id="r1", run_id="run-1", suite_id="s1", status="PASS")
    path = write_evaluation_report_json(report, tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["report_id"] == "r1"


def test_write_evaluation_report_json_content(tmp_path):
    report = EvaluationReport(report_id="r2", run_id="run-2", suite_id="s2", status="FAIL")
    path = write_evaluation_report_json(report, tmp_path)
    data = json.loads(path.read_text())
    assert data["status"] == "FAIL"
    assert data["run_id"] == "run-2"


def test_write_evaluation_report_md(tmp_path):
    report = EvaluationReport(
        report_id="r1", run_id="run-1", suite_id="s1",
        status="PASS", summary="test run",
        score_summary={"pass_rate": 1.0},
        threshold_summary={"passed": True},
        case_summaries=[{"case_id": "c1", "status": "EVAL_PASS", "passed": True, "score": 1.0, "message": "ok", "failure_class": None}],
    )
    path = write_evaluation_report_md(report, tmp_path)
    assert path.exists()
    content = path.read_text()
    assert "# Evaluation Report" in content
    assert "c1" in content


def test_write_evaluation_report_md_with_regression(tmp_path):
    report = EvaluationReport(
        report_id="r1", run_id="run-1", suite_id="s1",
        status="PASS",
        score_summary={},
        threshold_summary={},
        regression_summary={"status": "REGRESSION_PASS", "regression_count": 0},
        case_summaries=[],
    )
    path = write_evaluation_report_md(report, tmp_path)
    assert "Regression Summary" in path.read_text()


def test_write_evaluation_report_md_without_regression(tmp_path):
    report = EvaluationReport(
        report_id="r2", run_id="run-2", suite_id="s1",
        status="PASS",
        score_summary={},
        threshold_summary={},
        regression_summary=None,
        case_summaries=[],
    )
    path = write_evaluation_report_md(report, tmp_path)
    assert "Regression Summary" not in path.read_text()


def test_write_latest_evaluation_run(tmp_path):
    run = make_run()
    path = write_latest_evaluation_run(run, tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["run_id"] == "run-1"


def test_write_latest_evaluation_report(tmp_path):
    report = EvaluationReport(report_id="r1", run_id="run-1", suite_id="s1", status="PASS")
    path = write_latest_evaluation_report(report, tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["report_id"] == "r1"


def test_write_evaluation_report_summary_truncates_message(tmp_path):
    long_msg = "x" * 500
    run = make_run()
    run.case_results[0].message = long_msg
    result = write_evaluation_report(run, tmp_path)
    summary_msg = result["report"]["case_summaries"][0]["message"]
    assert len(summary_msg) <= 200


def test_write_evaluation_report_unknown_score_status(tmp_path):
    run = make_run()
    run.score_summary = "not_a_dict"
    result = write_evaluation_report(run, tmp_path)
    assert result["report"]["status"] == "UNKNOWN"
