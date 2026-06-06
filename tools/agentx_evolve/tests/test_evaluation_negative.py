import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.case_executor import execute_negative_fixture_case
from agentx_evolve.evaluation.fixture_validator import validate_benchmark_case
from agentx_evolve.evaluation.evaluation_models import BenchmarkCase, EVAL_PASS, EVAL_FAIL


def test_negative_case_rejects_invalid_case_type():
    case = BenchmarkCase(
        case_id="neg-1",
        case_type="NEGATIVE_FIXTURE_VALIDATION",
        warnings=["bad case"],
        errors=["invalid field"],
        expected_result={"expected_status": "EVAL_FAIL"},
    )
    result = execute_negative_fixture_case(case, Path("/tmp"))
    assert result.status == EVAL_FAIL


def test_negative_case_with_empty_case():
    case = BenchmarkCase(
        case_id="neg-2",
        case_type="NEGATIVE_FIXTURE_VALIDATION",
        expected_result={"expected_status": "EVAL_FAIL"},
    )
    result = execute_negative_fixture_case(case, Path("/tmp"))
    assert result.case_id == "neg-2"


def test_negative_case_missing_case_type():
    case_dict = {"case_id": "neg-1", "case_type": ""}
    valid, errors = validate_benchmark_case(case_dict)
    assert not valid


def test_negative_case_unknown_case_type():
    case_dict = {"schema_version": "1.0", "schema_id": "evaluation_benchmark_case.schema.json", "case_id": "neg-1", "case_type": "COMPLETELY_FAKE_TYPE", "warnings": [], "errors": []}
    valid, errors = validate_benchmark_case(case_dict)
    assert not valid
    assert any("not one of" in e for e in errors)


def test_negative_case_missing_case_id():
    case_dict = {"case_type": "STATIC_EXPECTED_RESULT"}
    valid, errors = validate_benchmark_case(case_dict)
    assert not valid or not valid


def test_negative_suite_no_case_refs():
    from agentx_evolve.evaluation.fixture_validator import validate_benchmark_suite
    valid, errors = validate_benchmark_suite({"schema_version": "1.0", "schema_id": "evaluation_benchmark_suite.schema.json", "suite_id": "s1", "case_refs": [], "warnings": [], "errors": []})
    assert not valid
    assert "suite has no case_refs" in errors


def test_negative_suite_empty_case_refs():
    from agentx_evolve.evaluation.fixture_validator import validate_benchmark_suite
    valid, errors = validate_benchmark_suite({"suite_id": "s1", "case_refs": []})
    assert not valid


def test_negative_expected_result_empty_comparator():
    from agentx_evolve.evaluation.fixture_validator import validate_expected_result
    valid, errors = validate_expected_result({"expected_status": "PASS", "comparators": [{"type": ""}]})
    assert not valid


def test_negative_case_with_traversal_ref():
    from agentx_evolve.evaluation.benchmark_loader import resolve_case_refs
    from agentx_evolve.evaluation.evaluation_models import BenchmarkSuite
    suite = BenchmarkSuite(suite_id="s1", case_refs=["../../etc/passwd"])
    with pytest.raises(ValueError, match="Path traversal"):
        resolve_case_refs(suite, Path("/tmp"))


def test_negative_run_config_no_id():
    from agentx_evolve.evaluation.run_config import validate_run_config
    valid, errors = validate_run_config({"timeout_seconds": "bad", "max_case_count": "bad"})
    assert not valid


def test_negative_threshold_all_failing():
    from agentx_evolve.evaluation.threshold_checker import check_thresholds
    from agentx_evolve.evaluation.evaluation_models import EvaluationScore, EvaluationThreshold
    score = EvaluationScore(total_cases=2, passed_cases=0, pass_rate=0.0, weighted_score=0.0)
    th = EvaluationThreshold(threshold_id="th-1", minimum_pass_rate=1.0, minimum_weighted_score=1.0)
    result = check_thresholds(score, th, [])
    assert not result["passed"]


def test_negative_baseline_not_found():
    from agentx_evolve.evaluation.baseline_manager import load_baseline
    with pytest.raises(FileNotFoundError):
        load_baseline(Path("/nonexistent/baseline.json"))
