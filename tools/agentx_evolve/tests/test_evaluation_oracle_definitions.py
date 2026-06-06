import pytest
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationExpectedResult, EvaluationThreshold,
    EXACT_MATCH, CONTAINS, REGEX_MATCH, NUMERIC_EQUALS,
)
from agentx_evolve.evaluation.comparator_engine import run_comparator, compare_observed_to_expected


def test_oracle_created_with_required_fields():
    oracle = EvaluationExpectedResult(expected_result_id="or-1", expected_status="PASS")
    assert oracle.expected_result_id == "or-1"
    assert oracle.expected_status == "PASS"


def test_invalid_oracle_id_empty():
    oracle = EvaluationExpectedResult(expected_result_id="", expected_status="PASS")
    assert oracle.expected_result_id == ""


def test_invalid_oracle_type_handled():
    oracle = EvaluationExpectedResult(expected_result_id="or-1", expected_status="INVALID_STATUS")
    assert oracle.expected_status == "INVALID_STATUS"


def test_oracle_can_reference_comparators():
    oracle = EvaluationExpectedResult(
        expected_result_id="or-1",
        expected_status="PASS",
        comparators=[
            {"type": EXACT_MATCH, "path": "status", "expected": "PASS"},
            {"type": NUMERIC_EQUALS, "path": "score", "expected": 1.0},
        ],
    )
    assert len(oracle.comparators) == 2
    assert oracle.comparators[0]["type"] == EXACT_MATCH


def test_oracle_comparator_execution():
    oracle = EvaluationExpectedResult(
        expected_result_id="or-1",
        expected_status="PASS",
        comparators=[{"type": EXACT_MATCH, "path": "status", "expected": "PASS"}],
    )
    details = compare_observed_to_expected({"status": "PASS"}, oracle)
    assert all(d["passed"] for d in details)


def test_oracle_with_parameters():
    comparator = {"type": REGEX_MATCH, "path": "msg", "expected": "^hello"}
    result = run_comparator(comparator, {"msg": "hello world"})
    assert result["passed"]


def test_oracle_contains_comparator():
    comparator = {"type": CONTAINS, "path": "items", "expected": "target"}
    result = run_comparator(comparator, {"items": ["a", "target", "b"]})
    assert result["passed"]


def test_oracle_empty_comparators_defaults_to_status_match():
    oracle = EvaluationExpectedResult(
        expected_result_id="or-1",
        expected_status="PASS",
        comparators=[],
    )
    details = compare_observed_to_expected({"msg": "PASS"}, oracle)
    assert len(details) == 1
