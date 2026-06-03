import os
from pathlib import Path

from .doc_models import (
    DocumentScanReport,
    DocumentSyncPlan,
    DocumentSyncResult,
    DocumentationSyncControllerResult,
    DocumentationSyncEvidenceManifest,
    DocumentationSyncReviewReport,
    DocumentationSyncCompletionRecord,
    DocumentationSyncCommandResult,
    DOC_SYNC_MODE_SCAN_ONLY,
    DOC_SYNC_MODE_VALIDATE_ONLY,
    DOC_SYNC_MODE_SCAN_PLAN,
    DOC_SYNC_MODE_DRY_RUN_APPLY,
    DOC_SYNC_MODE_APPLY_GENERATED,
    DOC_SYNC_MODE_REVIEW_REPORT,
    DOC_SYNC_MODE_COMPLETION_RECORD,
    APPLY_MODE_DRY_RUN,
    APPLY_MODE_APPLY,
    CENTRAL_STATUS_PASS,
    CENTRAL_STATUS_NOT_RUN,
    CENTRAL_STATUS_SCANNED,
    CENTRAL_STATUS_PLAN_CREATED,
    CENTRAL_STATUS_DRY_RUN_COMPLETE,
    CENTRAL_STATUS_APPLIED,
    LOCK_MODE_READ,
    LOCK_MODE_WRITE,
    new_id,
    utc_now_iso,
    sha256_file,
    to_dict,
)
from .doc_scanner import scan_documentation
from .drift_detector import detect_documentation_drift
from .link_validator import validate_document_links
from .doc_staleness import detect_stale_documents
from .sync_planner import generate_documentation_sync_plan
from .doc_sync_apply import apply_documentation_sync_plan
from .manual_doc_protector import check_documentation_sync_permission
from .evidence_writer import (
    write_scan_report,
    write_drift_report,
    write_link_report,
    write_staleness_report,
    write_sync_plan,
    write_sync_result,
    write_evidence_manifest,
    write_registry_report,
    write_manual_protection_report,
    write_generated_sync_report,
    append_change_history_line,
    sha256_evidence_file,
)
from .sync_reporter import build_documentation_sync_review_report
from .doc_lock import (
    acquire_docs_sync_lock,
    release_docs_sync_lock,
    read_docs_sync_lock,
)
from .generated_doc_sync import build_generated_section_registry
from .doc_traceability import (
    build_docs_sync_traceability_matrix,
    write_docs_sync_traceability_matrix,
)
from .doc_deviations import write_docs_sync_deviation_register

RUNTIME_ROOT = Path(".agentx-init/docs_sync")


