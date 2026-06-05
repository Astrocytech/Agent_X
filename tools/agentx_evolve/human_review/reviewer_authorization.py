from __future__ import annotations
from pathlib import Path
import json
from agentx_evolve.human_review.review_models import (
    HumanReviewerIdentity, HumanReviewRequest, HumanApprovalScope,
    HumanReviewValidationResult,
    new_id, utc_now_iso,
    AUTH_LOCAL_CONFIG, AUTH_MANUAL_RECORD, AUTH_SIGNED_RECORD,
    AUTH_EXTERNAL_ASSERTION, AUTH_UNKNOWN,
    RISK_LEVEL_LOW, RISK_LEVEL_MEDIUM, RISK_LEVEL_HIGH, RISK_LEVEL_CRITICAL,
    ALL_RISK_LEVELS, VALIDATION_VALID, VALIDATION_BLOCKED,
)


def load_reviewer_authorization_policy(repo_root: Path) -> dict:
    path = repo_root / ".agentx-init" / "human_review" / "human_review_authorization_policy.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def validate_reviewer_authorization(
    reviewer: HumanReviewerIdentity,
    requested_action: str,
    requested_effect: str,
    risk_level: str,
    scope: HumanApprovalScope,
    context: dict,
    repo_root: Path,
) -> HumanReviewValidationResult:
    errors = []

    if not reviewer.reviewer_id:
        errors.append("reviewer_id is required")

    if reviewer.auth_method == AUTH_UNKNOWN:
        errors.append("unknown auth method is not authorized")

    if risk_level not in ALL_RISK_LEVELS:
        errors.append(f"invalid risk_level: {risk_level}")

    policy = load_reviewer_authorization_policy(repo_root)
    if policy:
        allowed_reviewers = policy.get("allowed_reviewers")
        if allowed_reviewers is not None and reviewer.reviewer_id not in allowed_reviewers:
            errors.append(f"reviewer {reviewer.reviewer_id} not in allowed_reviewers policy")

        max_risk = policy.get("max_risk_level")
        if max_risk:
            risk_rank = {
                RISK_LEVEL_LOW: 0, RISK_LEVEL_MEDIUM: 1,
                RISK_LEVEL_HIGH: 2, RISK_LEVEL_CRITICAL: 3,
            }
            if risk_rank.get(risk_level, 99) > risk_rank.get(max_risk, 0):
                errors.append(f"risk_level {risk_level} exceeds policy max {max_risk}")

    if errors:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            requested_action=requested_action,
            requested_effect=requested_effect,
            status=VALIDATION_BLOCKED,
            reason="; ".join(errors),
            allowed=False,
            non_overridable_block_present=True,
        )
    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        requested_action=requested_action,
        requested_effect=requested_effect,
        status=VALIDATION_VALID,
        allowed=True,
    )


def validate_separation_of_duties(
    reviewer: HumanReviewerIdentity,
    request: HumanReviewRequest,
    context: dict,
) -> HumanReviewValidationResult:
    if not reviewer.reviewer_id:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            request_id=request.request_id,
            requested_action=request.requested_action,
            requested_effect=request.requested_effect,
            status=VALIDATION_BLOCKED,
            reason="reviewer_id is required for separation-of-duties check",
            allowed=False,
            non_overridable_block_present=True,
        )

    if reviewer.reviewer_id == request.requested_by:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            request_id=request.request_id,
            requested_action=request.requested_action,
            requested_effect=request.requested_effect,
            status=VALIDATION_BLOCKED,
            reason="self-approval is blocked by separation-of-duties",
            allowed=False,
            non_overridable_block_present=True,
        )

    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        request_id=request.request_id,
        requested_action=request.requested_action,
        requested_effect=request.requested_effect,
        status=VALIDATION_VALID,
        allowed=True,
    )
