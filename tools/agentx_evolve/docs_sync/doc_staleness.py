import re
from pathlib import Path

from .doc_models import (
    DocumentRecord,
    DocumentScanReport,
    DocumentStalenessRecord,
    DOC_STATUS_CURRENT,
    DOC_STATUS_STALE,
    DOC_STATUS_MISSING,
    CENTRAL_STATUS_CURRENT,
    CENTRAL_STATUS_MISSING,
    new_id,
    utc_now_iso,
    to_dict,
)

DONE_RE = re.compile(r"\bDONE\b", re.IGNORECASE)


def detect_stale_documents(
    repo_root: Path, scan_report: DocumentScanReport
) -> list[DocumentStalenessRecord]:
    repo_root = repo_root.resolve()
    records: list[DocumentStalenessRecord] = []

    for doc in scan_report.documents:
        abs_path = repo_root / doc.path
        related_code: list[str] = []
        related_schemas: list[str] = []
        related_tests: list[str] = []
        related_evidence: list[str] = []

        if not abs_path.exists():
            rec = DocumentStalenessRecord(
                staleness_id=new_id("stale"),
                document_id=doc.document_id,
                path=doc.path,
                status=DOC_STATUS_MISSING,
                staleness_reason="file does not exist on disk",
            )
            records.append(rec)
            continue

        text = abs_path.read_text(encoding="utf-8", errors="replace") if abs_path.exists() else ""

        staleness_reasons: list[str] = []

        if DONE_RE.search(text):
            evidence_found = False
            for other in scan_report.documents:
                if other.document_id != doc.document_id and other.authority == "RUNTIME_EVIDENCE":
                    evidence_found = True
                    related_evidence.append(other.path)
                    break
            if not evidence_found:
                staleness_reasons.append(
                    "document claims DONE but no runtime evidence found in scan"
                )

        for other in scan_report.documents:
            if other.document_type == "SCHEMA":
                related_schemas.append(other.path)
            elif other.document_type == "TEST":
                related_tests.append(other.path)

        if staleness_reasons:
            rec = DocumentStalenessRecord(
                staleness_id=new_id("stale"),
                document_id=doc.document_id,
                path=doc.path,
                status=DOC_STATUS_STALE,
                staleness_reason="; ".join(staleness_reasons),
                related_code_paths=related_code,
                related_schema_paths=related_schemas,
                related_test_paths=related_tests,
                related_evidence_paths=related_evidence,
            )
            records.append(rec)

    return records


def is_document_stale_against_related_files(
    document: DocumentRecord,
    related_paths: list[Path],
) -> DocumentStalenessRecord | None:
    if not related_paths:
        return None

    reasons: list[str] = []
    for rp in related_paths:
        if not rp.exists():
            reasons.append(f"referenced file missing: {rp}")

    if not reasons:
        return None

    return DocumentStalenessRecord(
        staleness_id=new_id("stale"),
        document_id=document.document_id,
        path=document.path,
        status=DOC_STATUS_STALE,
        staleness_reason="; ".join(reasons),
        related_code_paths=[str(p) for p in related_paths],
    )
