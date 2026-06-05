from __future__ import annotations
from pathlib import Path
from agentx_evolve.model.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, RiskAcceptance,
    ApprovalReference, GitEvidence, PromotionGateDecision,
    canonical_json, sha256_dict, from_dict, to_dict,
    CS_NOT_RUN, CS_PASS, CS_FAIL,
    PC_APPROVED, PC_BLOCKED, PC_NEEDS_APPROVAL, PC_NEEDS_GOVERNANCE,
    PC_NEEDS_VALIDATION, PC_EXPIRED, PC_INVALID, PC_FAILED, PC_DRY_RUN,
    PD_PROMOTE, PD_BLOCK, PD_DEFER, PD_EXPIRE, PD_INVALIDATE,
    PD_REQUEST_APPROVAL, PD_REQUEST_GOVERNANCE, PD_REQUEST_VALIDATION,
    PD_DRY_RUN_ONLY,
    FC_CANDIDATE_MISSING, FC_CANDIDATE_INVALID, FC_LOCK_UNAVAILABLE,
)
from agentx_evolve.promotion.gate_policy import (
    collect_promotion_blockers, has_non_overridable_blocker,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


def create_gate_decision(
    candidate: ReleaseCandidate | None,
    validation_evidence: ValidationEvidence | None,
    risk_acceptance: RiskAcceptance | None,
    approvals: list[ApprovalReference] | None,
    git_evidence: GitEvidence | None,
    policy_context: dict,
    integration_context: dict,
    repo_root: Path,
    dry_run: bool = False,
) -> PromotionGateDecision:
    blockers = collect_promotion_blockers(
        candidate, validation_evidence, risk_acceptance,
        approvals, git_evidence, policy_context,
        integration_context, repo_root,
    )

    decision_id = new_id("gd-")
    now = utc_now_iso()

    if candidate is None:
        return PromotionGateDecision(
            decision_id=decision_id,
            created_at=now,
            decision=PD_BLOCK,
            status=PC_FAILED,
            reason="No release candidate provided",
            blocking_failures=blockers,
            dry_run=dry_run,
        )

    if has_non_overridable_blocker(blockers):
        decision = PD_BLOCK
        status = PC_BLOCKED
        reason = "Non-overridable blockers prevent promotion"
    elif not blockers:
        if dry_run:
            decision = PD_DRY_RUN_ONLY
            status = PC_DRY_RUN
            reason = "Dry run: promotion would be approved"
        else:
            decision = PD_PROMOTE
            status = PC_APPROVED
            reason = "All checks passed"
    else:
        failure_classes = {b["failure_class"] for b in blockers}
        if FC_CANDIDATE_MISSING in failure_classes or FC_CANDIDATE_INVALID in failure_classes:
            decision = PD_INVALIDATE
            status = PC_INVALID
            reason = "Candidate is invalid"
        elif FC_LOCK_UNAVAILABLE in failure_classes:
            decision = PD_BLOCK
            status = PC_BLOCKED
            reason = "Promotion lock unavailable"
        elif any("APPROVAL" in fc for fc in failure_classes):
            decision = PD_REQUEST_APPROVAL
            status = PC_NEEDS_APPROVAL
            reason = "Approval checks failed"
        elif any("RISK" in fc for fc in failure_classes):
            decision = PD_REQUEST_GOVERNANCE
            status = PC_NEEDS_GOVERNANCE
            reason = "Risk checks require governance"
        elif any("VALIDATION" in fc or "EVIDENCE" in fc for fc in failure_classes):
            decision = PD_REQUEST_VALIDATION
            status = PC_NEEDS_VALIDATION
            reason = "Validation checks failed"
        elif any("EXPIRED" in fc for fc in failure_classes):
            decision = PD_EXPIRE
            status = PC_EXPIRED
            reason = "Candidate or evidence expired"
        else:
            decision = PD_BLOCK
            status = PC_BLOCKED
            reason = f"Blocked by {len(blockers)} failure(s)"

    passed_checks = []
    failed_checks = []
    for b in blockers:
        failed_checks.append(b.get("failure_class", FC_CANDIDATE_INVALID))
    if not blockers:
        passed_checks.append("all_checks_passed")

    idempotency_key = compute_decision_idempotency_key(
        candidate, validation_evidence, approvals, risk_acceptance, git_evidence,
    )

    decision_record = PromotionGateDecision(
        decision_id=decision_id,
        idempotency_key=idempotency_key,
        created_at=now,
        component_id=candidate.component_id,
        candidate_id=candidate.candidate_id,
        source_commit=candidate.source_commit,
        decision=decision,
        status=status,
        reason=reason,
        checks_run=[{"check": c.get("failure_class", ""), "result": "FAIL"} for c in blockers] or [{"check": "all_checks", "result": "PASS"}],
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        blocking_failures=blockers,
        required_approvals_status=CS_PASS if not any("APPROVAL" in b.get("failure_class", "") for b in blockers) else CS_FAIL,
        validation_status=CS_PASS if not any("VALIDATION" in b.get("failure_class", "") for b in blockers) else CS_FAIL,
        risk_status=CS_PASS if not any("RISK" in b.get("failure_class", "") for b in blockers) else CS_FAIL,
        policy_status=CS_PASS if not any("POLICY" in b.get("failure_class", "") for b in blockers) else CS_FAIL,
        git_status=CS_PASS if not any("GIT" in b.get("failure_class", "") for b in blockers) else CS_FAIL,
        expiry_status=CS_PASS if not any("EXPIRED" in b.get("failure_class", "") for b in blockers) else CS_FAIL,
        dry_run=dry_run,
    )
    decision_record.gate_decision_hash = sha256_dict(
        {k: v for k, v in to_dict(decision_record).items() if k != "gate_decision_hash"}
    )
    return decision_record


def validate_gate_decision(decision: PromotionGateDecision) -> list[str]:
    errors: list[str] = []
    if decision.schema_id != "promotion_gate_decision.schema.json":
        errors.append(f"schema_id mismatch: {decision.schema_id}")
    if not decision.decision_id:
        errors.append("decision_id is empty")
    if not decision.gate_decision_hash:
        errors.append("gate_decision_hash is empty")
    if decision.decision not in (
        PD_PROMOTE, PD_BLOCK, PD_DEFER, PD_EXPIRE, PD_INVALIDATE,
        PD_REQUEST_APPROVAL, PD_REQUEST_GOVERNANCE, PD_REQUEST_VALIDATION,
        PD_DRY_RUN_ONLY,
    ):
        errors.append(f"Unknown decision: {decision.decision}")
    if decision.status not in (
        PC_APPROVED, PC_BLOCKED, PC_NEEDS_APPROVAL, PC_NEEDS_GOVERNANCE,
        PC_NEEDS_VALIDATION, PC_EXPIRED, PC_INVALID, PC_FAILED, PC_DRY_RUN,
    ):
        errors.append(f"Unknown status: {decision.status}")
    return errors


def is_promotion_approved(decision: PromotionGateDecision) -> bool:
    return decision.status == PC_APPROVED and decision.decision == PD_PROMOTE


def compute_decision_idempotency_key(
    candidate: ReleaseCandidate | None,
    validation_evidence: ValidationEvidence | None,
    approvals: list[ApprovalReference] | None,
    risk_acceptance: RiskAcceptance | None,
    git_evidence: GitEvidence | None,
) -> str:
    payload: dict = {}
    if candidate:
        payload["candidate_id"] = candidate.candidate_id
        payload["candidate_hash"] = candidate.candidate_hash
        payload["source_commit"] = candidate.source_commit
    if validation_evidence:
        payload["validation_evidence_id"] = validation_evidence.evidence_id
        payload["validation_evidence_hash"] = validation_evidence.evidence_hash
    if approvals:
        payload["approval_ids"] = sorted(a.approval_id for a in approvals)
        payload["approval_hashes"] = sorted(a.approval_hash for a in approvals if a.approval_hash)
    if risk_acceptance:
        payload["risk_acceptance_id"] = risk_acceptance.risk_acceptance_id
        payload["risk_acceptance_hash"] = risk_acceptance.risk_acceptance_hash
    if git_evidence:
        payload["git_evidence_id"] = git_evidence.git_evidence_id
        payload["git_evidence_hash"] = git_evidence.git_evidence_hash
    return sha256_dict(payload)
