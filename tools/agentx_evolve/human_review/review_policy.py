from __future__ import annotations
from agentx_evolve.human_review.review_models import (
    HumanReviewerIdentity, HumanReviewRequest, HumanReviewValidationResult,
    new_id, utc_now_iso,
    AUTH_LOCAL_CONFIG, AUTH_MANUAL_RECORD, AUTH_SIGNED_RECORD,
    AUTH_EXTERNAL_ASSERTION, AUTH_UNKNOWN,
    RISK_LEVEL_LOW, RISK_LEVEL_MEDIUM, RISK_LEVEL_HIGH, RISK_LEVEL_CRITICAL,
)


def check_reviewer_authorization(
    reviewer: HumanReviewerIdentity,
    request: HumanReviewRequest,
) -> HumanReviewValidationResult:
    errors = []
    if not reviewer.reviewer_id:
        errors.append("reviewer_id is required")
    if not reviewer.reviewer_label:
        errors.append("reviewer_label is required")
    if not reviewer.reviewer_role:
        errors.append("reviewer_role is required")
    if reviewer.auth_method == AUTH_UNKNOWN:
        errors.append("unknown auth method is not authorized")
    if reviewer.reviewer_id == request.requested_by:
        errors.append("self-approval is blocked")
    if errors:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            request_id=request.request_id,
            requested_action=request.requested_action,
            requested_effect=request.requested_effect,
            status="BLOCKED",
            reason="; ".join(errors),
            allowed=False,
        )
    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        request_id=request.request_id,
        requested_action=request.requested_action,
        requested_effect=request.requested_effect,
        status="VALID",
        allowed=True,
    )


def check_separation_of_duties(
    requester_id: str,
    reviewer_id: str,
) -> bool:
    if requester_id == reviewer_id:
        return False
    return True


def check_non_overridable_blocks(
    policy_allowed: bool = True,
    sandbox_allowed: bool = True,
    schema_valid: bool = True,
) -> bool:
    if not policy_allowed:
        return False
    if not sandbox_allowed:
        return False
    if not schema_valid:
        return False
    return True
