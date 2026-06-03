from .doc_models import (
    DocumentScanReport,
    DocumentDriftRecord,
    DocumentLinkRecord,
    DocumentStalenessRecord,
    DocumentSyncPlan,
    DocumentSyncResult,
    DocumentationSyncReviewReport,
    CENTRAL_STATUS_PASS,
    CENTRAL_STATUS_PARTIAL,
    CENTRAL_STATUS_FAIL,
    CENTRAL_STATUS_NOT_RUN,
    CENTRAL_STATUS_CURRENT,
    CENTRAL_STATUS_DRIFTED,
    CENTRAL_STATUS_MISSING,
    SEVERITY_HIGH,
    SEVERITY_BLOCKER,
    new_id,
    utc_now_iso,
)


def build_documentation_sync_review_report(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord],
    link_records: list[DocumentLinkRecord],
    staleness_records: list[DocumentStalenessRecord],
    sync_plan: DocumentSyncPlan | None = None,
    sync_result: DocumentSyncResult | None = None,
) -> DocumentationSyncReviewReport:
    now = utc_now_iso()
    blockers: list[str] = []
    high_issues: list[str] = []
    followups: list[str] = []

    scan_status = CENTRAL_STATUS_PASS if scan_report.documents else CENTRAL_STATUS_FAIL

    if not drift_records:
        drift_status = CENTRAL_STATUS_PASS
    else:
        blocker_drifts = [d for d in drift_records if d.severity == SEVERITY_BLOCKER]
        high_drifts = [d for d in drift_records if d.severity == SEVERITY_HIGH]
        if blocker_drifts:
            drift_status = CENTRAL_STATUS_FAIL
            for d in blocker_drifts:
                blockers.append(f"blocker drift: {d.drift_type} for {d.document_id}")
        elif high_drifts:
            drift_status = CENTRAL_STATUS_PARTIAL
            for d in high_drifts:
                high_issues.append(f"high drift: {d.drift_type} for {d.document_id}")
        else:
            drift_status = CENTRAL_STATUS_PARTIAL

    broken_links = [l for l in link_records if l.status == CENTRAL_STATUS_FAIL]
    if not broken_links:
        link_status = CENTRAL_STATUS_PASS
    else:
        link_status = CENTRAL_STATUS_FAIL
        for l in broken_links[:10]:
            blockers.append(f"broken link: {l.target} in {l.source_path}")

    if not staleness_records:
        staleness_status = CENTRAL_STATUS_PASS
    else:
        missing = [s for s in staleness_records if s.status == CENTRAL_STATUS_MISSING]
        if missing:
            staleness_status = CENTRAL_STATUS_FAIL
            for s in missing:
                blockers.append(f"missing document: {s.document_id}")
        else:
            staleness_status = CENTRAL_STATUS_PARTIAL
            for s in staleness_records:
                followups.append(f"stale document: {s.document_id} - {s.staleness_reason}")

    manual_doc_status = CENTRAL_STATUS_PASS
    generated_doc_status = CENTRAL_STATUS_PASS
    evidence_status = CENTRAL_STATUS_PASS

    if sync_plan:
        if sync_plan.blocked_operations:
            manual_doc_status = CENTRAL_STATUS_PASS
            for op in sync_plan.blocked_operations:
                high_issues.append(f"blocked operation: {op.operation_type} on {op.target_path}")

    final_verdict = CENTRAL_STATUS_FAIL if blockers else CENTRAL_STATUS_PASS

    return DocumentationSyncReviewReport(
        created_at=now,
        scan_status=scan_status,
        drift_status=drift_status,
        link_status=link_status,
        staleness_status=staleness_status,
        manual_doc_protection_status=manual_doc_status,
        generated_doc_update_status=generated_doc_status,
        evidence_status=evidence_status,
        blockers=blockers,
        high_issues=high_issues,
        non_blocking_followups=followups,
        final_verdict=final_verdict,
    )
