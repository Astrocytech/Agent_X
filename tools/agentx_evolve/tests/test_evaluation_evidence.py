import pytest
import json
import hashlib
from pathlib import Path
from agentx_evolve.evaluation.evaluation_evidence import (
    write_evaluation_evidence_manifest, append_evaluation_run_history,
    append_evaluation_case_history, write_run_artifact,
    write_completion_record, hash_evidence_file,
)
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationCaseResult,
    EVAL_PASS,
)


def make_run(run_id="run-1", suite_id="suite-1"):
    return EvaluationRun(
        run_id=run_id,
        suite_id=suite_id,
        source_component="test",
        execution_mode="OFFLINE_FIXTURE",
        case_results=[
            EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
        ],
        artifact_refs=["artifact1.txt"],
        evidence_refs=["evidence1.json"],
    )


def test_write_evaluation_evidence_manifest(tmp_path):
    run = make_run()
    manifest = write_evaluation_evidence_manifest(run, tmp_path)
    assert manifest["run_id"] == "run-1"
    assert manifest["suite_id"] == "suite-1"
    assert manifest["final_decision"] == "DONE"


def test_write_evaluation_evidence_manifest_creates_file(tmp_path):
    run = make_run()
    write_evaluation_evidence_manifest(run, tmp_path)
    manifest_path = tmp_path / ".agentx-init" / "evaluation" / "evaluation_evidence_manifest.json"
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text())
    assert data["run_id"] == "run-1"


def test_write_evaluation_evidence_manifest_writes_run_artifact(tmp_path):
    run = make_run()
    write_evaluation_evidence_manifest(run, tmp_path)
    runs_dir = tmp_path / ".agentx-init" / "evaluation" / "runs"
    assert len(list(runs_dir.glob("*.json"))) == 1


def test_append_evaluation_run_history(tmp_path):
    run = make_run()
    result = append_evaluation_run_history(run, tmp_path)
    assert "path" in result
    history_path = Path(result["path"])
    assert history_path.exists()
    lines = history_path.read_text().strip().split("\n")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["run_id"] == "run-1"


def test_append_evaluation_run_history_appends(tmp_path):
    run = make_run()
    append_evaluation_run_history(run, tmp_path)
    append_evaluation_run_history(run, tmp_path)
    history_path = tmp_path / ".agentx-init" / "evaluation" / "evaluation_run_history.jsonl"
    lines = history_path.read_text().strip().split("\n")
    assert len(lines) == 2


def test_append_evaluation_case_history(tmp_path):
    case = EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True)
    result = append_evaluation_case_history(case, tmp_path)
    assert "path" in result
    history_path = Path(result["path"])
    assert history_path.exists()
    data = json.loads(history_path.read_text().strip())
    assert data["case_id"] == "c1"


def test_write_run_artifact(tmp_path):
    run = make_run()
    path = write_run_artifact(run, tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["run_id"] == "run-1"


def test_write_run_artifact_directory_created(tmp_path):
    run = make_run()
    path = write_run_artifact(run, tmp_path)
    assert path.parent.exists()


def test_write_completion_record(tmp_path):
    run = make_run()
    run.repo_commit = "abc123"
    record = write_completion_record(run, tmp_path)
    assert record["status"] == "VALIDATED"
    assert record["validated_commit"] == "abc123"
    assert record["final_decision"] == "DONE"


def test_write_completion_record_creates_file(tmp_path):
    run = make_run()
    run.repo_commit = "abc123"
    write_completion_record(run, tmp_path)
    record_path = tmp_path / ".agentx-init" / "evaluation" / "evaluation_completion_record.json"
    assert record_path.exists()
    data = json.loads(record_path.read_text())
    assert data["status"] == "VALIDATED"


def test_hash_evidence_file(tmp_path):
    f = tmp_path / "evidence.json"
    f.write_text('{"key": "value"}')
    h = hash_evidence_file(f)
    assert isinstance(h, str)
    assert len(h) == 64
    expected = hashlib.sha256(f.read_bytes()).hexdigest()
    assert h == expected


def test_hash_evidence_file_empty(tmp_path):
    f = tmp_path / "empty.json"
    f.write_text("")
    h = hash_evidence_file(f)
    assert len(h) == 64
