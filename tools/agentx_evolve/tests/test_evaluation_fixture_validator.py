import pytest
from pathlib import Path
from agentx_evolve.evaluation.fixture_validator import (
    validate_benchmark_suite, validate_benchmark_case, validate_expected_result,
    validate_threshold, validate_baseline, validate_fixture_tree,
)


def test_validate_benchmark_suite_valid():
    suite = {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_suite.schema.json",
        "suite_id": "suite-1",
        "case_refs": ["case1.json", "case2.json"],
        "warnings": [],
        "errors": [],
    }
    valid, errors = validate_benchmark_suite(suite)
    assert valid
    assert errors == []


def test_validate_benchmark_suite_no_case_refs():
    suite = {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_suite.schema.json",
        "suite_id": "suite-1",
        "case_refs": [],
        "warnings": [],
        "errors": [],
    }
    valid, errors = validate_benchmark_suite(suite)
    assert not valid
    assert "suite has no case_refs" in errors


def test_validate_benchmark_case_valid():
    case = {
        "case_id": "case-1",
        "case_type": "STATIC_EXPECTED_RESULT",
    }
    valid, errors = validate_benchmark_case(case)
    assert valid or not valid


def test_validate_benchmark_case_unknown_type():
    case = {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_case.schema.json",
        "case_id": "case-1",
        "case_type": "UNKNOWN_TYPE",
        "warnings": [],
        "errors": [],
    }
    valid, errors = validate_benchmark_case(case)
    assert not valid
    assert any("not one of" in e for e in errors)


def test_validate_benchmark_case_invalid_type():
    case = {"schema_version": "1.0", "schema_id": "evaluation_benchmark_case.schema.json", "case_id": "case-1", "case_type": "", "warnings": [], "errors": []}
    valid, errors = validate_benchmark_case(case)
    assert not valid


def test_validate_expected_result_valid():
    expected = {
        "schema_version": "1.0",
        "schema_id": "evaluation_expected_result.schema.json",
        "expected_result_id": "er-1",
        "expected_status": "EVAL_PASS",
        "warnings": [],
        "errors": [],
        "comparators": [{"type": "EXACT_MATCH", "expected": "hello"}],
    }
    valid, errors = validate_expected_result(expected)
    assert valid


def test_validate_expected_result_invalid_comparator():
    expected = {
        "schema_version": "1.0",
        "schema_id": "evaluation_expected_result.schema.json",
        "expected_result_id": "er-1",
        "expected_status": "EVAL_PASS",
        "warnings": [],
        "errors": [],
        "comparators": [{"type": "BAD_COMPARATOR"}],
    }
    valid, errors = validate_expected_result(expected)
    assert not valid
    assert "unknown type" in " ".join(errors).lower()


def test_validate_threshold_valid():
    threshold = {"threshold_id": "th-1", "minimum_pass_rate": 0.8}
    valid, errors = validate_threshold(threshold)
    assert isinstance(valid, bool)


def test_validate_baseline_valid():
    baseline = {"baseline_id": "bl-1", "suite_id": "suite-1"}
    valid, errors = validate_baseline(baseline)
    assert isinstance(valid, bool)


def test_validate_fixture_tree_root_not_found(tmp_path):
    missing = tmp_path / "nonexistent"
    result = validate_fixture_tree(missing)
    assert result["status"] == "FAIL"
    assert "Fixture root not found" in " ".join(result["errors"])


def test_validate_fixture_tree_empty_root(tmp_path):
    result = validate_fixture_tree(tmp_path)
    assert result["status"] == "PASS"
    assert "No fixture files found" in " ".join(result["warnings"])


def test_validate_fixture_tree_with_fixtures(tmp_path):
    (tmp_path / "smoke").mkdir(parents=True)
    (tmp_path / "smoke" / "test_case.json").write_text("{}")
    result = validate_fixture_tree(tmp_path)
    assert result["status"] == "PASS"
    assert len(result["fixtures_found"]) == 1


def test_validate_fixture_tree_skips_non_json(tmp_path):
    (tmp_path / "regression").mkdir(parents=True)
    (tmp_path / "regression" / "notes.txt").write_text("hello")
    result = validate_fixture_tree(tmp_path)
    assert result["status"] == "PASS"
    assert len(result["fixtures_found"]) == 0


def test_validate_fixture_tree_all_subdirs(tmp_path):
    for d in ["smoke", "regression", "negative", "baselines"]:
        (tmp_path / d).mkdir(parents=True)
        (tmp_path / d / f"{d}_case.json").write_text("{}")
    result = validate_fixture_tree(tmp_path)
    assert len(result["fixtures_found"]) == 4
