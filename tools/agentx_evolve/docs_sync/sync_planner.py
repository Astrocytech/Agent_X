from pathlib import Path

from .doc_models import (
    DocumentRecord,
    DocumentScanReport,
    DocumentDriftRecord,
    DocumentSyncOperation,
    DocumentSyncPlan,
    DOC_AUTHORITY_MANUAL_GOVERNED,
    DOC_AUTHORITY_MANUAL_EDITABLE,
    DOC_AUTHORITY_GENERATED,
    DOC_AUTHORITY_RUNTIME_EVIDENCE,
    DOC_OP_UPDATE_GENERATED,
    DOC_OP_UPDATE_INDEX,
    DOC_OP_UPDATE_README_SECTION,
    DOC_OP_BLOCKED_MANUAL_DOC,
    DOC_OP_NOOP,
    DOC_STATUS_DRIFTED,
    SEVERITY_HIGH,
    SEVERITY_BLOCKER,
    new_id,
    utc_now_iso,
    to_dict,
)


def generate_documentation_sync_plan(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord],
    policy_context: dict | None = None,
) -> DocumentSyncPlan:
    operations: list[DocumentSyncOperation] = []
    blocked_operations: list[DocumentSyncOperation] = []

    for drift in drift_records:
        if drift.severity in (SEVERITY_HIGH, SEVERITY_BLOCKER):
            target_doc = _find_document(scan_report, drift.document_id)
            if target_doc and target_doc.authority == DOC_AUTHORITY_MANUAL_GOVERNED:
                blocked = block_manual_doc_operation(
                    target_doc.path,
                    f"drift requires manual update: {drift.drift_type} ({drift.recommended_operation})",
                )
                blocked_operations.append(blocked)
            elif target_doc and target_doc.authority == DOC_AUTHORITY_GENERATED:
                ops = _plan_generated_updates(target_doc, drift)
                operations.extend(ops)
            else:
                for doc in scan_report.documents:
                    if doc.authority == DOC_AUTHORITY_GENERATED and doc.contains_generated_markers:
                        ops = _plan_generated_updates(doc, drift)
                        operations.extend(ops)

    readme_ops = plan_readme_updates(scan_report, drift_records)
    for op in readme_ops:
        if op.allowed_to_apply:
            operations.append(op)
        else:
            blocked_operations.append(op)

    index_ops = plan_index_updates(scan_report, drift_records)
    for op in index_ops:
        if op.allowed_to_apply:
            operations.append(op)
        else:
            blocked_operations.append(op)

    summary = {
        "total_operations": len(operations),
        "total_blocked": len(blocked_operations),
        "total_drifts": len(drift_records),
    }

    return DocumentSyncPlan(
        plan_id=new_id("plan"),
        created_at=utc_now_iso(),
        source_scan_id=scan_report.scan_id,
        operations=operations,
        blocked_operations=blocked_operations,
        summary=summary,
    )


def plan_readme_updates(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord],
) -> list[DocumentSyncOperation]:
    operations: list[DocumentSyncOperation] = []
    for doc in scan_report.documents:
        if doc.document_type == "README" and doc.contains_generated_markers:
            op = DocumentSyncOperation(
                operation_id=new_id("op"),
                operation_type=DOC_OP_UPDATE_README_SECTION,
                target_path=doc.path,
                target_authority=doc.authority,
                allowed_to_apply=True,
                reason="README has generated markers eligible for update",
            )
            operations.append(op)
    return operations


def plan_index_updates(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord],
) -> list[DocumentSyncOperation]:
    operations: list[DocumentSyncOperation] = []
    for doc in scan_report.documents:
        if doc.document_type == "INDEX" and doc.contains_generated_markers:
            op = DocumentSyncOperation(
                operation_id=new_id("op"),
                operation_type=DOC_OP_UPDATE_INDEX,
                target_path=doc.path,
                target_authority=doc.authority,
                allowed_to_apply=True,
                reason="INDEX has generated markers eligible for update",
            )
            operations.append(op)
    return operations


def block_manual_doc_operation(
    target_path: str,
    reason: str,
) -> DocumentSyncOperation:
    return DocumentSyncOperation(
        operation_id=new_id("op"),
        operation_type=DOC_OP_BLOCKED_MANUAL_DOC,
        target_path=target_path,
        target_authority=DOC_AUTHORITY_MANUAL_GOVERNED,
        requires_policy_approval=True,
        requires_manual_review=True,
        allowed_to_apply=False,
        reason=reason,
    )


def _find_document(scan_report: DocumentScanReport, document_id: str) -> DocumentRecord | None:
    for doc in scan_report.documents:
        if doc.document_id == document_id:
            return doc
    return None


def _plan_generated_updates(
    doc: DocumentRecord, drift: DocumentDriftRecord
) -> list[DocumentSyncOperation]:
    ops: list[DocumentSyncOperation] = []
    op = DocumentSyncOperation(
        operation_id=new_id("op"),
        operation_type=DOC_OP_UPDATE_GENERATED,
        target_path=doc.path,
        target_authority=doc.authority,
        allowed_to_apply=True,
        reason=f"update generated content for drift: {drift.drift_type}",
    )
    ops.append(op)
    return ops
