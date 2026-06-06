from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import (
    FinalAcceptanceReport, FinalAcceptanceCompletionRecord,
    FinalAcceptanceLayerRegistry, FinalAcceptanceEvidenceManifest,
    CrossLayerCheck, FinalAcceptanceValidationResult, FinalAcceptanceDeviation,
    FinalAcceptanceArtifactHash,
    VERDICT_NOT_ACCEPTED, MODE_SOURCE_ONLY_ACCEPTANCE,
)
from .artifact_writer import write_json_artifact, atomic_write_json


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def build_final_acceptance_report(
    repo_root: Path,
    registry: FinalAcceptanceLayerRegistry,
    evidence_manifest: FinalAcceptanceEvidenceManifest | None = None,
    cross_layer_checks: list[CrossLayerCheck] | None = None,
    validation_results: list[FinalAcceptanceValidationResult] | None = None,
    schema_validation_results: list[FinalAcceptanceValidationResult] | None = None,
    deviations: list[FinalAcceptanceDeviation] | None = None,
    layer_statuses: dict[str, str] | None = None,
    final_verdict: str = VERDICT_NOT_ACCEPTED,
    implementation_rating: float = 0.0,
    safe_deferrals: list[dict[str, Any]] | None = None,
    blockers: list[str] | None = None,
    high_issues: list[str] | None = None,
    non_blocking_followups: list[str] | None = None,
    artifact_hashes: list[FinalAcceptanceArtifactHash] | None = None,
    artifact_hashes_path: str = "",
    artifact_hashes_content_id: str = "",
    artifact_hashes_sha256: str | None = None,
) -> FinalAcceptanceReport:
    layer_statuses = layer_statuses or {}
    safe_deferrals = safe_deferrals or []
    blockers = blockers or []
    high_issues = high_issues or []
    non_blocking_followups = non_blocking_followups or []
    artifact_hashes = artifact_hashes or []

    evidence_summary = {}
    if evidence_manifest:
        evidence_summary = {
            "total_items": len(evidence_manifest.items),
            "items_found": sum(1 for i in evidence_manifest.items if i.exists),
            "items_missing": sum(1 for i in evidence_manifest.items if not i.exists),
            "schema_valid": sum(1 for i in evidence_manifest.items if i.schema_valid),
            "schema_invalid": sum(1 for i in evidence_manifest.items if not i.schema_valid),
        }

    cross_layer_summary = {}
    if cross_layer_checks:
        cross_layer_summary = {
            "total_checks": len(cross_layer_checks),
            "passed": sum(1 for c in cross_layer_checks if c.status == "PASS"),
            "failed": sum(1 for c in cross_layer_checks if c.status == "FAIL"),
            "not_applicable": sum(1 for c in cross_layer_checks if c.status == "NOT_APPLICABLE"),
        }

    validation_summary = {}
    if validation_results:
        validation_summary = {
            "total_commands": len(validation_results),
            "passed": sum(1 for r in validation_results if r.status == "PASS"),
            "failed": sum(1 for r in validation_results if r.status == "FAIL"),
            "not_run": sum(1 for r in validation_results if r.status == "NOT_RUN"),
        }

    schema_val_summary = {}
    if schema_validation_results:
        schema_val_summary = {
            "total": len(schema_validation_results),
            "passed": sum(1 for r in schema_validation_results if r.status == "PASS"),
            "failed": sum(1 for r in schema_validation_results if r.status == "FAIL"),
        }

    return FinalAcceptanceReport(
        reviewed_commit=registry.reviewed_commit,
        reviewed_branch=registry.reviewed_branch,
        created_at=_make_timestamp(),
        acceptance_mode=registry.acceptance_mode,
        bootstrap_mode_used=registry.bootstrap_self,
        final_verdict=final_verdict,
        implementation_rating=implementation_rating,
        layer_statuses=layer_statuses,
        evidence_summary=evidence_summary,
        cross_layer_summary=cross_layer_summary,
        validation_summary=validation_summary,
        schema_validation_summary=schema_val_summary,
        safe_deferrals=safe_deferrals,
        deviations=[d.__dict__ if hasattr(d, '__dict__') else dict(d) for d in (deviations or [])],
        blockers=blockers,
        high_issues=high_issues,
        non_blocking_followups=non_blocking_followups,
        artifact_hashes=[h.__dict__ if hasattr(h, '__dict__') else dict(h) for h in artifact_hashes],
        artifact_hashes_path=artifact_hashes_path,
        artifact_hashes_content_id=artifact_hashes_content_id,
        artifact_hashes_sha256=artifact_hashes_sha256,
    )


def _report_to_dict(report: FinalAcceptanceReport) -> dict:
    return {
        "schema_version": report.schema_version,
        "schema_id": report.schema_id,
        "source_component": report.source_component,
        "reviewed_commit": report.reviewed_commit,
        "reviewed_branch": report.reviewed_branch,
        "created_at": report.created_at,
        "acceptance_mode": report.acceptance_mode,
        "bootstrap_mode_used": report.bootstrap_mode_used,
        "final_verdict": report.final_verdict,
        "implementation_rating": report.implementation_rating,
        "layer_statuses": report.layer_statuses,
        "evidence_summary": report.evidence_summary,
        "cross_layer_summary": report.cross_layer_summary,
        "validation_summary": report.validation_summary,
        "schema_validation_summary": report.schema_validation_summary,
        "safe_deferrals": report.safe_deferrals,
        "deviations": report.deviations,
        "blockers": report.blockers,
        "high_issues": report.high_issues,
        "non_blocking_followups": report.non_blocking_followups,
        "artifact_hashes": report.artifact_hashes,
        "artifact_hashes_path": report.artifact_hashes_path,
        "artifact_hashes_content_id": report.artifact_hashes_content_id,
        "artifact_hashes_sha256": report.artifact_hashes_sha256,
        "self_hash_mode": report.self_hash_mode,
        "warnings": report.warnings,
        "errors": report.errors,
    }


def write_final_acceptance_report(report: FinalAcceptanceReport, repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_report.json", _report_to_dict(report))


def _completion_record_to_dict(record: FinalAcceptanceCompletionRecord) -> dict:
    return {
        "schema_version": record.schema_version,
        "schema_id": record.schema_id,
        "source_component": record.source_component,
        "status": record.status,
        "reviewed_commit": record.reviewed_commit,
        "reviewed_branch": record.reviewed_branch,
        "created_at": record.created_at,
        "acceptance_mode": record.acceptance_mode,
        "bootstrap_mode_used": record.bootstrap_mode_used,
        "final_verdict": record.final_verdict,
        "implementation_rating": record.implementation_rating,
        "commands_run": record.commands_run,
        "artifacts_created": record.artifacts_created,
        "review_environment": record.review_environment,
        "artifact_hashes": record.artifact_hashes,
        "artifact_hashes_path": record.artifact_hashes_path,
        "artifact_hashes_content_id": record.artifact_hashes_content_id,
        "artifact_hashes_sha256": record.artifact_hashes_sha256,
        "self_hash_mode": record.self_hash_mode,
        "accepted_safe_deferrals": record.accepted_safe_deferrals,
        "unresolved_blockers": record.unresolved_blockers,
        "unresolved_high_issues": record.unresolved_high_issues,
        "warnings": record.warnings,
        "errors": record.errors,
    }
