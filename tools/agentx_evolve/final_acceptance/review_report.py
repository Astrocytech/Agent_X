import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceDeviation
from .artifact_writer import write_json_artifact, runtime_root

RELEASE_READY = "RELEASE_READY"
NOT_RELEASE_READY = "NOT_RELEASE_READY"
NOT_CLAIMED = "NOT_CLAIMED"


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(65536)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _resolve_artifact(repo_root: Path, name: str) -> Path:
    return runtime_root(repo_root) / name


def build_review_report(
    repo_root: Path,
    reviewed_commit: str | None,
    reviewed_branch: str | None,
    acceptance_mode: str,
    bootstrap_self: bool,
    final_verdict: str,
    implementation_rating: float,
    blockers: list[str],
    high_issues: list[str],
    non_blocking_followups: list[str],
    deviations: list[FinalAcceptanceDeviation],
    commands_run: list[dict[str, Any]],
    layer_statuses: dict[str, str],
    git_status_start: str,
    git_status_end: str,
    release_ready_status: str = NOT_CLAIMED,
    acceptance_scope_id: str = "",
) -> dict[str, Any]:
    rt = runtime_root(repo_root)

    evidence_freshness_path = _resolve_artifact(repo_root, "final_acceptance_evidence_freshness_report.json")
    evidence_manifest_path = _resolve_artifact(repo_root, "final_acceptance_evidence_manifest.json")
    runtime_artifact_path = _resolve_artifact(repo_root, "final_acceptance_runtime_artifact_report.json")
    release_readiness_path = _resolve_artifact(repo_root, "final_acceptance_release_readiness_report.json")
    completion_record_path = _resolve_artifact(repo_root, "final_acceptance_completion_record.json")
    layer_registry_path = _resolve_artifact(repo_root, "final_acceptance_layer_registry.json")

    def sha_or_none(p: Path) -> str | None:
        if p.exists():
            return _file_sha256(p)
        return None

    working_tree_start = "CLEAN" if not git_status_start else "HAS_CHANGES"
    working_tree_end = "CLEAN" if not git_status_end else "HAS_CHANGES"

    working_tree_start_status = (
        "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY"
        if working_tree_start == "CLEAN"
        else "HAS_CHANGES"
    )
    working_tree_end_status = (
        "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY"
        if working_tree_end == "CLEAN"
        else "HAS_CHANGES"
    )

    deviation_list: list[dict[str, Any]] = []
    for d in deviations:
        deviation_list.append({
            "deviation_id": d.deviation_id,
            "area": d.area,
            "description": d.description,
            "reason": d.reason,
            "accepted_status": d.accepted_status,
        })

    return {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_review_report.schema.json",
        "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "review_document_id": "FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD",
        "review_document_version": "v4.0",
        "reviewed_commit": reviewed_commit,
        "reviewed_branch": reviewed_branch,
        "reviewed_at": _make_timestamp(),
        "reviewer": "AGENTX_EVOLVE_FINAL_ACCEPTANCE",
        "acceptance_scope_id": acceptance_scope_id,
        "acceptance_mode": acceptance_mode,
        "bootstrap_mode_used": bootstrap_self,
        "working_tree_start_status": working_tree_start_status,
        "working_tree_end_status": working_tree_end_status,
        "commands_run": commands_run,
        "coverage_statuses": {},
        "layer_completion_matrix_path": str(layer_registry_path),
        "layer_completion_matrix_sha256": sha_or_none(layer_registry_path),
        "evidence_freshness_report_path": str(evidence_freshness_path),
        "evidence_freshness_report_sha256": sha_or_none(evidence_freshness_path),
        "evidence_manifest_path": str(evidence_manifest_path),
        "evidence_manifest_sha256": sha_or_none(evidence_manifest_path),
        "runtime_artifact_report_path": str(runtime_artifact_path),
        "runtime_artifact_report_sha256": sha_or_none(runtime_artifact_path),
        "release_readiness_report_path": str(release_readiness_path),
        "release_readiness_report_sha256": sha_or_none(release_readiness_path),
        "completion_record_path": str(completion_record_path),
        "completion_record_sha256": sha_or_none(completion_record_path),
        "self_hash_method": "canonicalize_self_hash_field",
        "blockers": blockers,
        "high_issues": high_issues,
        "non_blocking_followups": non_blocking_followups,
        "deviation_register": deviation_list,
        "release_ready_status": release_ready_status,
        "implementation_rating": implementation_rating,
        "final_verdict": final_verdict,
        "warnings": [],
        "errors": [],
    }


def write_review_report(data: dict[str, Any], repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_review_report.json", data)
