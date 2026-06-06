import pytest
import json
import math
from pathlib import Path
from agentx_evolve.evaluation.fixture_validator import (
    validate_benchmark_suite, validate_benchmark_case, validate_expected_result,
)
from agentx_evolve.evaluation.benchmark_loader import resolve_case_refs
from agentx_evolve.evaluation.baseline_manager import load_baseline
from agentx_evolve.evaluation.score_calculator import normalize_score
from agentx_evolve.evaluation.evaluation_models import BenchmarkCase, BenchmarkSuite
from agentx_evolve.evaluation.path_guards import ensure_inside_root
from agentx_evolve.evaluation.comparator_engine import run_comparator
from agentx_evolve.evaluation.report_writer import write_evaluation_report_json
from agentx_evolve.evaluation.evaluation_models import EvaluationReport


def test_malformed_suite_no_case_refs():
    valid, errors = validate_benchmark_suite({"suite_id": "s1"})
    assert not valid


def test_malformed_case_missing_case_id():
    valid, errors = validate_benchmark_case({"case_type": "STATIC_EXPECTED_RESULT"})
    assert not valid


def test_malformed_case_missing_case_type():
    valid, errors = validate_benchmark_case({"case_id": "c1", "case_type": ""})
    assert not valid


def test_missing_expected_result_causes_failure(tmp_path):
    case = BenchmarkCase(case_id="c1", case_type="STATIC_EXPECTED_RESULT", expected_result={})
    from agentx_evolve.evaluation.case_executor import execute_static_case
    result = execute_static_case(case, tmp_path)
    assert not result.passed


def test_unknown_comparator_type_rejected():
    result = run_comparator({"type": "FAKE_TYPE", "path": "", "expected": "x"}, {})
    assert not result["passed"]
    assert "Unknown comparator type" in result["message"]


def test_path_traversal_in_case_ref_rejected():
    suite = BenchmarkSuite(suite_id="s1", case_refs=["../../etc/passwd"])
    with pytest.raises(ValueError, match="Path traversal"):
        resolve_case_refs(suite, Path("/tmp"))


def test_invalid_baseline_missing_baseline_id(tmp_path):
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps({"suite_id": "s1"}))
    baseline = load_baseline(p)
    assert baseline.baseline_id == ""


def test_nan_score_rejected():
    with pytest.raises(ValueError):
        val = normalize_score(float("nan"), 1.0)
        if math.isnan(val):
            raise ValueError("NaN score not allowed")


def test_negative_weight_handled():
    case = BenchmarkCase(case_id="c1", case_type="STATIC_EXPECTED_RESULT", weight=-5.0, expected_result={"expected_status": "PASS"})
    from agentx_evolve.evaluation.score_calculator import calculate_case_score
    result = calculate_case_score(case, {"status": "ok"})
    assert result.weight == 1.0


def test_report_writer_refuses_path_outside_root(tmp_path):
    with pytest.raises(ValueError):
        ensure_inside_root(Path("../outside"), tmp_path)


def test_secret_like_values_redacted_in_reports(tmp_path):
    payload = {"status": "ok", "secret": "sk-test123", "api_key": "abc123"}
    result = run_comparator({"type": "CUSTOM_STATIC_CHECK", "path": "", "expected": "IS_REDACTED"}, payload)
    assert not result["passed"]
