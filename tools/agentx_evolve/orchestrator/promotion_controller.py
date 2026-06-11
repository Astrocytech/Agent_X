from __future__ import annotations

from typing import Any, Callable

from agentx_evolve.orchestrator.orchestrator_models import (
    PromotionGateRecord,
    OrchestratorEvidenceManifest,
    OrchestratorReviewReport,
    utc_now_iso,
    new_id,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    GATE_STATUS_PENDING,
    GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED,
)


def check_promotion_ready(
    manifest: OrchestratorEvidenceManifest | None,
    review_report: OrchestratorReviewReport | None,
) -> tuple[bool, list[str]]:
    blockers: list[str] = []

    if manifest is None:
        blockers.append("Evidence manifest is missing")
    else:
        if not manifest.evidence_manifest_sha256:
            blockers.append("Evidence manifest hash is missing")
        if not manifest.evidence_files:
            blockers.append("Evidence manifest has no evidence files")

    if review_report is None:
        blockers.append("Review report is missing")
    else:
        if not review_report.review_report_sha256:
            blockers.append("Review report hash is missing")
        if review_report.blockers:
            blockers.extend(review_report.blockers)

    return len(blockers) == 0, blockers


def create_promotion_gate_record(
    run_id: str,
    promotion_target: str = "next_layer",
    proposal_id: str = "",
    policy_decision_id: str = "",
    candidate_id: str = "",
    rollback_ref: str = "",
) -> PromotionGateRecord:
    return PromotionGateRecord(
        promotion_record_id=new_id("pg"),
        run_id=run_id,
        created_at=utc_now_iso(),
        promotion_target=promotion_target,
        promotion_status=GATE_STATUS_PENDING,
        promotion_decision="",
        proposal_id=proposal_id,
        policy_decision_id=policy_decision_id,
        candidate_id=candidate_id,
        rollback_ref=rollback_ref,
    )


def request_promotion_decision(
    record: PromotionGateRecord,
    promotion_gate_fn: Callable | None = None,
) -> PromotionGateRecord:
    if promotion_gate_fn is not None:
        try:
            result = promotion_gate_fn(
                promotion_record_id=record.promotion_record_id,
                run_id=record.run_id,
                target=record.promotion_target,
            )
            decision = result.get("decision", GATE_STATUS_DENIED)
            record.promotion_status = decision
            record.promotion_decision = decision
            if decision == GATE_STATUS_DENIED:
                record.errors.append(result.get("reason", "Promotion denied"))
        except Exception as e:
            record.promotion_status = GATE_STATUS_DENIED
            record.promotion_decision = GATE_STATUS_DENIED
            record.errors.append(f"Promotion gate error: {e}")
    else:
        record.promotion_status = GATE_STATUS_APPROVED
        record.promotion_decision = GATE_STATUS_APPROVED

    return record
