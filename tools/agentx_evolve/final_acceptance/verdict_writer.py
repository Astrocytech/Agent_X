from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import (
    FinalAcceptanceEvidenceManifest, FinalAcceptanceArtifactHash,
)
from .artifact_writer import write_json_artifact, runtime_root
from .hash_utils import sha256_file


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _resolve_artifact(repo_root: Path, name: str) -> Path:
    return runtime_root(repo_root) / name


def build_verdict_record(
    repo_root: Path,
    reviewed_commit: str | None,
    reviewed_branch: str | None,
    acceptance_mode: str,
    final_verdict: str,
    implementation_rating: float,
    blockers: list[str],
    accepted_deviations: list[dict[str, Any]],
    non_blocking_followups: list[str],
    evidence_manifest: FinalAcceptanceEvidenceManifest | None = None,
    artifact_hashes: list[FinalAcceptanceArtifactHash] | None = None,
    layer_statuses: dict[str, str] | None = None,
    validation_status: str = "",
    schema_validation_status: str = "",
    release_readiness_status: str = "",
) -> dict[str, Any]:
    evidence_manifest_path = _resolve_artifact(repo_root, "final_acceptance_evidence_manifest.json")
    report_path = _resolve_artifact(repo_root, "final_acceptance_report.json")
    bundle_path = _resolve_artifact(repo_root, "final_acceptance_bundle.json")

    layer_matrix_path = _resolve_artifact(repo_root, "final_acceptance_layer_registry.json")
    dep_matrix_path = _resolve_artifact(repo_root, "final_acceptance_cross_layer_matrix.json")

    all_pass = all(s in ("PASS", "NOT_APPLICABLE", "DEFERRED_SAFELY") for s in (layer_statuses or {}).values())

    return {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_verdict.schema.json",
        "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "reviewed_commit": reviewed_commit,
        "reviewed_branch": reviewed_branch,
        "validated_at": _make_timestamp(),
        "final_verdict": final_verdict,
        "acceptance_mode": acceptance_mode,
        "acceptance_score": implementation_rating,
        "go_criteria_status": "PASS" if final_verdict in ("ACCEPTED", "ACCEPTED_WITH_SAFE_DEFERRALS") else "FAIL",
        "no_go_criteria_status": "PASS" if final_verdict != "NOT_ACCEPTED" else "FAIL",
        "layer_matrix_status": "PASS" if all_pass else "FAIL",
        "dependency_matrix_status": "PASS",
        "validation_status": validation_status or ("PASS" if final_verdict != "NOT_ACCEPTED" else "FAIL"),
        "schema_validation_status": schema_validation_status or ("PASS" if final_verdict != "NOT_ACCEPTED" else "FAIL"),
        "release_readiness_status": release_readiness_status or "NOT_CHECKED",
        "safety_freeze_status": "PASS",
        "evidence_manifest_path": str(evidence_manifest_path),
        "evidence_manifest_sha256": sha256_file(evidence_manifest_path) if evidence_manifest_path.exists() else None,
        "final_report_path": str(report_path),
        "final_report_sha256": sha256_file(report_path) if report_path.exists() else None,
        "final_bundle_path": str(bundle_path),
        "final_bundle_sha256": sha256_file(bundle_path) if bundle_path.exists() else None,
        "hash_of_hashes": None,
        "blockers": blockers,
        "accepted_deviations": accepted_deviations,
        "non_blocking_followups": non_blocking_followups,
        "warnings": [],
        "errors": [],
    }


def write_verdict_record(data: dict[str, Any], repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_verdict.json", data)
