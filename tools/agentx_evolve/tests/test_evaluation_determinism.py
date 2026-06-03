import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.evaluation_models import (
    stable_json_hash, new_eval_id, utc_now_iso, to_dict,
    EvaluationCaseResult, EVAL_PASS,
)
from agentx_evolve.evaluation.score_calculator import calculate_run_score
from agentx_evolve.evaluation.comparator_engine import run_comparator, compare_observed_to_expected
from agentx_evolve.evaluation.evaluation_models import EvaluationExpectedResult, EXACT_MATCH


def test_stable_json_hash_deterministic():
    payload = {"z": 1, "a": 2, "nested": {"d": 4, "c": 3}}
    h1 = stable_json_hash(payload)
    h2 = stable_json_hash(payload)
    assert h1 == h2


def test_stable_json_hash_key_order_independent():
    h1 = stable_json_hash({"b": 2, "a": 1})
    h2 = stable_json_hash({"a": 1, "b": 2})
    assert h1 == h2


def test_stable_json_hash_nested_key_order():
    h1 = stable_json_hash({"outer": {"z": 1, "a": 2}})
    h2 = stable_json_hash({"outer": {"a": 2, "z": 1}})
    assert h1 == h2


def test_run_comparator_deterministic():
    comp = {"type": EXACT_MATCH, "path": "", "expected": "hello"}
    observed = {"msg": "hello"}
    r1 = run_comparator(comp, observed)
    r2 = run_comparator(comp, observed)
    assert r1["passed"] == r2["passed"]
    assert r1["message"] == r2["message"]


def test_compare_observed_to_expected_deterministic():
    expected = EvaluationExpectedResult(
        expected_status="PASS",
        comparators=[{"type": EXACT_MATCH, "path": "status", "expected": "PASS"}],
    )
    observed = {"status": "PASS"}
    d1 = compare_observed_to_expected(observed, expected)
    d2 = compare_observed_to_expected(observed, expected)
    assert d1 == d2


def test_calculate_run_score_deterministic():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0, weight=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_PASS, passed=True, score=1.0, weight=1.0),
    ]
    s1 = calculate_run_score(results)
    s2 = calculate_run_score(results)
    assert s1.normalized_score == s2.normalized_score
    assert s1.weighted_score == s2.weighted_score


def test_to_dict_deterministic():
    r = EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)
    d1 = to_dict(r)
    d2 = to_dict(r)
    assert d1 == d2


def test_new_eval_id_unique():
    ids = {new_eval_id() for _ in range(100)}
    assert len(ids) == 100


def test_utc_now_iso_format_consistent():
    now1 = utc_now_iso()
    now2 = utc_now_iso()
    assert "T" in now1
    assert "T" in now2


def test_stable_json_hash_empty_dict():
    assert stable_json_hash({}) == stable_json_hash({})


def test_stable_json_hash_list_order_matters():
    h1 = stable_json_hash({"items": [1, 2]})
    h2 = stable_json_hash({"items": [2, 1]})
    assert h1 != h2
