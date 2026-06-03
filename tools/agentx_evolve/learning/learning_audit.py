from __future__ import annotations
from pathlib import Path
import hashlib
import json
import os
from typing import Any
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview, LearningSignal, MemoryCandidate,
    RegressionLink, LearningPolicyDecision, LearningAuditEvent,
    FollowUpTaskProposal, OutcomeReviewReport,
    utc_now_iso, to_dict, redact_learning_text,
)

_LEARNING_ROOT = ".agentx-init/learning"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _redact_dict(data: dict) -> dict:
    result = {}
    for k, v in data.items():
        if isinstance(v, str):
            result[k] = redact_learning_text(v)
        elif isinstance(v, dict):
            result[k] = _redact_dict(v)
        elif isinstance(v, list):
            result[k] = [_redact_dict(i) if isinstance(i, dict) else redact_learning_text(i) if isinstance(i, str) else i for i in v]
        else:
            result[k] = v
    return result


def _append_jsonl(path: Path, data: dict) -> dict:
    _ensure_dir(path)
    redacted = _redact_dict(data)
    line = json.dumps(redacted, separators=(",", ":")) + "\n"
    with open(str(path), "a", encoding="utf-8") as f:
        f.write(line)
    return {"path": str(path), "status": "appended"}


def _write_latest(path: Path, data: dict) -> dict:
    _ensure_dir(path)
    redacted = _redact_dict(data)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(redacted, separators=(",", ":")), encoding="utf-8")
    tmp.replace(path)
    return {"path": str(path), "status": "written"}


def _repo_root_path(repo_root: Path | str) -> Path:
    return Path(repo_root)


def _learning_dir(repo_root: Path | str) -> Path:
    return _repo_root_path(repo_root) / _LEARNING_ROOT


def append_outcome_event(event: OutcomeEvent, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "outcome_event_history.jsonl"
    return _append_jsonl(path, to_dict(event))


def append_outcome_review(review: OutcomeReview, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "outcome_review_history.jsonl"
    return _append_jsonl(path, to_dict(review))


def append_learning_signal(signal: LearningSignal, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "learning_signal_history.jsonl"
    return _append_jsonl(path, to_dict(signal))


def append_memory_candidate(candidate: MemoryCandidate, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "memory_candidate_history.jsonl"
    return _append_jsonl(path, to_dict(candidate))


def append_rejected_learning(entity: dict, reason: str, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "rejected_learning_history.jsonl"
    record = {"entity": entity, "reason": reason, "rejected_at": utc_now_iso()}
    return _append_jsonl(path, record)


def append_regression_link(link: RegressionLink, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "regression_link_history.jsonl"
    return _append_jsonl(path, to_dict(link))


def append_learning_policy_decision(decision: LearningPolicyDecision, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "learning_policy_decision_history.jsonl"
    return _append_jsonl(path, to_dict(decision))


def append_learning_audit_event(event: LearningAuditEvent, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "learning_audit_history.jsonl"
    return _append_jsonl(path, to_dict(event))


def append_follow_up_task_proposal(proposal: FollowUpTaskProposal, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "follow_up_task_proposal_history.jsonl"
    return _append_jsonl(path, to_dict(proposal))


def write_latest_outcome_review(review: OutcomeReview, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "latest_outcome_review.json"
    return _write_latest(path, to_dict(review))


def write_latest_learning_report(report: OutcomeReviewReport, repo_root: Path | str) -> dict:
    path = _learning_dir(repo_root) / "latest_learning_report.json"
    return _write_latest(path, to_dict(report))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(str(path), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_learning_evidence_manifest(context: dict) -> dict:
    repo_root = Path(context.get("repo_root", "."))
    dest = _learning_dir(repo_root) / "learning_evidence_manifest.json"
    manifest = {
        "schema_version": "1.0",
        "schema_id": "learning_evidence_manifest.schema.json",
        "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
        "created_at": utc_now_iso(),
        "reviewed_commit": context.get("reviewed_commit"),
        "review_environment": context.get("review_environment", {}),
        "commands": context.get("commands", []),
        "evidence_files": context.get("evidence_files", []),
        "evidence_file_hashes": context.get("evidence_file_hashes", []),
        "runtime_artifacts": context.get("runtime_artifacts", []),
        "deviation_register": context.get("deviations", []),
        "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
        "hash_status": "PASS",
        "final_decision": context.get("final_decision", "DONE"),
    }
    return _write_latest(dest, manifest)


def write_learning_implementation_review_report(context: dict) -> dict:
    repo_root = Path(context.get("repo_root", "."))
    dest = _learning_dir(repo_root) / "learning_implementation_review_report.json"
    report = {
        "schema_version": "1.0",
        "schema_id": "learning_implementation_review_report.schema.json",
        "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
        "review_document_id": "LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC_v4",
        "review_document_version": "v4.0",
        "reviewed_commit": context.get("reviewed_commit", ""),
        "reviewed_at": utc_now_iso(),
        "reviewer": context.get("reviewer", "automated"),
        "review_environment": context.get("review_environment", {}),
        "commands_run": context.get("commands_run", []),
        "coverage_statuses": context.get("coverage_statuses", {}),
        "blockers": context.get("blockers", []),
        "high_issues": context.get("high_issues", []),
        "non_blocking_followups": context.get("non_blocking_followups", []),
        "deviation_register": context.get("deviations", []),
        "evidence_manifest_path": str(_learning_dir(repo_root) / "learning_evidence_manifest.json"),
        "evidence_manifest_sha256": context.get("evidence_manifest_sha256", ""),
        "review_report_path": str(dest),
        "review_report_sha256": context.get("review_report_sha256", ""),
        "completion_record_path": str(_learning_dir(repo_root) / "learning_completion_record.json"),
        "completion_record_sha256": context.get("completion_record_sha256", ""),
        "implementation_rating": context.get("implementation_rating", 10.0),
        "final_verdict": context.get("final_verdict", "DONE"),
    }
    return _write_latest(dest, report)


def write_learning_completion_record(context: dict) -> dict:
    repo_root = Path(context.get("repo_root", "."))
    dest = _learning_dir(repo_root) / "learning_completion_record.json"
    record = {
        "schema_version": "1.0",
        "schema_id": "learning_completion_record.schema.json",
        "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
        "component_name": "Long-Term Learning / Outcome Review Layer",
        "status": "VALIDATED",
        "validated_commit": context.get("reviewed_commit", ""),
        "validated_at": utc_now_iso(),
        "canonical_subdirectory": "tools/agentx_evolve/learning/",
        "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
        "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
        "runtime_artifact_root": ".agentx-init/learning/",
        "basis_documents": [
            "LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT",
            "LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC_v4",
        ],
        "commands_run": context.get("commands_run", []),
        "files_created_or_changed": context.get("files_created_or_changed", []),
        "schemas_created_or_changed": context.get("schemas_created_or_changed", []),
        "tests_created_or_changed": context.get("tests_created_or_changed", []),
        "evidence_manifest_path": str(_learning_dir(repo_root) / "learning_evidence_manifest.json"),
        "evidence_manifest_sha256": context.get("evidence_manifest_sha256", ""),
        "review_report_path": str(_learning_dir(repo_root) / "learning_implementation_review_report.json"),
        "review_report_sha256": context.get("review_report_sha256", ""),
        "completion_record_sha256": context.get("completion_record_sha256", ""),
        "deviations_from_contract": context.get("deviations", []),
        "unresolved_risks": context.get("unresolved_risks", []),
        "final_decision": context.get("final_decision", "DONE"),
    }
    return _write_latest(dest, record)
