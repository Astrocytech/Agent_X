import pytest
import json
import os
import tempfile

from agentx_evolve.evaluation.evaluation_harness import (
    GoldenTask, EvalResult, EvalSuiteResult, EvaluationHarness, QualityScorecard,
    ES_PASS, ES_FAIL, ES_NOT_RUN, ALL_EVAL_STATUSES, ALL_TASK_TYPES,
    sha256_dict, to_canonical_json,
)


def test_constants():
    assert ES_PASS == "PASS"
    assert ES_FAIL == "FAIL"
    assert ES_NOT_RUN == "NOT_RUN"
    assert len(ALL_EVAL_STATUSES) == 3
    assert "IMPLEMENT_PATCH" in ALL_TASK_TYPES
    assert "SECURITY" in ALL_TASK_TYPES
    assert "ORCHESTRATOR" in ALL_TASK_TYPES


def test_sha256_dict_produces_digest():
    task = GoldenTask(task_id="t1", description="test")
    h = sha256_dict(task)
    assert isinstance(h, str)
    assert len(h) == 64


def test_to_canonical_json_roundtrip():
    task = GoldenTask(task_id="t1", description="test")
    raw = to_canonical_json(task)
    data = json.loads(raw)
    assert data["task_id"] == "t1"
    assert data["description"] == "test"


def test_register_task_adds_task():
    harness = EvaluationHarness()
    task = GoldenTask(task_id="gt-1", description="first")
    harness.register_task(task)
    assert harness.get_task("gt-1") is task


def test_run_suite_with_all_tasks_returns_results():
    harness = EvaluationHarness()
    harness.register_task(GoldenTask(task_id="gt-a"))
    harness.register_task(GoldenTask(task_id="gt-b"))
    suite = harness.run_suite()
    assert suite.total == 2
    assert suite.passed == 2
    assert suite.failed == 0
    assert len(suite.results) == 2
    assert suite.suite_id.startswith("eval-")


def test_eval_suite_result_pass_rate():
    suite = EvalSuiteResult(total=4, passed=3, failed=1)
    assert suite.pass_rate == 0.75
    suite2 = EvalSuiteResult()
    assert suite2.pass_rate == 1.0


def test_quality_scorecard_set_and_get():
    sc = QualityScorecard()
    assert sc.get_score("accuracy") == 0.0
    sc.set_score("accuracy", 0.85)
    assert sc.get_score("accuracy") == 0.85
    sc.set_score("accuracy", -0.5)
    assert sc.get_score("accuracy") == 0.0


def test_quality_scorecard_average():
    sc = QualityScorecard()
    assert sc.average() == 1.0
    sc.set_score("a", 0.5)
    sc.set_score("b", 1.0)
    assert sc.average() == 0.75


def test_write_suite_result_creates_file(tmp_path):
    harness = EvaluationHarness()
    original_dir = os.path.abspath(".agentx-init")
    suite = EvalSuiteResult(suite_id="test-suite-1", total=1, passed=1)
    path = harness.write_suite_result(suite)
    saved_path = path
    try:
        assert os.path.exists(saved_path)
        with open(saved_path) as f:
            data = json.load(f)
        assert data["suite_id"] == "test-suite-1"
    finally:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        for root, dirs, files in os.walk(".agentx-init", topdown=False):
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except OSError:
                    pass


def test_append_suite_history_appends(tmp_path):
    harness = EvaluationHarness()
    suite1 = EvalSuiteResult(suite_id="s1", total=1, passed=1)
    suite2 = EvalSuiteResult(suite_id="s2", total=1, passed=0)
    path1 = harness.append_suite_history(suite1)
    path2 = harness.append_suite_history(suite2)
    try:
        assert path1 == path2
        assert os.path.exists(path1)
        with open(path1) as f:
            lines = f.read().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["suite_id"] == "s1"
        assert json.loads(lines[1])["suite_id"] == "s2"
    finally:
        if os.path.exists(path1):
            os.remove(path1)


