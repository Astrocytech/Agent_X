import pytest
import json
import hashlib
from pathlib import Path
from agentx_evolve.evaluation.baseline_manager import (
    load_baseline, write_candidate_baseline, verify_baseline_hash,
)
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationBaseline, EvaluationCaseResult,
    EVAL_PASS, EVAL_FAIL,
)


def make_run(run_id="run-1", suite_id="suite-1"):
    return EvaluationRun(
        run_id=run_id,
        suite_id=suite_id,
        repo_commit="abc123",
        case_results=[
            EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
            EvaluationCaseResult(case_id="c2", status=EVAL_FAIL, passed=False, score=0.0),
        ],
        score_summary={"normalized_score": 0.5, "weighted_score": 0.5},
        artifact_refs=["a1"],
        evidence_refs=["e1"],
    )


def test_load_baseline(tmp_path):
    data = {
        "baseline_id": "bl-1",
        "suite_id": "suite-1",
        "baseline_run_id": "run-1",
        "source_component": "test",
    }
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data))
    baseline = load_baseline(p)
    assert isinstance(baseline, EvaluationBaseline)
    assert baseline.baseline_id == "bl-1"


def test_load_baseline_not_found():
    with pytest.raises(FileNotFoundError):
        load_baseline(Path("/missing/baseline.json"))


def test_load_baseline_unknown_fields_ignored(tmp_path):
    data = {"baseline_id": "bl-1", "suite_id": "s1", "extra": "ignored"}
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data))
    baseline = load_baseline(p)
    assert baseline.baseline_id == "bl-1"
    assert not hasattr(baseline, "extra")


def test_write_candidate_baseline(tmp_path):
    run = make_run()
    path = write_candidate_baseline(run, tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["baseline_id"] == "run-1"
    assert data["suite_id"] == "suite-1"
    assert data["source_component"] == "EvaluationHarness"


def test_write_candidate_baseline_creates_dir(tmp_path):
    run = make_run()
    path = write_candidate_baseline(run, tmp_path)
    assert path.parent.exists()


def test_write_candidate_baseline_includes_sha256(tmp_path):
    run = make_run()
    path = write_candidate_baseline(run, tmp_path)
    data = json.loads(path.read_text())
    assert "sha256" in data
    assert len(data["sha256"]) == 64


def test_write_candidate_baseline_case_result_index(tmp_path):
    run = make_run()
    path = write_candidate_baseline(run, tmp_path)
    data = json.loads(path.read_text())
    assert "c1" in data["case_result_index"]
    assert data["case_result_index"]["c1"]["status"] == EVAL_PASS


def test_verify_baseline_hash_match(tmp_path):
    data = {
        "baseline_id": "bl-1",
        "suite_id": "s1",
        "baseline_run_id": "run-1",
        "source_component": "test",
    }
    p = tmp_path / "baseline.json"
    content = json.dumps(data, indent=2)
    p.write_text(content)
    sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
    baseline = EvaluationBaseline(baseline_id="bl-1", suite_id="s1", baseline_run_id="run-1", sha256=sha256)
    assert verify_baseline_hash(baseline, p)


def test_verify_baseline_hash_mismatch(tmp_path):
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps({"baseline_id": "bl-1"}))
    baseline = EvaluationBaseline(baseline_id="bl-1", suite_id="s1", baseline_run_id="r1", sha256="wronghash")
    assert not verify_baseline_hash(baseline, p)


def test_verify_baseline_hash_file_missing(tmp_path):
    baseline = EvaluationBaseline(baseline_id="bl-1", suite_id="s1", baseline_run_id="r1", sha256="hash")
    assert not verify_baseline_hash(baseline, tmp_path / "missing.json")


def test_verify_baseline_hash_none_sha256(tmp_path):
    p = tmp_path / "baseline.json"
    p.write_text("{}")
    baseline = EvaluationBaseline(baseline_id="bl-1", suite_id="s1", baseline_run_id="r1", sha256=None)
    result = verify_baseline_hash(baseline, p)
    assert not result
