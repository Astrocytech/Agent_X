import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkSuite, BenchmarkCase, EvaluationRun, EvaluationCaseResult,
    EVAL_PASS, EVAL_FAIL, EVAL_SKIPPED,
    utc_now_iso, new_eval_id,
)
from agentx_evolve.evaluation.fixture_validator import validate_benchmark_suite, validate_benchmark_case
from agentx_evolve.evaluation.score_calculator import calculate_run_score
from agentx_evolve.evaluation.threshold_checker import check_thresholds
from agentx_evolve.evaluation.path_guards import resolve_inside_root


def test_smoke_imports():
    from agentx_evolve.evaluation import (
        EVAL_PASS, EVAL_FAIL,
        BenchmarkSuite, BenchmarkCase, EvaluationRun,
        run_evaluation,
    )
    assert EVAL_PASS == "EVAL_PASS"


def test_smoke_create_suite():
    suite = BenchmarkSuite(suite_id="smoke-1", suite_name="Smoke Test Suite")
    assert suite.suite_id == "smoke-1"


def test_smoke_create_case():
    case = BenchmarkCase(case_id="smoke-1", case_type="STATIC_EXPECTED_RESULT", input_payload={"key": "value"})
    assert case.case_id == "smoke-1"


def test_smoke_create_result():
    result = EvaluationCaseResult(case_id="smoke-1", status=EVAL_PASS, passed=True, score=1.0)
    assert result.passed


def test_smoke_validate_suite():
    suite_data = {"suite_id": "s1", "case_refs": ["c1.json"]}
    valid, errors = validate_benchmark_suite(suite_data)
    assert isinstance(valid, bool)


def test_smoke_validate_case():
    case_data = {"case_id": "c1", "case_type": "STATIC_EXPECTED_RESULT"}
    valid, errors = validate_benchmark_case(case_data)
    assert isinstance(valid, bool) or isinstance(valid, bool)


def test_smoke_calculate_score_empty():
    score = calculate_run_score([])
    assert score.total_cases == 0
    assert score.passed_cases == 0


def test_smoke_utc_now():
    now = utc_now_iso()
    assert isinstance(now, str)


def test_smoke_new_id():
    eid = new_eval_id()
    assert isinstance(eid, str)
    assert len(eid) > 5


def test_smoke_full_pipeline(tmp_path):
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    suite_path = fixture_dir / "smoke_suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "smoke_suite",
        "case_refs": ["smoke_case.json"],
        "first_run_allowed": True,
        "default_threshold_id": None,
        "baseline_ref": None,
        "warnings": [],
        "errors": [],
    }))
    case_path = fixture_dir / "smoke_case.json"
    case_path.write_text(json.dumps({
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_case.schema.json",
        "case_id": "smoke_case", "case_type": "STATIC_EXPECTED_RESULT",
        "input_payload": {"result": "pass"},
        "expected_result": {
            "schema_version": "1.0",
            "schema_id": "evaluation_expected_result.schema.json",
            "expected_result_id": "er-1",
            "expected_status": "PASS",
            "warnings": [],
            "errors": [],
            "comparators": [{"type": "EXACT_MATCH", "path": "result", "expected": "pass"}],
        },
        "warnings": [],
        "errors": [],
    }))
    from agentx_evolve.evaluation.evaluation_runner import run_evaluation
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert run.suite_id == "smoke_suite"


def test_smoke_path_guard():
    path = resolve_inside_root(Path("sub/file.txt"), Path("/tmp"))
    assert str(path).endswith("sub/file.txt")
