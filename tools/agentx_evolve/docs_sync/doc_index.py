from pathlib import Path

from .doc_models import (
    DocumentRecord,
    DocumentScanReport,
    DocumentDriftRecord,
    DOC_AUTHORITY_MANUAL_GOVERNED,
    DOC_AUTHORITY_GENERATED,
    DOC_AUTHORITY_RUNTIME_EVIDENCE,
    DOC_STATUS_DRIFTED,
    DRIFT_TYPE_MISSING_INDEX_ENTRY,
    SEVERITY_MEDIUM,
    CENTRAL_STATUS_DRIFTED,
    new_id,
    utc_now_iso,
)


def build_document_index(scan_report: DocumentScanReport) -> dict:
    index: dict = {
        "generated_at": utc_now_iso(),
        "scan_id": scan_report.scan_id,
        "total_documents": len(scan_report.documents),
        "categories": {},
    }

    categories: dict[str, list[dict]] = {}
    for doc in scan_report.documents:
        doc_type = doc.document_type
        if doc_type not in categories:
            categories[doc_type] = []
        categories[doc_type].append({
            "document_id": doc.document_id,
            "path": doc.path,
            "authority": doc.authority,
            "status": doc.status,
            "protected": doc.protected,
        })

    index["categories"] = categories

    by_authority: dict[str, int] = {}
    for doc in scan_report.documents:
        auth = doc.authority
        by_authority[auth] = by_authority.get(auth, 0) + 1
    index["by_authority"] = by_authority

    return index


def validate_document_index(
    repo_root: Path,
    scan_report: DocumentScanReport,
) -> list[DocumentDriftRecord]:
    records: list[DocumentDriftRecord] = []

    for doc in scan_report.documents:
        abs_path = repo_root / doc.path
        if not abs_path.exists():
            records.append(DocumentDriftRecord(
                drift_id=new_id("drift"),
                created_at=utc_now_iso(),
                document_id=doc.document_id,
                path=doc.path,
                drift_type=DRIFT_TYPE_MISSING_INDEX_ENTRY,
                status=CENTRAL_STATUS_DRIFTED,
                expected={"exists": True},
                actual={"exists": False},
                severity=SEVERITY_MEDIUM,
                recommended_operation="REVIEW",
            ))

    return records


def render_generated_index_section(index: dict) -> str:
    lines = ["<!-- AGENTX-GENERATED-SECTION:START document_index -->"]
    lines.append("")
    lines.append(f"**Document Index** (generated at {index.get('generated_at', 'unknown')})")
    lines.append("")
    lines.append(f"Total documents: {index.get('total_documents', 0)}")
    lines.append("")

    categories = index.get("categories", {})
    for doc_type, docs in sorted(categories.items()):
        lines.append(f"### {doc_type}")
        lines.append(f"Count: {len(docs)}")
        for d in docs:
            lines.append(f"- {d.get('path', '?')} ({d.get('authority', '?')})")
        lines.append("")

    lines.append("<!-- AGENTX-GENERATED-SECTION:END document_index -->")
    return "\n".join(lines)
