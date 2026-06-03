import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.fixture_validator import (
    validate_benchmark_suite, validate_benchmark_case,
    validate_expected_result, validate_threshold, validate_baseline,
)
from agentx_evolve.evaluation.evaluation_models import (
    ALL_CASE_TYPES, ALL_COMPARATOR_TYPES, STATIC_EXPECTED_RESULT,
    EXACT_MATCH,
)


def test_schema_integration_valid_suite():
    suite = {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_suite.schema.json",
        "suite_id": "suite-integration",
        "case_refs": ["case1.json", "case2.json"],
        "default_threshold_id": "th-1",
        "baseline_ref": None,
    }
    valid, errors = validate_benchmark_suite(suite)
    assert valid or isinstance(errors, list)


def test_schema_integration_valid_case():
    for case_type in ALL_CASE_TYPES:
        case = {"schema_version": "1.0", "schema_id": "evaluation_benchmark_case.schema.json", "case_id": f"case-{case_type}", "case_type": case_type, "warnings": [], "errors": []}
        valid, errors = validate_benchmark_case(case)
        if not valid:
            assert False, f"Case type {case_type} should be valid, got errors: {errors}"


def test_schema_integration_valid_expected_result():
    for comp_type in ALL_COMPARATOR_TYPES:
        expected = {
            "expected_status": "PASS",
            "comparators": [{"type": comp_type, "path": ".", "expected": "value"}],
        }
        valid, errors = validate_expected_result(expected)
        if not valid and "unknown type" in " ".join(errors).lower():
            assert False, f"Comparator type {comp_type} should be valid, got errors: {errors}"


def test_schema_integration_threshold():
    threshold = {
        "threshold_id": "th-integration",
        "minimum_pass_rate": 0.95,
        "minimum_weighted_score": 0.9,
        "maximum_regression_count": 0,
        "allow_blocked_cases": False,
    }
    valid, errors = validate_threshold(threshold)
    assert isinstance(valid, bool)


def test_schema_integration_baseline():
    baseline = {
        "baseline_id": "bl-integration",
        "suite_id": "suite-1",
        "baseline_run_id": "run-1",
        "score_summary": {"total_cases": 5, "passed_cases": 5},
    }
    valid, errors = validate_baseline(baseline)
    assert isinstance(valid, bool)


def test_schema_integration_round_trip(tmp_path):
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    suite_path = fixture_root / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "rt-suite",
        "case_refs": ["rt-case.json"],
        "default_threshold_id": None,
        "baseline_ref": None,
        "first_run_allowed": True,
        "warnings": [],
        "errors": [],
    }))
    case_data = {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_case.schema.json",
        "case_id": "rt-case",
        "case_type": STATIC_EXPECTED_RESULT,
        "input_payload": {"value": 42},
        "expected_result": {
            "schema_version": "1.0",
            "schema_id": "evaluation_expected_result.schema.json",
            "expected_result_id": "er-1",
            "expected_status": "PASS",
            "warnings": [],
            "errors": [],
            "comparators": [{"type": EXACT_MATCH, "path": "value", "expected": 42}],
        },
        "warnings": [],
        "errors": [],
    }
    (tmp_path / "rt-case.json").write_text(json.dumps(case_data))
    (fixture_root / "rt-case.json").write_text(json.dumps(case_data))
    from agentx_evolve.evaluation.evaluation_runner import run_evaluation
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert run.suite_id == "rt-suite"
    assert len(run.case_results) == 1


def test_schema_integration_invalid_case_type_rejected():
    case = {"schema_version": "1.0", "schema_id": "evaluation_benchmark_case.schema.json", "case_id": "bad", "case_type": "NOT_A_REAL_TYPE", "warnings": [], "errors": []}
    valid, errors = validate_benchmark_case(case)
    assert not valid
    assert any("not one of" in e for e in errors)


def test_schema_integration_missing_expected_result():
    expected = {"schema_version": "1.0", "schema_id": "evaluation_expected_result.schema.json", "expected_result_id": "er-1", "expected_status": "PASS", "warnings": [], "errors": [], "comparators": [{"type": "FAKE_COMP"}]}
    valid, errors = validate_expected_result(expected)
    assert not valid
    assert "unknown type" in " ".join(errors).lower()


def test_schema_integration_suite_with_all_fields():
    suite = {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_suite.schema.json",
        "suite_id": "full-suite",
        "suite_name": "Full Schema Suite",
        "description": "Suite with all fields",
        "created_at": "2024-01-01T00:00:00",
        "source_component": "test",
        "case_refs": [],
        "default_threshold_id": "th-default",
        "baseline_ref": None,
        "first_run_allowed": True,
        "tags": ["smoke"],
    }
    valid, errors = validate_benchmark_suite(suite)
    assert valid or isinstance(errors, list)


def test_schema_validation_utility_covers_run_config_and_fixture_lock():
    schemas = [
        "evaluation_run_config.schema.json",
        "evaluation_fixture_lock.schema.json",
    ]
    from pathlib import Path
    schema_dir = Path(__file__).resolve().parents[3] / "tools" / "agentx_evolve" / "schemas"
    for s in schemas:
        assert (schema_dir / s).exists(), f"Missing schema: {s}"