def test_list_tasks_by_tag():
    harness = EvaluationHarness()
    t1 = GoldenTask(task_id="gt-a", tags=["core", "patch"])
    t2 = GoldenTask(task_id="gt-b", tags=["core", "security"])
    t3 = GoldenTask(task_id="gt-c", tags=["extra"])
    harness.register_task(t1)
    harness.register_task(t2)
    harness.register_task(t3)
    core_tasks = harness.list_tasks(tag="core")
    assert len(core_tasks) == 2
    assert {t.task_id for t in core_tasks} == {"gt-a", "gt-b"}
    security_tasks = harness.list_tasks(tag="security")
    assert len(security_tasks) == 1
    assert security_tasks[0].task_id == "gt-b"
    all_tasks = harness.list_tasks()
    assert len(all_tasks) == 3


def test_latest_suite_returns_last():
    harness = EvaluationHarness()
    harness.register_task(GoldenTask(task_id="gt-1"))
    assert harness.latest_suite() is None
    s1 = harness.run_suite(task_ids=["gt-1"])
    s2 = harness.run_suite(task_ids=["gt-1"])
    assert harness.latest_suite() is s2
    assert harness.latest_suite() is not s1


def test_write_scorecard_persists(tmp_path):
    sc = QualityScorecard()
    sc.set_score("accuracy", 0.9)
    sc.set_score("coverage", 0.75)
    path = os.path.join(str(tmp_path), "scorecard.json")
    result_path = sc.write_scorecard(path)
    assert result_path == path
    assert os.path.exists(path)
    with open(path) as f:
        data = json.load(f)
    assert data["scores"]["accuracy"] == 0.9


def test_load_scorecard_roundtrip(tmp_path):
    sc = QualityScorecard()
    sc.set_score("accuracy", 0.9)
    path = os.path.join(str(tmp_path), "scorecard.json")
    sc.write_scorecard(path)
    loaded = QualityScorecard.load_scorecard(path)
    assert loaded.get_score("accuracy") == 0.9


def test_eval_result_hash():
    r1 = EvalResult(task_id="t1", passed=True)
    r2 = EvalResult(task_id="t1", passed=True)
    r3 = EvalResult(task_id="t2", passed=True)
    assert r1.result_hash == r2.result_hash
    assert r1.result_hash != r3.result_hash


def test_suite_hash():
    s1 = EvalSuiteResult(suite_id="s1")
    s2 = EvalSuiteResult(suite_id="s1")
    s3 = EvalSuiteResult(suite_id="s2")
    assert s1.suite_hash == s2.suite_hash
    assert s1.suite_hash != s3.suite_hash


def test_harness_acquire_release_lock():
    harness = EvaluationHarness()
    harness.acquire_lock()
    harness.release_lock()


def test_harness_validate_against_schema():
    harness = EvaluationHarness()
    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string"}},
    }
    errs = harness.validate_against_schema({"name": "ok"}, schema)
    assert errs == []
    errs2 = harness.validate_against_schema({"name": 42}, schema)
    assert len(errs2) > 0


def test_harness_run_suite_with_custom_evaluator():
    harness = EvaluationHarness()
    harness.register_task(GoldenTask(task_id="gt-fail"))
    harness.register_task(GoldenTask(task_id="gt-pass"))

    def custom_eval(task):
        if task.task_id == "gt-fail":
            return EvalResult(task_id=task.task_id, passed=False, actual_outcome="failed")
        return EvalResult(task_id=task.task_id, passed=True, actual_outcome="passed")

    suite = harness.run_suite(evaluator=custom_eval)
    assert suite.total == 2
    assert suite.passed == 1
    assert suite.failed == 1
    assert suite.results[0].actual_outcome == "failed"
    assert suite.results[1].actual_outcome == "passed"


def test_harness_list_suites():
    harness = EvaluationHarness()
    harness.register_task(GoldenTask(task_id="gt-1"))
    assert harness.list_suites() == []
    s1 = harness.run_suite()
    assert harness.list_suites() == [s1]
    s2 = harness.run_suite()
    assert harness.list_suites() == [s1, s2]
