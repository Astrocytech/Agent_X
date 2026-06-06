import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.report_writer import (
    write_evaluation_report, write_evaluation_report_json,
    write_evaluation_report_md,
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
        score_summary={"normalized_score": 0.5, "status": "PASS", "passed_cases": 1, "failed_cases": 1, "total_cases": 2},
        threshold_summary={"passed": True, "checks": []},
    )


def test_report_json_and_md_same_run_id(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    md_content = Path(result["md_path"]).read_text()
    assert json_data["run_id"] == run.run_id
    assert run.run_id in md_content


def test_report_json_and_md_same_suite_id(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    md_content = Path(result["md_path"]).read_text()
    assert json_data["suite_id"] == "suite-1"
    assert "suite-1" in md_content


def test_report_json_contains_score_summary(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    assert "score_summary" in json_data
    assert json_data["score_summary"]["total_cases"] == 2


def test_report_md_contains_case_results(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    md_content = Path(result["md_path"]).read_text()
    assert "c1" in md_content
    assert "c2" in md_content


def test_report_json_contains_threshold_summary(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    assert "threshold_summary" in json_data


def test_report_md_contains_final_verdict(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    md_content = Path(result["md_path"]).read_text()
    assert "Final Verdict" in md_content


def test_report_parity_both_have_same_case_count(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    md_content = Path(result["md_path"]).read_text()
    json_count = len(json_data["case_summaries"])
    assert json_count == 2
    assert f"{json_count} cases" in md_content or "c1" in md_content


def test_report_json_with_regression(tmp_path):
    run = make_run()
    run.regression_summary = {"status": "REGRESSION_PASS", "regression_count": 0}
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    assert json_data["regression_summary"] is not None


def test_report_md_with_regression(tmp_path):
    run = make_run()
    run.regression_summary = {"status": "REGRESSION_PASS", "regression_count": 0}
    result = write_evaluation_report(run, tmp_path)
    md_content = Path(result["md_path"]).read_text()
    assert "Regression Summary" in md_content


def test_report_json_without_regression(tmp_path):
    run = make_run()
    run.regression_summary = None
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    assert json_data["regression_summary"] is None


def test_report_parity_latest_is_same_as_json(tmp_path):
    run = make_run()
    result = write_evaluation_report(run, tmp_path)
    json_data = json.loads(Path(result["json_path"]).read_text())
    latest_data = json.loads(Path(result["latest_path"]).read_text())
    assert json_data["run_id"] == latest_data["run_id"]
    assert json_data["suite_id"] == latest_data["suite_id"]
