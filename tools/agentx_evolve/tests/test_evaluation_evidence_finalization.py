import pytest
import json
import hashlib
from pathlib import Path
from agentx_evolve.evaluation.evaluation_evidence import (
    write_evaluation_evidence_manifest, write_run_artifact,
    hash_evidence_file, write_completion_record,
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


def test_write_evidence_index_creates_file(tmp_path):
    run = make_run()
    manifest = write_evaluation_evidence_manifest(run, tmp_path)
    manifest_path = tmp_path / ".agentx-init" / "evaluation" / "evaluation_evidence_manifest.json"
    assert manifest_path.exists()


def test_evidence_index_includes_case_evidence_refs(tmp_path):
    run = make_run()
    manifest = write_evaluation_evidence_manifest(run, tmp_path)
    assert manifest["run_id"] == "run-1"


def test_evidence_index_includes_run_artifact_refs(tmp_path):
    run = make_run()
    manifest = write_evaluation_evidence_manifest(run, tmp_path)
    assert len(manifest["runtime_artifacts"]) >= 1
    assert all(isinstance(a, str) for a in manifest["runtime_artifacts"])


def test_evidence_index_hashes_each_artifact(tmp_path):
    run = make_run()
    manifest = write_evaluation_evidence_manifest(run, tmp_path)
    assert len(manifest["runtime_artifact_hashes"]) >= 1
    for h in manifest["runtime_artifact_hashes"]:
        assert len(h) == 64


def test_finalize_evidence_returns_artifact_paths_and_hashes(tmp_path):
    run = make_run()
    manifest = write_evaluation_evidence_manifest(run, tmp_path)
    artifact_path = manifest["runtime_artifacts"][0]
    artifact_hash = manifest["runtime_artifact_hashes"][0]
    assert isinstance(artifact_path, str)
    assert len(artifact_hash) == 64


def test_evidence_manifest_sha256_computed_correctly(tmp_path):
    run = make_run()
    write_evaluation_evidence_manifest(run, tmp_path)
    manifest_path = tmp_path / ".agentx-init" / "evaluation" / "evaluation_evidence_manifest.json"
    content = manifest_path.read_bytes()
    expected = hashlib.sha256(content).hexdigest()
    actual = hash_evidence_file(manifest_path)
    assert actual == expected


def test_evidence_index_contains_run_id_suite_id_timestamp(tmp_path):
    run = make_run()
    manifest = write_evaluation_evidence_manifest(run, tmp_path)
    assert "run_id" in manifest
    assert "suite_id" in manifest
    assert "validated_at" in manifest
    assert manifest["run_id"] == "run-1"
    assert manifest["suite_id"] == "suite-1"
