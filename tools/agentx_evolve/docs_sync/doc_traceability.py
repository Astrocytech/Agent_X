from pathlib import Path

from .doc_models import (
    DocumentScanReport,
    DocumentationSyncTraceabilityMatrix,
    TRACEABILITY_STATUS_PASS,
    TRACEABILITY_STATUS_NOT_CHECKED,
    new_id,
    utc_now_iso,
    to_dict,
)

TRACEABILITY_REQUIREMENTS = [
    {
        "requirement_id": "REQ-DS-SCAN-001",
        "requirement_text": "scan documents",
        "implementation_file": "docs_sync/doc_scanner.py",
        "test_file": "test_docs_sync_scanner.py",
        "evidence_artifact": "documentation_scan_result.json",
    },
    {
        "requirement_id": "REQ-DS-CLASSIFY-001",
        "requirement_text": "classify authority",
        "implementation_file": "docs_sync/doc_registry.py",
        "test_file": "test_docs_sync_registry.py",
        "evidence_artifact": "documentation_registry.json",
    },
    {
        "requirement_id": "REQ-DS-DRIFT-001",
        "requirement_text": "detect drift",
        "implementation_file": "docs_sync/drift_detector.py",
        "test_file": "test_docs_sync_drift_detector.py",
        "evidence_artifact": "documentation_drift_report.json",
    },
    {
        "requirement_id": "REQ-DS-PROTECT-001",
        "requirement_text": "protect manual docs",
        "implementation_file": "docs_sync/manual_doc_protector.py",
        "test_file": "test_docs_sync_negative_cases.py",
        "evidence_artifact": "manual_doc_protection_report.json",
    },
    {
        "requirement_id": "REQ-DS-GENUPDATE-001",
        "requirement_text": "update generated section only",
        "implementation_file": "docs_sync/generated_doc_sync.py",
        "test_file": "test_docs_sync_generated_doc_sync.py",
        "evidence_artifact": "documentation_sync_result.json",
    },
    {
        "requirement_id": "REQ-DS-LINKS-001",
        "requirement_text": "validate links",
        "implementation_file": "docs_sync/link_validator.py",
        "test_file": "test_docs_sync_link_validator.py",
        "evidence_artifact": "broken_link_report.json",
    },
    {
        "requirement_id": "REQ-DS-STALE-001",
        "requirement_text": "detect stale docs",
        "implementation_file": "docs_sync/doc_staleness.py",
        "test_file": "test_docs_sync_staleness.py",
        "evidence_artifact": "document_staleness_report.json",
    },
    {
        "requirement_id": "REQ-DS-EVIDENCE-001",
        "requirement_text": "write evidence",
        "implementation_file": "docs_sync/evidence_writer.py",
        "test_file": "test_docs_sync_evidence_writer.py",
        "evidence_artifact": "documentation_evidence_manifest.json",
    },
    {
        "requirement_id": "REQ-DS-CONTROLLER-001",
        "requirement_text": "controller flow",
        "implementation_file": "docs_sync/doc_controller.py",
        "test_file": "test_docs_sync_controller.py",
        "evidence_artifact": "documentation_review_report.json",
    },
]


def build_docs_sync_traceability_matrix(
    repo_root: Path,
    scan_report: DocumentScanReport,
) -> dict:
    entries: list[dict] = []
    summary_counts = {"PASS": 0, "NOT_CHECKED": 0, "total": len(TRACEABILITY_REQUIREMENTS)}

    for req in TRACEABILITY_REQUIREMENTS:
        impl_found = any(req["implementation_file"] in d.path for d in scan_report.documents)
        test_found = any(req["test_file"] in d.path for d in scan_report.documents)

        status = TRACEABILITY_STATUS_PASS if impl_found else TRACEABILITY_STATUS_NOT_CHECKED

        entries.append({
            "requirement_id": req["requirement_id"],
            "requirement_text": req["requirement_text"],
            "implementation_file": req["implementation_file"],
            "test_file": req["test_file"],
            "evidence_artifact": req["evidence_artifact"],
            "status": status,
        })

        if status == TRACEABILITY_STATUS_PASS:
            summary_counts["PASS"] += 1
        else:
            summary_counts["NOT_CHECKED"] += 1

    return {
        "schema_version": "1.0",
        "schema_id": "documentation_sync_traceability_matrix.schema.json",
        "matrix_id": new_id("tm"),
        "created_at": utc_now_iso(),
        "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        "entries": entries,
        "summary": summary_counts,
        "warnings": [],
        "errors": [],
    }


def validate_docs_sync_traceability_matrix(matrix: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    entries = matrix.get("entries", [])
    if not entries:
        errors.append("traceability matrix has no entries")
    for entry in entries:
        if entry.get("status") == TRACEABILITY_STATUS_NOT_CHECKED:
            errors.append(
                f"requirement {entry.get('requirement_id')} not satisfied: "
                f"{entry.get('requirement_text')}"
            )
    return len(errors) == 0, errors


def write_docs_sync_traceability_matrix(repo_root: Path, matrix: dict) -> dict:
    import json
    out_dir = repo_root / ".agentx-init" / "docs_sync"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "documentation_sync_traceability_matrix.json"
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2, default=str)
    tmp.replace(path)
    return {"path": str(path), "status": "written"}
