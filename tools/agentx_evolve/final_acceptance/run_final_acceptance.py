from pathlib import Path
from typing import Any

from agentx_evolve.final_acceptance.report_generator import (
    build_final_acceptance_report,
    write_final_acceptance_report,
)


def run_final_acceptance(
    repo_root: Path,
    registry: Any,
    evidence_manifest: Any = None,
    cross_layer_checks: list[Any] | None = None,
    validation_results: list[Any] | None = None,
    schema_validation_results: list[Any] | None = None,
    deviations: list[Any] | None = None,
    layer_statuses: dict[str, str] | None = None,
    final_verdict: str = "NOT_ACCEPTED",
    implementation_rating: float = 0.0,
    safe_deferrals: list[dict[str, Any]] | None = None,
    blockers: list[str] | None = None,
    high_issues: list[str] | None = None,
    non_blocking_followups: list[str] | None = None,
    artifact_hashes: list[Any] | None = None,
    artifact_hashes_path: str = "",
    artifact_hashes_content_id: str = "",
    artifact_hashes_sha256: str | None = None,
) -> dict[str, Any]:
    report = build_final_acceptance_report(
        repo_root=repo_root,
        registry=registry,
        evidence_manifest=evidence_manifest,
        cross_layer_checks=cross_layer_checks,
        validation_results=validation_results,
        schema_validation_results=schema_validation_results,
        deviations=deviations,
        layer_statuses=layer_statuses,
        final_verdict=final_verdict,
        implementation_rating=implementation_rating,
        safe_deferrals=safe_deferrals,
        blockers=blockers,
        high_issues=high_issues,
        non_blocking_followups=non_blocking_followups,
        artifact_hashes=artifact_hashes,
        artifact_hashes_path=artifact_hashes_path,
        artifact_hashes_content_id=artifact_hashes_content_id,
        artifact_hashes_sha256=artifact_hashes_sha256,
    )
    output_path = write_final_acceptance_report(report, repo_root)
    return {
        "report": report,
        "output_path": str(output_path),
        "final_verdict": report.final_verdict,
    }


__all__ = [
    "build_final_acceptance_report",
    "write_final_acceptance_report",
    "run_final_acceptance",
]
