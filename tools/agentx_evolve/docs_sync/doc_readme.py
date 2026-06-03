from pathlib import Path

from .doc_models import (
    DocumentRecord,
    DocumentScanReport,
    DocumentDriftRecord,
    DOC_AUTHORITY_GENERATED,
    DOC_STATUS_DRIFTED,
    DRIFT_TYPE_STALE_README_STATUS,
    SEVERITY_MEDIUM,
    CENTRAL_STATUS_DRIFTED,
    new_id,
    utc_now_iso,
)
from .doc_registry import has_generated_markers


def validate_readme_status(
    repo_root: Path,
    scan_report: DocumentScanReport,
) -> list[DocumentDriftRecord]:
    records: list[DocumentDriftRecord] = []
    now = utc_now_iso()

    for doc in scan_report.documents:
        if doc.document_type != "README":
            continue

        abs_path = repo_root / doc.path
        if not abs_path.exists():
            continue

        text = abs_path.read_text(encoding="utf-8", errors="replace")

        if not has_generated_markers(text):
            continue

        for line in text.split("\n"):
            ls = line.strip().lower()
            if "status:" in ls and "done" in ls:
                broken_links_found = any(
                    d.authority == DOC_AUTHORITY_GENERATED
                    and d.status == "FAIL"
                    for d in scan_report.documents
                )
                if broken_links_found:
                    records.append(DocumentDriftRecord(
                        drift_id=new_id("drift"),
                        created_at=now,
                        document_id=doc.document_id,
                        path=doc.path,
                        drift_type=DRIFT_TYPE_STALE_README_STATUS,
                        status=CENTRAL_STATUS_DRIFTED,
                        expected={"validated": True},
                        actual={"validated": False},
                        severity=SEVERITY_MEDIUM,
                        recommended_operation="UPDATE_README",
                    ))

    return records


def render_generated_readme_section(scan_report: DocumentScanReport) -> str:
    lines = ["<!-- AGENTX-GENERATED-SECTION:START docs_sync_status -->"]
    lines.append("")
    lines.append("## Documentation Sync Status")
    lines.append("")
    lines.append(f"Scan ID: {scan_report.scan_id}")
    lines.append(f"Scanned: {scan_report.summary.get('total_scanned', 0)} files")
    lines.append(f"Documents: {scan_report.summary.get('total_documents', 0)}")
    lines.append(f"Skipped: {scan_report.summary.get('total_skipped', 0)}")
    lines.append("")
    lines.append("<!-- AGENTX-GENERATED-SECTION:END docs_sync_status -->")
    return "\n".join(lines)
