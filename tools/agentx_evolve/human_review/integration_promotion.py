from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewRequest, HumanApprovalScope, HumanReviewValidationResult,
    new_id, utc_now_iso,
    SCOPE_PROMOTION,
    VALIDATION_VALID, VALIDATION_BLOCKED,
)
from agentx_evolve.human_review.approval_requests import create_review_request
from agentx_evolve.human_review.approval_lookup import validate_approval


def create_review_request_from_promotion_request(
    promotion_request: dict,
    validation_summary: dict,
    repo_root: Path,
) -> HumanReviewRequest:
    promotion_request_id = promotion_request.get("promotion_request_id", promotion_request.get("request_id", ""))
    requested_by = promotion_request.get("requested_by", promotion_request.get("requester_id", "promotion_agent"))
    requested_action = promotion_request.get("action", "promotion")
    requested_effect = promotion_request.get("effect", "promote_artifacts")
    risk_level = validation_summary.get("risk_level", promotion_request.get("risk_level", "HIGH"))
    reason = validation_summary.get("reason", promotion_request.get("reason", "Promotion requiring human review"))
    artifact_refs = promotion_request.get("artifact_refs", validation_summary.get("artifact_refs", []))
    commit_hashes = validation_summary.get("commit_hashes", promotion_request.get("commit_hashes", []))
    scope = HumanApprovalScope(
        scope_id=new_id("scp"),
        scope_type=SCOPE_PROMOTION,
        promotion_request_id=promotion_request_id,
        artifact_hashes=artifact_refs,
        commit_hashes=commit_hashes,
        risk_level=risk_level,
        session_id=promotion_request.get("session_id"),
        repo_identity_hash=promotion_request.get("repo_identity_hash"),
        allowed_effects=validation_summary.get("allowed_effects", ["promote_artifacts"]),
        blocked_effects=validation_summary.get("blocked_effects", []),
    )
    context = {
        "promotion_request_id": promotion_request_id,
        "validation_summary": validation_summary,
        "artifact_count": len(artifact_refs),
        "session_id": promotion_request.get("session_id"),
    }
    request = create_review_request(
        requested_by=requested_by,
        requested_action=requested_action,
        requested_effect=requested_effect,
        risk_level=risk_level,
        reason=reason,
        scope=scope,
        context=context,
        repo_root=repo_root,
    )
    request.promotion_request_id = promotion_request_id
    return request


def validate_approval_for_promotion(
    promotion_request: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult:
    promotion_request_id = promotion_request.get("promotion_request_id", promotion_request.get("request_id", ""))
    requested_action = promotion_request.get("action", "promotion")
    requested_effect = promotion_request.get("effect", "promote_artifacts")
    artifact_refs = promotion_request.get("artifact_refs", [])
    commit_hashes = promotion_request.get("commit_hashes", [])
    scope = HumanApprovalScope(
        scope_id=new_id("scp"),
        scope_type=SCOPE_PROMOTION,
        promotion_request_id=promotion_request_id,
        artifact_hashes=artifact_refs,
        commit_hashes=commit_hashes,
        session_id=promotion_request.get("session_id"),
    )
    try:
        result = validate_approval(
            approval_id=approval_decision_id,
            requested_action=requested_action,
            requested_effect=requested_effect,
            scope=scope,
            repo_root=repo_root,
        )
    except Exception:
        result = HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            approval_decision_id=approval_decision_id,
            requested_action=requested_action,
            requested_effect=requested_effect,
            status=VALIDATION_BLOCKED,
            reason="Promotion dependency unavailable; validation blocked",
            allowed=False,
            non_overridable_block_present=True,
        )
    return result
