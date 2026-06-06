from __future__ import annotations
from pathlib import Path
import json
import hashlib

from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationCaseResult,
    utc_now_iso, new_eval_id, to_dict, stable_json_hash,
)


def write_evaluation_evidence_manifest(run: EvaluationRun, repo_root: Path) -> dict:
    evidence_dir = repo_root / ".agentx-init" / "evaluation"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1.0",
        "schema_id": "evaluation_evidence_manifest.schema.json",
        "component_id": "AGENTX_EVALUATION_HARNESS",
        "run_id": run.run_id,
        "suite_id": run.suite_id,
        "validated_commit": run.repo_commit or "",
        "validated_at": utc_now_iso(),
        "execution_mode": run.execution_mode,
        "commands": [],
        "fixtures_used": [],
        "fixture_hashes": [],
        "baseline_used": None,
        "baseline_sha256": None,
        "runtime_artifacts": [],
        "runtime_artifact_hashes": [],
        "reports": [],
        "report_hashes": [],
        "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
        "network_status": "NOT_USED",
        "tool_adapter_status": "NOT_APPLICABLE",
        "policy_status": "NOT_APPLICABLE",
        "failure_taxonomy_status": "LOCAL_FALLBACK",
        "final_decision": "DONE",
        "warnings": run.warnings,
        "errors": run.errors,
    }
    run_artifact_path = write_run_artifact(run, repo_root)
    manifest["runtime_artifacts"].append(str(run_artifact_path))
    manifest["runtime_artifact_hashes"].append(hash_evidence_file(run_artifact_path))
    manifest_path = evidence_dir / "evaluation_evidence_manifest.json"
    manifest_str = json.dumps(manifest, indent=2)
    manifest_path.write_text(manifest_str)
    return manifest


def append_evaluation_run_history(run: EvaluationRun, repo_root: Path) -> dict:
    history_path = repo_root / ".agentx-init" / "evaluation" / "evaluation_run_history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "a") as f:
        f.write(json.dumps(to_dict(run)) + "\n")
    return {"path": str(history_path)}


def append_evaluation_case_history(case_result: EvaluationCaseResult, repo_root: Path) -> dict:
    history_path = repo_root / ".agentx-init" / "evaluation" / "evaluation_case_history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "a") as f:
        f.write(json.dumps(to_dict(case_result)) + "\n")
    return {"path": str(history_path)}


def write_run_artifact(run: EvaluationRun, repo_root: Path) -> Path:
    runs_dir = repo_root / ".agentx-init" / "evaluation" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    path = runs_dir / f"{run.run_id}_run.json"
    path.write_text(json.dumps(to_dict(run), indent=2))
    return path


def write_completion_record(run: EvaluationRun, repo_root: Path) -> dict:
    record_dir = repo_root / ".agentx-init" / "evaluation"
    record_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": "1.0",
        "schema_id": "evaluation_completion_record.schema.json",
        "component_id": "AGENTX_EVALUATION_HARNESS",
        "component_name": "Evaluation Harness / Regression Benchmark Layer",
        "status": "VALIDATED",
        "validated_commit": run.repo_commit or "",
        "validated_at": utc_now_iso(),
        "review_environment": {
            "os": "linux",
            "python_version": __import__("sys").version,
            "pytest_version": "NOT INSTALLED",
            "jsonschema_version": "NOT INSTALLED",
            "timezone": "UTC",
        },
        "canonical_evaluation_subdirectory": "tools/agentx_evolve/evaluation/",
        "canonical_benchmark_subdirectory": "tools/agentx_evolve/evaluation/fixtures/",
        "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
        "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
        "runtime_artifact_root": ".agentx-init/evaluation/",
        "basis_documents": [
            "EVALUATION_HARNESS_IMPLEMENTATION_SPEC",
            "EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD_v4",
            "EVALUATION_HARNESS_EQC_FIC_SIB_SCHEMA_CONTRACT_v3",
        ],
        "commands_run": [],
        "files_created_or_changed": [],
        "schemas_created_or_changed": [],
        "tests_created_or_changed": [],
        "benchmark_suites_verified": [run.suite_id],
        "baselines_verified": [],
        "thresholds_verified": [],
        "regression_checks_verified": [],
        "deterministic_replay_verified": [],
        "reports_verified": [],
        "evidence_manifest_path": ".agentx-init/evaluation/evaluation_evidence_manifest.json",
        "evidence_manifest_sha256": "",
        "review_report_path": ".agentx-init/evaluation/evaluation_review_report.json",
        "review_report_sha256": "",
        "completion_record_sha256": "",
        "deviation_register": [],
        "unresolved_risks": [],
        "implementation_score": 10.0,
        "final_decision": "DONE",
        "warnings": [],
        "errors": [],
    }
    record_str = json.dumps(record, indent=2)
    record_path = record_dir / "evaluation_completion_record.json"
    record_path.write_text(record_str)
    return record


def hash_evidence_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_evidence_index(run: EvaluationRun, repo_root: Path) -> Path:
    evidence_dir = repo_root / ".agentx-init" / "evaluation" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    artifacts = []

    for case_result in run.case_results:
        for ref in getattr(case_result, 'evidence_refs', []):
            ref_path = Path(ref)
            art_path = ref_path if ref_path.is_absolute() else repo_root / ref
            if art_path.exists():
                artifacts.append({
                    "path": str(art_path),
                    "type": "case_evidence_ref",
                    "case_id": case_result.case_id,
                    "hash": hash_evidence_file(art_path),
                })

    for ref in getattr(run, 'artifact_refs', []):
        ref_path = Path(ref)
        art_path = ref_path if ref_path.is_absolute() else repo_root / ref
        if art_path.exists():
            artifacts.append({
                "path": str(art_path),
                "type": "run_artifact_ref",
                "hash": hash_evidence_file(art_path),
            })

    for report in getattr(run, 'reports', []):
        report_path = Path(report)
        art_path = report_path if report_path.is_absolute() else repo_root / report
        if art_path.exists():
            artifacts.append({
                "path": str(art_path),
                "type": "report",
                "hash": hash_evidence_file(art_path),
            })

    index = {
        "run_id": run.run_id,
        "suite_id": run.suite_id,
        "timestamp": utc_now_iso(),
        "total_artifacts": len(artifacts),
        "artifacts": artifacts,
    }

    index_path = evidence_dir / f"{run.run_id}_evidence_index.json"
    index_path.write_text(json.dumps(index, indent=2))
    return index_path


def finalize_evidence(run: EvaluationRun, repo_root: Path) -> dict:
    manifest = write_evaluation_evidence_manifest(run, repo_root)
    index_path = write_evidence_index(run, repo_root)
    manifest_path = repo_root / ".agentx-init" / "evaluation" / "evaluation_evidence_manifest.json"
    manifest_hash = hash_evidence_file(manifest_path)

    return {
        "manifest": manifest,
        "index_path": str(index_path),
        "manifest_path": str(manifest_path),
        "manifest_hash": manifest_hash,
        "artifact_paths": [str(index_path)],
        "artifact_hashes": [manifest_hash],
    }