def run_documentation_sync(
    repo_root: Path,
    mode: str = DOC_SYNC_MODE_SCAN_PLAN,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    policy_context: dict | None = None,
    reviewed_commit: str | None = None,
) -> dict:
    repo_root = repo_root.resolve()
    now = utc_now_iso()
    result_id = new_id("ctrl")

    if policy_context is None:
        policy_context = {}

    (repo_root / RUNTIME_ROOT).mkdir(parents=True, exist_ok=True)

    lock_result = acquire_docs_sync_lock(repo_root, LOCK_MODE_READ)
    if lock_result.get("status") == "BLOCKED" and mode == DOC_SYNC_MODE_APPLY_GENERATED:
        return {
            "status": "BLOCKED",
            "reason": "could not acquire lock for apply mode",
            "result_id": result_id,
        }

    scan_report = scan_documentation(repo_root, include_paths, exclude_paths)

    write_scan_report(repo_root, scan_report)

    drift_records = detect_documentation_drift(repo_root, scan_report)
    write_drift_report(repo_root, drift_records)

    link_records = validate_document_links(repo_root, scan_report)
    write_link_report(repo_root, link_records)

    staleness_records = detect_stale_documents(repo_root, scan_report)
    write_staleness_report(repo_root, staleness_records)

    if mode in (DOC_SYNC_MODE_SCAN_ONLY, DOC_SYNC_MODE_VALIDATE_ONLY):
        release_docs_sync_lock(repo_root, lock_result.get("lock", {}).get("lock_id", ""))
        return _build_controller_result(
            result_id, now, mode, CENTRAL_STATUS_SCANNED,
            scan_report_path=_rel(RUNTIME_ROOT / "documentation_scan_result.json"),
            drift_report_path=_rel(RUNTIME_ROOT / "documentation_drift_report.json"),
            link_report_path=_rel(RUNTIME_ROOT / "broken_link_report.json"),
            staleness_report_path=_rel(RUNTIME_ROOT / "document_staleness_report.json"),
        )

    sync_plan = generate_documentation_sync_plan(scan_report, drift_records, policy_context)
    write_sync_plan(repo_root, sync_plan)

    if mode == DOC_SYNC_MODE_SCAN_PLAN:
        release_docs_sync_lock(repo_root, lock_result.get("lock", {}).get("lock_id", ""))
        return _build_controller_result(
            result_id, now, mode, CENTRAL_STATUS_PLAN_CREATED,
            scan_report_path=_rel(RUNTIME_ROOT / "documentation_scan_result.json"),
            drift_report_path=_rel(RUNTIME_ROOT / "documentation_drift_report.json"),
            link_report_path=_rel(RUNTIME_ROOT / "broken_link_report.json"),
            staleness_report_path=_rel(RUNTIME_ROOT / "document_staleness_report.json"),
            sync_plan_path=_rel(RUNTIME_ROOT / "documentation_sync_plan.json"),
        )

    apply_mode = APPLY_MODE_APPLY if mode == DOC_SYNC_MODE_APPLY_GENERATED else APPLY_MODE_DRY_RUN

    write_lock = acquire_docs_sync_lock(repo_root, LOCK_MODE_WRITE)
    if write_lock.get("status") in ("BLOCKED", "STALE") and mode == DOC_SYNC_MODE_APPLY_GENERATED:
        release_docs_sync_lock(repo_root, lock_result.get("lock", {}).get("lock_id", ""))
        return {
            "status": "BLOCKED",
            "reason": "write lock unavailable for apply",
            "result_id": result_id,
        }

    sync_result = apply_documentation_sync_plan(repo_root, sync_plan, apply_mode)
    write_sync_result(repo_root, sync_result)

    release_docs_sync_lock(repo_root, write_lock.get("lock", {}).get("lock_id", ""))
    release_docs_sync_lock(repo_root, lock_result.get("lock", {}).get("lock_id", ""))

    review_report = build_documentation_sync_review_report(
        scan_report, drift_records, link_records, staleness_records, sync_plan, sync_result,
    )
    _write_review_report(repo_root, review_report)

    evidence_manifest = DocumentationSyncEvidenceManifest(
        created_at=now,
        scan_report_path=_rel(RUNTIME_ROOT / "documentation_scan_result.json"),
        drift_report_path=_rel(RUNTIME_ROOT / "documentation_drift_report.json"),
        sync_plan_path=_rel(RUNTIME_ROOT / "documentation_sync_plan.json") if sync_plan else None,
        sync_result_path=_rel(RUNTIME_ROOT / "documentation_sync_result.json"),
        review_report_path=_rel(RUNTIME_ROOT / "documentation_review_report.json"),
        validated_commit=reviewed_commit,
    )
    write_evidence_manifest(repo_root, evidence_manifest)

    write_registry_report(repo_root, {"registry_id": new_id("reg"), "entries": []})
    write_manual_protection_report(repo_root, {"status": "PROTECTED", "blocked_operations": [to_dict(o) for o in sync_plan.blocked_operations] if sync_plan else []})
    write_generated_sync_report(repo_root, {"status": "COMPLETE" if mode == DOC_SYNC_MODE_APPLY_GENERATED else "DRY_RUN", "result": to_dict(sync_result) if sync_result else {}})
    append_change_history_line(repo_root, {"event": "sync_completed", "mode": mode, "result_id": result_id, "created_at": now})

    return _build_controller_result(
        result_id, now, mode, CENTRAL_STATUS_APPLIED if mode == DOC_SYNC_MODE_APPLY_GENERATED else CENTRAL_STATUS_DRY_RUN_COMPLETE,
        scan_report_path=_rel(RUNTIME_ROOT / "documentation_scan_result.json"),
        drift_report_path=_rel(RUNTIME_ROOT / "documentation_drift_report.json"),
        link_report_path=_rel(RUNTIME_ROOT / "broken_link_report.json"),
        staleness_report_path=_rel(RUNTIME_ROOT / "document_staleness_report.json"),
        sync_plan_path=_rel(RUNTIME_ROOT / "documentation_sync_plan.json"),
        sync_result_path=_rel(RUNTIME_ROOT / "documentation_sync_result.json"),
        evidence_manifest_path=_rel(RUNTIME_ROOT / "documentation_evidence_manifest.json"),
        review_report_path=_rel(RUNTIME_ROOT / "documentation_review_report.json"),
        changed_files=sync_result.changed_files if sync_result else [],
        blocked_operations=[o for o in (sync_plan.blocked_operations if sync_plan else [])],
    )


def run_scan_only(
    repo_root: Path,
    policy_context: dict | None = None,
) -> dict:
    return run_documentation_sync(repo_root, DOC_SYNC_MODE_SCAN_ONLY, policy_context=policy_context)


def run_validate_only(
    repo_root: Path,
    policy_context: dict | None = None,
) -> dict:
    return run_documentation_sync(repo_root, DOC_SYNC_MODE_VALIDATE_ONLY, policy_context=policy_context)


def run_plan_only(
    repo_root: Path,
    policy_context: dict | None = None,
) -> dict:
    return run_documentation_sync(repo_root, DOC_SYNC_MODE_SCAN_PLAN, policy_context=policy_context)


def run_apply_generated(
    repo_root: Path,
    policy_context: dict,
) -> dict:
    return run_documentation_sync(repo_root, DOC_SYNC_MODE_APPLY_GENERATED, policy_context=policy_context)


def _build_controller_result(
    result_id: str,
    created_at: str,
    mode: str,
    status: str,
    scan_report_path: str | None = None,
    drift_report_path: str | None = None,
    link_report_path: str | None = None,
    staleness_report_path: str | None = None,
    sync_plan_path: str | None = None,
    sync_result_path: str | None = None,
    evidence_manifest_path: str | None = None,
    review_report_path: str | None = None,
    changed_files: list[str] | None = None,
    blocked_operations: list | None = None,
) -> dict:
    result = {
        "result_id": result_id,
        "created_at": created_at,
        "mode": mode,
        "status": status,
        "scan_report_path": scan_report_path,
        "drift_report_path": drift_report_path,
        "link_report_path": link_report_path,
        "staleness_report_path": staleness_report_path,
        "sync_plan_path": sync_plan_path,
        "sync_result_path": sync_result_path,
        "evidence_manifest_path": evidence_manifest_path,
        "review_report_path": review_report_path,
        "changed_files": changed_files or [],
        "blocked_operations": [to_dict(o) if hasattr(o, "__slots__") else o for o in (blocked_operations or [])],
        "warnings": [],
        "errors": [],
    }
    return result


def _rel(path: Path) -> str:
    return str(path.as_posix())


def _write_review_report(repo_root: Path, report: DocumentationSyncReviewReport) -> None:
    import json
    path = repo_root / RUNTIME_ROOT / "documentation_review_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = to_dict(report)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.replace(path)
