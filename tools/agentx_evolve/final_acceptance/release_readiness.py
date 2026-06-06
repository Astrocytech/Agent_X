from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import (
    FinalAcceptanceEvidenceManifest, FinalAcceptanceValidationResult,
    VERDICT_NOT_ACCEPTED, VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS,
    STATUS_PASS, STATUS_FAIL,
)
from .artifact_writer import write_json_artifact, runtime_root


RELEASE_READY = "RELEASE_READY"
NOT_RELEASE_READY = "NOT_RELEASE_READY"
NOT_CLAIMED = "NOT_CLAIMED"


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def build_release_readiness_report(
    repo_root: Path,
    acceptance_mode: str,
    final_verdict: str,
    implementation_rating: float,
    layer_statuses: dict[str, str],
    validation_results: list[FinalAcceptanceValidationResult],
    schema_validation_results: list[FinalAcceptanceValidationResult],
    blockers: list[str],
    high_issues: list[str],
    evidence_manifest: FinalAcceptanceEvidenceManifest | None,
    has_completion_record: bool,
) -> dict[str, Any]:
    check_results: list[dict[str, Any]] = []
    blockers_found: list[str] = []
    all_pass = True

    def add_check(check_id: str, description: str, passed: bool, detail: str = "") -> None:
        check_results.append({
            "check_id": check_id,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
        })
        nonlocal all_pass
        if not passed:
            all_pass = False

    add_check(
        "verdict_accepted",
        "Final verdict is ACCEPTED or ACCEPTED_WITH_SAFE_DEFERRALS",
        final_verdict in (VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS),
        f"Verdict: {final_verdict}",
    )

    add_check(
        "no_blockers",
        "No unresolved blockers remain",
        len(blockers) == 0,
        f"{len(blockers)} blocker(s) found" if blockers else "No blockers",
    )
    if blockers:
        blockers_found.extend(blockers)

    add_check(
        "compileall_passed",
        "Compileall validation passes",
        any(r.status == STATUS_PASS and r.command_name == "compileall" for r in validation_results),
    )

    add_check(
        "pytest_passed",
        "Pytest validation passes",
        any(r.status == STATUS_PASS and r.command_name in ("pytest", "pytest_final_acceptance") for r in validation_results),
    )

    add_check(
        "schema_validation_passed",
        "Schema validation passes",
        any(r.status == STATUS_PASS for r in schema_validation_results) if schema_validation_results else False,
    )

    add_check(
        "evidence_manifest_exists",
        "Evidence manifest exists and hashes are present",
        evidence_manifest is not None and len(evidence_manifest.items) > 0,
    )

    add_check(
        "completion_record_exists",
        "Completion record exists",
        has_completion_record,
    )

    if evidence_manifest:
        has_hashes = any(i.sha256 is not None for i in evidence_manifest.items)
        add_check(
            "evidence_hashes_present",
            "Evidence items have SHA-256 hashes",
            has_hashes,
        )

    all_layers_valid = all(
        s in (STATUS_PASS, "DEFERRED_SAFELY", "NOT_APPLICABLE")
        for s in layer_statuses.values()
    )
    add_check(
        "layers_validated",
        "All required layers are validated",
        all_layers_valid,
        f"Layer statuses: {layer_statuses}",
    )

    if final_verdict == VERDICT_NOT_ACCEPTED:
        release_readiness = NOT_RELEASE_READY
        overall_status = "FAIL"
        blockers_found.append("Final verdict is NOT_ACCEPTED")
    elif all_pass:
        release_readiness = RELEASE_READY
        overall_status = "PASS"
    else:
        release_readiness = NOT_RELEASE_READY
        overall_status = "FAIL" if blockers_found else "PARTIAL"

    return {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_release_readiness_report.schema.json",
        "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "created_at": _make_timestamp(),
        "acceptance_mode": acceptance_mode,
        "release_readiness": release_readiness,
        "report_status": overall_status,
        "implementation_rating": implementation_rating,
        "checks": check_results,
        "blockers": blockers_found,
        "warnings": [],
        "errors": [],
    }


def write_release_readiness_report(data: dict[str, Any], repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_release_readiness_report.json", data)
