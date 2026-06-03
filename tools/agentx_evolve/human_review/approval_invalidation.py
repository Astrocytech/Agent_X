from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanApprovalDecision, HumanReviewValidationResult,
    new_id, utc_now_iso, sha256_dict, append_jsonl, human_review_runs_dir,
    VALIDATION_VALID, VALIDATION_STALE, VALIDATION_REPLAYED,
    VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH,
)
import json


def check_approval_context_drift(
    decision: HumanApprovalDecision,
    current_context: dict,
    repo_root: Path,
) -> HumanReviewValidationResult:
    vid = new_id("val")
    vtime = utc_now_iso()
    scope = decision.scope

    ctx_repo = current_context.get("repo_identity_hash")
    ctx_sess = current_context.get("session_id")

    if scope:
        if scope.repo_identity_hash and ctx_repo and scope.repo_identity_hash != ctx_repo:
            return HumanReviewValidationResult(
                validation_id=vid,
                validated_at=vtime,
                approval_decision_id=decision.decision_id,
                request_id=decision.request_id,
                status=VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH,
                reason="Repo identity hash does not match approved context",
                replay_or_context_mismatch=True,
                allowed=False,
            )
        if scope.session_id and ctx_sess and scope.session_id != ctx_sess:
            return HumanReviewValidationResult(
                validation_id=vid,
                validated_at=vtime,
                approval_decision_id=decision.decision_id,
                request_id=decision.request_id,
                status=VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH,
                reason="Session ID does not match approved context",
                replay_or_context_mismatch=True,
                allowed=False,
            )

    if _detect_context_replay(decision.decision_id, current_context, repo_root):
        return HumanReviewValidationResult(
            validation_id=vid,
            validated_at=vtime,
            approval_decision_id=decision.decision_id,
            request_id=decision.request_id,
            status=VALIDATION_REPLAYED,
            reason="Context replay detected: identical context already consumed",
            replay_or_context_mismatch=True,
            allowed=False,
        )

    if _detect_context_staleness(decision, current_context):
        return HumanReviewValidationResult(
            validation_id=vid,
            validated_at=vtime,
            approval_decision_id=decision.decision_id,
            request_id=decision.request_id,
            status=VALIDATION_STALE,
            reason="Context is stale",
            allowed=False,
        )

    return HumanReviewValidationResult(
        validation_id=vid,
        validated_at=vtime,
        approval_decision_id=decision.decision_id,
        request_id=decision.request_id,
        status=VALIDATION_VALID,
        matched_scope=True,
        allowed=True,
    )


def _detect_context_replay(decision_id: str, context: dict, repo_root: Path) -> bool:
    path = human_review_runs_dir(repo_root) / "approval_invalidation_history.jsonl"
    if not path.exists():
        return False
    context_fp = sha256_dict(context) if context else ""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("approval_decision_id") == decision_id:
                stored_ctx = data.get("context", {})
                if sha256_dict(stored_ctx) == context_fp:
                    return True
    return False


def _detect_context_staleness(decision: HumanApprovalDecision, context: dict) -> bool:
    ctx_ts = context.get("context_timestamp") or context.get("timestamp")
    if not ctx_ts or not decision.decided_at:
        return False
    try:
        from datetime import datetime, timezone
        ctx_dt = datetime.fromisoformat(ctx_ts)
        if ctx_dt.tzinfo is None:
            ctx_dt = ctx_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - ctx_dt).total_seconds() > 3600
    except (ValueError, TypeError):
        return False


def invalidate_approval_on_context_drift(
    approval_decision_id: str,
    drift_reason: str,
    current_context: dict,
    repo_root: Path,
) -> dict:
    from agentx_evolve.human_review.approval_lookup import lookup_approval
    decision = lookup_approval(approval_decision_id, repo_root)
    if decision is None:
        return {"error": f"Approval {approval_decision_id} not found"}
    check_result = check_approval_context_drift(decision, current_context, repo_root)
    record = append_approval_invalidation_record(
        approval_decision_id=approval_decision_id,
        reason=drift_reason,
        context=current_context,
        repo_root=repo_root,
    )
    return {
        "approval_decision_id": approval_decision_id,
        "drift_detected": check_result.status != VALIDATION_VALID,
        "validation_status": check_result.status,
        "record": record,
    }


def append_approval_invalidation_record(
    approval_decision_id: str,
    reason: str,
    context: dict,
    repo_root: Path,
) -> dict:
    entry = {
        "invalidation_id": new_id("inv"),
        "approval_decision_id": approval_decision_id,
        "reason": reason,
        "context": context,
        "invalidated_at": utc_now_iso(),
    }
    append_jsonl(human_review_runs_dir(repo_root) / "approval_invalidation_history.jsonl", entry)
    return entry
