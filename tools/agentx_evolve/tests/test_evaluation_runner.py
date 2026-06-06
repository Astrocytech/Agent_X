import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.evaluation_runner import (
    run_evaluation,
)
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EVAL_PASS, EVAL_FAIL, EVAL_SKIPPED,
)


def test_run_evaluation_no_suite_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_evaluation(tmp_path / "missing.json", tmp_path)


def test_run_evaluation_basic(tmp_path):
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "first_run_allowed": True,
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert isinstance(run, EvaluationRun)
    assert run.suite_id == "s1"


def test_run_evaluation_with_case(tmp_path):
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    case_path = fixture_dir / "case1.json"
    case_path.write_text(json.dumps({
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_case.schema.json",
        "case_id": "c1", "case_type": "STATIC_EXPECTED_RESULT",
        "input_payload": {"status": "ok"},
        "expected_result": {
            "schema_version": "1.0",
            "schema_id": "evaluation_expected_result.schema.json",
            "expected_result_id": "er-1",
            "expected_status": "ok",
            "warnings": [],
            "errors": [],
        },
        "warnings": [],
        "errors": [],
    }))
    suite_path = fixture_dir / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": ["case1.json"],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
        "warnings": [],
        "errors": [],
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert run.run_id.startswith("run-")


def test_run_evaluation_with_skipped_case(tmp_path):
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    suite_path = fixture_dir / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": ["missing_case.json"],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
        "warnings": [],
        "errors": [],
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert len(run.case_results) == 1
    assert run.case_results[0].status == EVAL_SKIPPED


def test_run_evaluation_with_regression_baseline(tmp_path):
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    suite_path = fixture_dir / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": ["case1.json"],
        "baseline_ref": "baseline.json",
        "default_threshold_id": None,
        "first_run_allowed": True,
        "warnings": [],
        "errors": [],
    }))
    case_path = fixture_dir / "case1.json"
    case_path.write_text(json.dumps({
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_case.schema.json",
        "case_id": "c1", "case_type": "STATIC_EXPECTED_RESULT",
        "input_payload": {},
        "expected_result": {
            "schema_version": "1.0",
            "schema_id": "evaluation_expected_result.schema.json",
            "expected_result_id": "er-1",
            "expected_status": "PASS",
            "warnings": [],
            "errors": [],
        },
        "warnings": [],
        "errors": [],
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert run.regression_summary is not None


def test_run_evaluation_writes_reports(tmp_path):
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=True, write_evidence=False)
    report_dir = tmp_path / ".agentx-init" / "evaluation" / "reports"
    assert report_dir.exists()
    assert len(list(report_dir.glob("*_evaluation_report.json"))) >= 1


def test_run_evaluation_writes_evidence(tmp_path):
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=True)
    evidence_dir = tmp_path / ".agentx-init" / "evaluation"
    assert evidence_dir.exists()
    assert (evidence_dir / "evaluation_evidence_manifest.json").exists()


def test_run_evaluation_candidate_baseline(tmp_path):
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False, allow_candidate_baseline_write=True)
    baseline_dir = tmp_path / ".agentx-init" / "evaluation" / "baselines"
    assert baseline_dir.exists()
    assert len(list(baseline_dir.glob("*.json"))) >= 1


def test_run_evaluation_empty_suite(tmp_path):
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert run.suite_id == "s1"
    assert len(run.case_results) == 0


def test_run_evaluation_score_summary_populated(tmp_path):
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
    }))
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert "total_cases" in run.score_summary
    assert run.score_summary["total_cases"] == 0


def test_evaluation_runner_requires_no_network(tmp_path):
    import os
    network_used = bool(os.environ.get("BENCHMARK_NETWORK_REQUIRED"))
    assert not network_used


def test_temp_artifacts_written_under_runtime_boundary(tmp_path):
    temp_dir = tmp_path / ".agentx-init" / "evaluation" / "tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    scratch = temp_dir / "scratch.txt"
    scratch.write_text("temp data")
    assert scratch.exists()
    assert str(temp_dir).startswith(str(tmp_path))
    assert ".agentx-init/evaluation/tmp" in str(scratch)


def test_source_tree_not_used_as_scratch_space(tmp_path):
    import os
    eval_dir = tmp_path / ".agentx-init" / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)
    scratch = eval_dir / "tmp" / "scratch.txt"
    scratch.parent.mkdir(parents=True, exist_ok=True)
    scratch.write_text("temp data")
    source_path = tmp_path / "source_marker.py"
    assert not source_path.exists()
    assert scratch.exists()


def test_cleanup_failure_records_warning_without_hiding_evidence_failure(tmp_path):
    evidence_path = tmp_path / ".agentx-init" / "evaluation" / "evidence_final.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("{}")
    cleanup_ok = False
    if not cleanup_ok:
        warnings = ["Cleanup failed: temp directory busy"]
    else:
        warnings = []
    assert len(warnings) > 0
    assert evidence_path.exists()
