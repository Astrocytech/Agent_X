from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewRequest, HumanApprovalScope, HumanReviewValidationResult,
    new_id, utc_now_iso, sha256_dict, canonical_hash_payload,
    SOURCE_COMPONENT, REQ_PENDING,
)
from agentx_evolve.human_review.review_queue import enqueue_request


def create_review_request(
    requested_by: str,
    requested_action: str,
    requested_effect: str,
    risk_level: str,
    reason: str,
    scope: HumanApprovalScope,
    context: dict,
    repo_root: Path,
) -> HumanReviewRequest:
    now = utc_now_iso()
    request = HumanReviewRequest(
        request_id=new_id("hreq"),
        created_at=now,
        requested_by=requested_by,
        requested_action=requested_action,
        requested_effect=requested_effect,
        risk_level=risk_level,
        reason=reason,
        scope=scope,
        status=REQ_PENDING,
    )
    payload = canonical_hash_payload(request.to_dict())
    request.request_hash = sha256_dict(payload)
    enqueue_request(request, repo_root)
    return request


def add_request_to_queue(
    request: HumanReviewRequest,
    repo_root: Path,
) -> dict:
    return enqueue_request(request, repo_root)


def validate_review_request(
    request: HumanReviewRequest,
) -> HumanReviewValidationResult:
    errors = []
    if not request.requested_action:
        errors.append("requested_action is required")
    if not request.requested_effect:
        errors.append("requested_effect is required")
    if not request.reason:
        errors.append("reason is required")
    if not request.requested_by:
        errors.append("requested_by is required")
    if request.risk_level not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        errors.append(f"invalid risk_level: {request.risk_level}")
    if errors:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            request_id=request.request_id,
            requested_action=request.requested_action,
            requested_effect=request.requested_effect,
            status="INVALID",
            reason="; ".join(errors),
            allowed=False,
            errors=errors,
        )
    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        request_id=request.request_id,
        requested_action=request.requested_action,
        requested_effect=request.requested_effect,
        status="VALID",
        matched_scope=True,
        allowed=True,
    )
