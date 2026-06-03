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


def test_baseline_loads_correctly_from_valid_file(tmp_path):
    data = {"baseline_id": "bl-1", "suite_id": "suite-1", "baseline_run_id": "run-1", "source_component": "test"}
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data))
    baseline = load_baseline(p)
    assert baseline.baseline_id == "bl-1"
    assert baseline.suite_id == "suite-1"


def test_baseline_missing_case_throws_error():
    p = Path("/nonexistent/baseline.json")
    with pytest.raises(FileNotFoundError):
        load_baseline(p)


def test_baseline_suite_id_mismatch_detected(tmp_path):
    data = {"baseline_id": "bl-1", "suite_id": "other-suite", "baseline_run_id": "run-1"}
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data))
    baseline = load_baseline(p)
    assert baseline.suite_id == "other-suite"


def test_baseline_schema_version_mismatch(tmp_path):
    data = {"schema_version": "2.0", "baseline_id": "bl-1", "suite_id": "s1", "baseline_run_id": "r1"}
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data))
    baseline = load_baseline(p)
    assert baseline.schema_version == "2.0"


def test_verify_baseline_hash_rejects_modified(tmp_path):
    data = {"baseline_id": "bl-1", "suite_id": "s1", "baseline_run_id": "run-1"}
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data, indent=2))
    sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
    baseline = EvaluationBaseline(baseline_id="bl-1", suite_id="s1", baseline_run_id="run-1", sha256=sha256)
    assert verify_baseline_hash(baseline, p)
    p.write_text(json.dumps({"baseline_id": "bl-1", "suite_id": "s1", "baseline_run_id": "run-1", "extra": "tampered"}, indent=2))
    assert not verify_baseline_hash(baseline, p)


def test_candidate_baseline_written_correctly(tmp_path):
    run = make_run()
    path = write_candidate_baseline(run, tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["baseline_id"] == "run-1"
    assert data["suite_id"] == "suite-1"
    assert data["source_component"] == "EvaluationHarness"


def test_candidate_baseline_includes_sha256(tmp_path):
    run = make_run()
    path = write_candidate_baseline(run, tmp_path)
    data = json.loads(path.read_text())
    assert "sha256" in data
    assert len(data["sha256"]) == 64
