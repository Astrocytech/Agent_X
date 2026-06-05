from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanApprovalDecision, HumanRejectionDecision, HumanDeferralDecision,
    HumanClarificationRequest, HumanReviewerIdentity, HumanApprovalScope,
    HumanReviewRequest, HumanReviewAuditEvent,
    new_id, utc_now_iso, sha256_dict, canonical_hash_payload,
    atomic_write_json, append_jsonl, human_review_runs_dir,
    SOURCE_COMPONENT, DECISION_APPROVED, DECISION_REJECTED,
    DECISION_DEFERRED, DECISION_NEEDS_CLARIFICATION,
    REQ_APPROVED, REQ_REJECTED, REQ_DEFERRED, REQ_NEEDS_CLARIFICATION,
)
from agentx_evolve.human_review.review_queue import load_queue, resolve_request, save_queue


def _record_decision_common(repo_root: Path, history_file: str, latest_file: str, payload: dict) -> dict:
    append_jsonl(human_review_runs_dir(repo_root) / history_file, payload)
    return atomic_write_json(human_review_runs_dir(repo_root) / latest_file, payload)


def record_approval_decision(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    reason: str,
    scope: HumanApprovalScope,
    expires_at: str | None,
    no_expiry_reason: str | None,
    context: dict,
    repo_root: Path,
) -> HumanApprovalDecision:
    now = utc_now_iso()
    decision = HumanApprovalDecision(
        decision_id=new_id("hdec"),
        request_id=request_id,
        decided_at=now,
        reviewer=reviewer,
        decision=DECISION_APPROVED,
        reason=reason,
        scope=scope,
        expires_at=expires_at,
        no_expiry_reason=no_expiry_reason,
    )
    payload = canonical_hash_payload(decision.to_dict())
    decision.decision_hash = sha256_dict(payload)
    _record_decision_common(repo_root, "approval_decision_history.jsonl", "latest_approval_decision.json", decision.to_dict())
    resolve_request(request_id, repo_root)
    return decision


def record_rejection_decision(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    reason: str,
    context: dict,
    repo_root: Path,
) -> HumanRejectionDecision:
    now = utc_now_iso()
    decision = HumanRejectionDecision(
        decision_id=new_id("hdec"),
        request_id=request_id,
        decided_at=now,
        reviewer=reviewer,
        reason=reason,
    )
    payload = canonical_hash_payload(decision.to_dict())
    decision.decision_hash = sha256_dict(payload)
    _record_decision_common(repo_root, "rejection_decision_history.jsonl", "latest_rejection_decision.json", decision.to_dict())
    resolve_request(request_id, repo_root)
    return decision


def record_deferral_decision(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    reason: str,
    deferred_until: str | None,
    context: dict,
    repo_root: Path,
) -> HumanDeferralDecision:
    now = utc_now_iso()
    decision = HumanDeferralDecision(
        decision_id=new_id("hdec"),
        request_id=request_id,
        decided_at=now,
        reviewer=reviewer,
        reason=reason,
        deferred_until=deferred_until,
    )
    payload = canonical_hash_payload(decision.to_dict())
    decision.decision_hash = sha256_dict(payload)
    _record_decision_common(repo_root, "deferral_decision_history.jsonl", "latest_deferral_decision.json", decision.to_dict())
    queue = load_queue(repo_root)
    if request_id not in queue.deferred_requests:
        queue.deferred_requests.append(request_id)
    save_queue(queue, repo_root)
    return decision


def record_clarification_request(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    question: str,
    context: dict,
    repo_root: Path,
) -> HumanClarificationRequest:
    now = utc_now_iso()
    clarification = HumanClarificationRequest(
        clarification_id=new_id("hcla"),
        request_id=request_id,
        created_at=now,
        reviewer=reviewer,
        clarification_question=question,
    )
    payload = canonical_hash_payload(clarification.to_dict())
    clarification.clarification_hash = sha256_dict(payload)
    _record_decision_common(repo_root, "clarification_request_history.jsonl", "latest_clarification_request.json", clarification.to_dict())
    queue = load_queue(repo_root)
    if request_id not in queue.clarification_requests:
        queue.clarification_requests.append(request_id)
    save_queue(queue, repo_root)
    return clarification
