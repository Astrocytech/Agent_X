import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import (
    FinalAcceptanceLayerRegistry, FinalAcceptanceEvidenceManifest,
    CrossLayerCheck, FinalAcceptanceValidationResult, FinalAcceptanceDeviation,
    FinalAcceptanceReport, FinalAcceptanceCompletionRecord, FinalAcceptanceArtifactHash,
    VERDICT_NOT_ACCEPTED, MODE_SOURCE_ONLY_ACCEPTANCE, STATUS_PASS, STATUS_FAIL,
    STATUS_NOT_CHECKED, STATUS_NOT_RUN, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY,
    SEVERITY_BLOCKER, SEVERITY_HIGH, VALIDATED_NOT_ACCEPTED,
)
from .artifact_writer import write_json_artifact, ensure_runtime_root, runtime_root
from .layer_catalog import build_canonical_layer_catalog, validate_layer_catalog
from .layer_registry import (
    build_final_acceptance_layer_registry, write_layer_registry,
    list_required_layers, list_safely_deferred_layers,
)
from .mode_policy import (
    build_mode_policy, is_layer_required_for_mode, is_deferral_allowed_for_mode,
    validate_acceptance_mode,
)
from .evidence_collector import collect_layer_evidence, write_evidence_manifest
from .deviation_register import load_deviation_register, validate_deviation_register, write_deviation_register
from .cross_layer_checker import run_cross_layer_checks, write_cross_layer_matrix
from .validation_runner import run_validation_commands, write_validation_results
from .schema_validator import validate_final_acceptance_schemas, write_schema_validation_results
from .hash_utils import hash_artifacts, write_artifact_hashes, validate_acyclic_hash_manifest
from .final_verdict import calculate_final_verdict
from .report_generator import (
    build_final_acceptance_report, write_final_acceptance_report,
    _completion_record_to_dict,
)
from .bundle_manifest import build_final_acceptance_bundle, write_bundle_manifest
from .evidence_freshness import build_evidence_freshness_report, write_evidence_freshness_report
from .runtime_artifact_report import build_runtime_artifact_report, write_runtime_artifact_report
from .release_readiness import build_release_readiness_report, write_release_readiness_report
from .review_report import build_review_report, write_review_report
from .active_feature_inference import infer_active_features
from .safety_freeze import build_safety_freeze_report, write_safety_freeze_report
from .audit_logger import append_event, append_command_record
from .verdict_writer import build_verdict_record, write_verdict_record


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _get_git_status(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=repo_root, timeout=30,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def _write_git_status(repo_root: Path, filename: str) -> None:
    status = _get_git_status(repo_root)
    root = runtime_root(repo_root)
    (root / filename).write_text(status or "(empty - no changes or git not available)\n", encoding="utf-8")


def _build_review_environment() -> dict[str, Any]:
    env: dict[str, Any] = {
        "os": platform.system(),
        "python_version": platform.python_version(),
    }
    try:
        import pytest
        env["pytest_version"] = pytest.__version__
    except ImportError:
        env["pytest_version"] = "unknown"
    return env


def run_final_acceptance(
    repo_root: Path,
    acceptance_mode: str = MODE_SOURCE_ONLY_ACCEPTANCE,
    reviewed_commit: str | None = None,
    reviewed_branch: str | None = None,
    bootstrap_self: bool = False,
    skip_validation_commands: bool = False,
    skip_schema_validation: bool = False,
    skip_cross_layer_checks: bool = False,
    include_full_pytest: bool = True,
    avoid_recursive_final_acceptance: bool = True,
    no_safe_deferrals: bool = False,
) -> dict[str, Any]:
    ensure_runtime_root(repo_root)

    errors: list[str] = validate_acceptance_mode(acceptance_mode)
    if errors:
        return {
            "final_verdict": VERDICT_NOT_ACCEPTED,
            "implementation_rating": 0.0,
            "errors": errors,
            "blockers": errors,
            "high_issues": [],
            "non_blocking_followups": [],
            "layer_statuses": {},
        }

    # ---- Phase 1: Draft Artifacts ----

    mode_policy = build_mode_policy(acceptance_mode)
    write_json_artifact(repo_root, "final_acceptance_mode_policy.json", mode_policy)

    catalog = build_canonical_layer_catalog()
    catalog_errors = validate_layer_catalog(catalog)
    if catalog_errors:
        errors.extend(catalog_errors)

    active_features = infer_active_features(repo_root, catalog)
    for lid, active in active_features.items():
        if active:
            for layer in catalog:
                if layer.layer_id == lid and not layer.required_for_acceptance:
                    layer.required_for_acceptance = True
                    break

    append_event(repo_root, "acceptance_run_started", {
        "acceptance_mode": acceptance_mode,
        "repo_root": str(repo_root),
        "active_features_inferred": list(active_features.keys()),
    })

    registry = build_final_acceptance_layer_registry(
        repo_root=repo_root,
        reviewed_commit=reviewed_commit,
        reviewed_branch=reviewed_branch,
        acceptance_mode=acceptance_mode,
        bootstrap_self=bootstrap_self,
    )
    write_layer_registry(registry, repo_root)

    deviations = load_deviation_register(repo_root)
    deviation_errors = validate_deviation_register(deviations)
    errors.extend(deviation_errors)
    write_deviation_register(deviations, repo_root)

    evidence_manifest = collect_layer_evidence(repo_root, registry, bootstrap_self=bootstrap_self)
    write_evidence_manifest(evidence_manifest, repo_root)

    _write_git_status(repo_root, "git_status_start.txt")

    layer_statuses: dict[str, str] = {}
    for layer in registry.layers:
        lid = layer.layer_id
        required = is_layer_required_for_mode(lid, acceptance_mode)
        deferred_allowed = is_deferral_allowed_for_mode(lid, acceptance_mode)

        layer_items = [i for i in evidence_manifest.items if i.layer_id == lid]
        required_items = [i for i in layer_items if i.required]
        missing_required = [i for i in required_items if not i.exists]

        if not required:
            if deferred_allowed:
                layer_statuses[lid] = STATUS_DEFERRED_SAFELY
            else:
                layer_statuses[lid] = STATUS_NOT_APPLICABLE
        elif missing_required:
            layer_statuses[lid] = STATUS_FAIL
        else:
            all_readable = all(i.readable for i in required_items)
            if all_readable:
                layer_statuses[lid] = STATUS_PASS
            else:
                layer_statuses[lid] = STATUS_FAIL

    cross_layer_checks: list[CrossLayerCheck] = []
    if not skip_cross_layer_checks:
        cross_layer_checks = run_cross_layer_checks(
            repo_root, registry, evidence_manifest, acceptance_mode,
        )
        write_cross_layer_matrix(cross_layer_checks, repo_root)

    validation_results: list[FinalAcceptanceValidationResult] = []
    if not skip_validation_commands:
        validation_results = run_validation_commands(
            repo_root,
            include_full_pytest=include_full_pytest,
            avoid_recursive_final_acceptance=avoid_recursive_final_acceptance,
        )
        write_validation_results(validation_results, repo_root)

    schema_validation_results: list[FinalAcceptanceValidationResult] = []
    if not skip_schema_validation:
        schema_validation_results = validate_final_acceptance_schemas(repo_root)
        write_schema_validation_results(schema_validation_results, repo_root)

    # Create scope freeze artifact per DOD §36
    scope_artifact = {
        "schema_version": "1.0",
        "source_component": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "created_at": _make_timestamp(),
        "acceptance_mode": acceptance_mode,
        "reviewed_commit": reviewed_commit,
        "reviewed_branch": reviewed_branch,
        "bootstrap_mode_used": bootstrap_self,
        "layers_in_scope": [l.layer_id for l in registry.layers],
        "total_layers": len(registry.layers),
        "validation_included": not skip_validation_commands,
        "schema_validation_included": not skip_schema_validation,
        "cross_layer_checks_included": not skip_cross_layer_checks,
        "warnings": [],
        "errors": [],
    }
    write_json_artifact(repo_root, "final_acceptance_scope.json", scope_artifact)

    safety_freeze_data = build_safety_freeze_report(repo_root)
    write_safety_freeze_report(safety_freeze_data, repo_root)
    has_safety_violation = safety_freeze_data.get("safety_freeze_status") == "FAIL"
    append_event(repo_root, "safety_freeze_checked", {
        "status": safety_freeze_data.get("safety_freeze_status"),
        "checks": [c["status"] for c in safety_freeze_data.get("checks", [])],
    })

    if reviewed_commit:
        required_layer_ids = [
            l.layer_id for l in registry.layers
            if is_layer_required_for_mode(l.layer_id, acceptance_mode)
        ]
        freshness_report = build_evidence_freshness_report(
            repo_root=repo_root,
            evidence_manifest=evidence_manifest,
            reviewed_commit=reviewed_commit,
            acceptance_mode=acceptance_mode,
            required_layer_ids=required_layer_ids,
        )
        write_evidence_freshness_report(freshness_report, repo_root)

    required_layers = [
        l for l in registry.layers
        if is_layer_required_for_mode(l.layer_id, acceptance_mode)
    ]
    safely_deferred = [
        l for l in registry.layers
        if not is_layer_required_for_mode(l.layer_id, acceptance_mode)
        and is_deferral_allowed_for_mode(l.layer_id, acceptance_mode)
    ]

    safe_deferrals: list[dict[str, Any]] = []
    for layer in safely_deferred:
        safe_deferrals.append({
            "layer_id": layer.layer_id,
            "layer_name": layer.layer_name,
            "reason": f"Safely deferred in mode {acceptance_mode}",
        })

    # ---- Phase 2: Finalize with Verdict ----

    all_blockers: list[str] = []
    all_high: list[str] = []
    all_non_blocking: list[str] = []

    final_verdict, implementation_rating, blockers, high_issues, non_blocking_followups = (
        calculate_final_verdict(
            evidence_manifest=evidence_manifest,
            cross_layer_checks=cross_layer_checks,
            validation_results=validation_results,
            schema_validation_results=schema_validation_results,
            deviations=deviations,
            layer_statuses=layer_statuses,
            safe_deferrals=safe_deferrals,
            blockers=all_blockers,
            high_issues=all_high,
            non_blocking_followups=all_non_blocking,
            bootstrap_self=bootstrap_self,
            no_safe_deferrals=no_safe_deferrals,
        )
    )

    _write_git_status(repo_root, "git_status_end.txt")

    # ---- Phase 3: Hash Final Artifacts ----

    artifact_hashes: list[FinalAcceptanceArtifactHash] = []
    artifact_hashes_path = ""
    artifact_hashes_content_id = ""
    artifact_hashes_sha256: str | None = None

    runtime_root_path = ensure_runtime_root(repo_root)
    artifact_paths = list(runtime_root_path.rglob("*")) if runtime_root_path.exists() else []
    artifact_hashes = hash_artifacts(
        artifact_paths,
        exclude_self_hash_file=runtime_root_path / "final_acceptance_artifact_hashes.json",
    )
    hashes_file = write_artifact_hashes(artifact_hashes, repo_root)
    artifact_hashes_path = str(hashes_file)
    hash_errors = validate_acyclic_hash_manifest(repo_root)
    errors.extend(hash_errors)

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
    write_final_acceptance_report(report, repo_root)

    runtime_report_data = build_runtime_artifact_report(repo_root, deviations)
    write_runtime_artifact_report(runtime_report_data, repo_root)

    readiness_report = build_release_readiness_report(
        repo_root=repo_root,
        acceptance_mode=acceptance_mode,
        final_verdict=final_verdict,
        implementation_rating=implementation_rating,
        layer_statuses=layer_statuses,
        validation_results=validation_results,
        schema_validation_results=schema_validation_results,
        blockers=blockers,
        high_issues=high_issues,
        evidence_manifest=evidence_manifest,
        has_completion_record=True,
    )
    write_release_readiness_report(readiness_report, repo_root)

    schema_val_output = "\n".join(
        f"[{r.status}] {r.summary}" for r in schema_validation_results
    ) if schema_validation_results else "Schema validation was skipped"
    write_json_artifact(repo_root, "final_acceptance_command_output_schema_validation.txt",
                        {"output": schema_val_output})

    runner_summary_lines = [
        f"Verdict: {final_verdict}",
        f"Rating: {implementation_rating:.4f}",
        f"Blockers: {len(blockers)}",
        f"High Issues: {len(high_issues)}",
        f"Non-blocking: {len(non_blocking_followups)}",
    ]
    runner_output = "\n".join(runner_summary_lines)
    write_json_artifact(repo_root, "final_acceptance_command_output_runner.txt",
                        {"output": runner_output})

    for vr in validation_results:
        append_command_record(
            repo_root, vr.command_name, vr.status, vr.exit_code, vr.summary,
        )
    append_event(repo_root, "validation_commands_completed", {
        "total": len(validation_results),
        "passed": sum(1 for r in validation_results if r.status == "PASS"),
        "failed": sum(1 for r in validation_results if r.status == "FAIL"),
    })

    artifact_paths_written = [
        "final_acceptance_mode_policy.json",
        "final_acceptance_layer_registry.json",
        "final_acceptance_evidence_manifest.json",
        "final_acceptance_deviation_register.json",
        "final_acceptance_cross_layer_matrix.json",
        "final_acceptance_validation_results.json",
        "final_acceptance_schema_validation_results.json",
        "final_acceptance_scope.json",
        "final_acceptance_evidence_freshness_report.json",
        "final_acceptance_safety_freeze.json",
        "git_status_start.txt",
        "git_status_end.txt",
        "final_acceptance_report.json",
        "final_acceptance_runtime_artifact_report.json",
        "final_acceptance_release_readiness_report.json",
        "final_acceptance_command_output_schema_validation.txt",
        "final_acceptance_command_output_runner.txt",
        "final_acceptance_completion_record.json",
        "latest_final_acceptance_result.json",
        "final_acceptance_verdict.json",
        "final_acceptance_review_report.json",
        "final_acceptance_event_history.jsonl",
        "final_acceptance_command_history.jsonl",
        "final_acceptance_artifact_hashes.json",
        "final_acceptance_bundle.json",
    ]

    completion_record_status = "VALIDATED"
    if final_verdict == VERDICT_NOT_ACCEPTED:
        completion_record_status = VALIDATED_NOT_ACCEPTED

    completion_record = FinalAcceptanceCompletionRecord(
        status=completion_record_status,
        reviewed_commit=registry.reviewed_commit,
        reviewed_branch=registry.reviewed_branch,
        created_at=_make_timestamp(),
        acceptance_mode=acceptance_mode,
        bootstrap_mode_used=bootstrap_self,
        final_verdict=final_verdict,
        implementation_rating=implementation_rating,
        commands_run=[
            {"command_name": r.command_name, "status": r.status}
            for r in validation_results
        ],
        artifacts_created=artifact_paths_written,
        review_environment=_build_review_environment(),
        artifact_hashes=[h.__dict__ for h in artifact_hashes],
        artifact_hashes_path=artifact_hashes_path,
        artifact_hashes_content_id=artifact_hashes_content_id,
        artifact_hashes_sha256=artifact_hashes_sha256,
        accepted_safe_deferrals=safe_deferrals,
        unresolved_blockers=blockers,
        unresolved_high_issues=high_issues,
        warnings=[],
        errors=errors,
    )
    write_completion_record(completion_record, repo_root)
    write_latest_result(completion_record, repo_root)

    accepted_deviations_list: list[dict[str, Any]] = [
        {"deviation_id": d.deviation_id, "area": d.area, "description": d.description}
        for d in deviations
    ]
    verdict_record = build_verdict_record(
        repo_root=repo_root,
        reviewed_commit=reviewed_commit,
        reviewed_branch=reviewed_branch,
        acceptance_mode=acceptance_mode,
        final_verdict=final_verdict,
        implementation_rating=implementation_rating,
        blockers=blockers,
        accepted_deviations=accepted_deviations_list,
        non_blocking_followups=non_blocking_followups,
        evidence_manifest=evidence_manifest,
        artifact_hashes=artifact_hashes,
        layer_statuses=layer_statuses,
        validation_status="PASS" if all(r.status == "PASS" for r in validation_results) else "FAIL",
        schema_validation_status="PASS" if all(r.status == "PASS" for r in schema_validation_results) else "FAIL",
        release_readiness_status=readiness_report.get("report_status", "NOT_CHECKED"),
    )
    write_verdict_record(verdict_record, repo_root)
    append_event(repo_root, "verdict_written", {
        "final_verdict": final_verdict,
        "implementation_rating": implementation_rating,
    })

    git_start_str = _get_git_status(repo_root)
    git_end_str = _get_git_status(repo_root)
    commands_run_list = [
        {"command_name": r.command_name, "status": r.status}
        for r in validation_results
    ]
    review_report_data = build_review_report(
        repo_root=repo_root,
        reviewed_commit=reviewed_commit,
        reviewed_branch=reviewed_branch,
        acceptance_mode=acceptance_mode,
        bootstrap_self=bootstrap_self,
        final_verdict=final_verdict,
        implementation_rating=implementation_rating,
        blockers=blockers,
        high_issues=high_issues,
        non_blocking_followups=non_blocking_followups,
        deviations=deviations,
        commands_run=commands_run_list,
        layer_statuses=layer_statuses,
        git_status_start=git_start_str,
        git_status_end=git_end_str,
        release_ready_status=readiness_report.get("release_readiness", "NOT_CLAIMED"),
    )
    write_review_report(review_report_data, repo_root)

    runtime_root_path = ensure_runtime_root(repo_root)
    all_final_paths = list(runtime_root_path.rglob("*")) if runtime_root_path.exists() else []
    final_artifact_hashes = hash_artifacts(
        all_final_paths,
        exclude_self_hash_file=runtime_root_path / "final_acceptance_artifact_hashes.json",
    )
    write_artifact_hashes(final_artifact_hashes, repo_root)

    layer_evidence_hashes: dict[str, str] = {}
    for item in evidence_manifest.items:
        if item.sha256:
            layer_evidence_hashes[item.layer_id] = item.sha256

    command_output_hashes: dict[str, str] = {}
    for vr in validation_results:
        if vr.output_sha256:
            command_output_hashes[vr.command_name] = vr.output_sha256

    bundle_data = build_final_acceptance_bundle(
        repo_root=repo_root,
        reviewed_commit=reviewed_commit,
        artifact_hashes=final_artifact_hashes,
        layer_evidence_hashes=layer_evidence_hashes,
        command_output_hashes=command_output_hashes,
    )
    write_bundle_manifest(bundle_data, repo_root)

    append_event(repo_root, "acceptance_run_completed", {
        "final_verdict": final_verdict,
        "artifacts_written": len(artifact_paths_written),
    })

    return {
        "final_verdict": final_verdict,
        "implementation_rating": implementation_rating,
        "blockers": blockers,
        "high_issues": high_issues,
        "non_blocking_followups": non_blocking_followups,
        "layer_statuses": layer_statuses,
        "errors": errors,
        "completion_record": completion_record,
    }


def write_completion_record(record: FinalAcceptanceCompletionRecord, repo_root: Path) -> Path:
    return write_json_artifact(
        repo_root,
        "final_acceptance_completion_record.json",
        _completion_record_to_dict(record),
    )


def write_latest_result(record: FinalAcceptanceCompletionRecord, repo_root: Path) -> Path:
    return write_json_artifact(
        repo_root,
        "latest_final_acceptance_result.json",
        _completion_record_to_dict(record),
    )
