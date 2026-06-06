import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.benchmark_loader import (
    load_benchmark_suite, load_benchmark_case, load_benchmark_cases,
    load_threshold, resolve_case_refs,
)
from agentx_evolve.evaluation.evaluation_models import BenchmarkSuite, BenchmarkCase, EvaluationThreshold


def test_load_benchmark_suite(tmp_path):
    data = {
        "suite_id": "suite-1",
        "suite_name": "Test Suite",
        "case_refs": ["case1.json"],
    }
    p = tmp_path / "suite.json"
    p.write_text(json.dumps(data))
    suite = load_benchmark_suite(p)
    assert isinstance(suite, BenchmarkSuite)
    assert suite.suite_id == "suite-1"
    assert suite.case_refs == ["case1.json"]


def test_load_benchmark_suite_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_benchmark_suite(Path("/nonexistent/suite.json"))


def test_load_benchmark_suite_unknown_fields_ignored(tmp_path):
    data = {"suite_id": "s1", "extra_field": "ignored"}
    p = tmp_path / "suite.json"
    p.write_text(json.dumps(data))
    suite = load_benchmark_suite(p)
    assert suite.suite_id == "s1"
    assert not hasattr(suite, "extra_field")


def test_load_benchmark_case(tmp_path):
    data = {"case_id": "case-1", "case_type": "STATIC_EXPECTED_RESULT", "input_payload": {"key": "val"}}
    p = tmp_path / "case.json"
    p.write_text(json.dumps(data))
    case = load_benchmark_case(p)
    assert isinstance(case, BenchmarkCase)
    assert case.case_id == "case-1"
    assert case.input_payload == {"key": "val"}


def test_load_benchmark_case_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_benchmark_case(Path("/missing/case.json"))


def test_load_benchmark_case_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not json")
    with pytest.raises(json.JSONDecodeError):
        load_benchmark_case(p)


def test_load_benchmark_cases(tmp_path):
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    suite_data = {
        "suite_id": "s1",
        "case_refs": ["case1.json", "case2.json"],
    }
    suite_p = tmp_path / "suite.json"
    suite_p.write_text(json.dumps(suite_data))
    suite = load_benchmark_suite(suite_p)
    for ref in ["case1.json", "case2.json"]:
        (fixture_root / ref).write_text(json.dumps({"case_id": ref.replace(".json", ""), "case_type": "STATIC_EXPECTED_RESULT"}))
    cases = load_benchmark_cases(suite, fixture_root)
    assert len(cases) == 2
    assert all(isinstance(c, BenchmarkCase) for c in cases)


def test_load_benchmark_cases_file_missing(tmp_path):
    suite_data = {"suite_id": "s1", "case_refs": ["missing.json"]}
    suite_p = tmp_path / "suite.json"
    suite_p.write_text(json.dumps(suite_data))
    suite = load_benchmark_suite(suite_p)
    with pytest.raises(FileNotFoundError):
        load_benchmark_cases(suite, tmp_path)


def test_load_benchmark_cases_path_traversal_rejected(tmp_path):
    suite_data = {"suite_id": "s1", "case_refs": ["../../etc/passwd"]}
    suite_p = tmp_path / "suite.json"
    suite_p.write_text(json.dumps(suite_data))
    suite = load_benchmark_suite(suite_p)
    with pytest.raises(ValueError, match="Path traversal"):
        load_benchmark_cases(suite, tmp_path)


def test_load_threshold(tmp_path):
    data = {"threshold_id": "th-1", "minimum_pass_rate": 0.9}
    p = tmp_path / "threshold.json"
    p.write_text(json.dumps(data))
    th = load_threshold(p)
    assert isinstance(th, EvaluationThreshold)
    assert th.threshold_id == "th-1"


def test_load_threshold_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_threshold(Path("/missing/threshold.json"))


def test_resolve_case_refs(tmp_path):
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    suite_data = {"suite_id": "s1", "case_refs": ["a.json", "b.json"]}
    suite_p = tmp_path / "suite.json"
    suite_p.write_text(json.dumps(suite_data))
    suite = load_benchmark_suite(suite_p)
    for ref in ["a.json", "b.json"]:
        (fixture_root / ref).write_text("{}")
    refs = resolve_case_refs(suite, fixture_root)
    assert len(refs) == 2
    assert all(isinstance(r, Path) for r in refs)


def test_resolve_case_refs_traversal_rejected(tmp_path):
    suite_data = {"suite_id": "s1", "case_refs": ["../outside.json"]}
    suite_p = tmp_path / "suite.json"
    suite_p.write_text(json.dumps(suite_data))
    suite = load_benchmark_suite(suite_p)
    with pytest.raises(ValueError, match="Path traversal"):
        resolve_case_refs(suite, tmp_path)
