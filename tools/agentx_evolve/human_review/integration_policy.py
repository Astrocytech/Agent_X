from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewRequest, HumanApprovalScope, HumanReviewValidationResult,
    new_id, utc_now_iso,
    SCOPE_ACTION,
    VALIDATION_VALID, VALIDATION_BLOCKED,
)
from agentx_evolve.human_review.approval_requests import create_review_request
from agentx_evolve.human_review.approval_lookup import validate_approval


def create_review_request_from_policy_decision(
    policy_decision: dict,
    context: dict,
    repo_root: Path,
) -> HumanReviewRequest:
    requested_by = policy_decision.get("requested_by", context.get("requester_id", "policy_engine"))
    requested_action = policy_decision.get("action", "unknown_action")
    requested_effect = policy_decision.get("effect", "unknown_effect")
    risk_level = policy_decision.get("risk_level", "LOW")
    reason = policy_decision.get("reason", policy_decision.get("rationale", ""))
    policy_decision_id = policy_decision.get("policy_decision_id", policy_decision.get("decision_id", ""))
    scope = HumanApprovalScope(
        scope_id=new_id("scp"),
        scope_type=SCOPE_ACTION,
        action_id=requested_action,
        policy_decision_id=policy_decision_id,
        risk_level=risk_level,
        session_id=context.get("session_id"),
        repo_identity_hash=context.get("repo_identity_hash"),
        allowed_effects=policy_decision.get("allowed_effects", []),
        blocked_effects=policy_decision.get("blocked_effects", []),
    )
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
    request.policy_decision_id = policy_decision_id
    return request


def validate_approval_for_policy_decision(
    policy_decision: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult:
    requested_action = policy_decision.get("action", "unknown_action")
    requested_effect = policy_decision.get("effect", "unknown_effect")
    scope_dict = policy_decision.get("scope", {})
    scope = HumanApprovalScope(
        scope_id=scope_dict.get("scope_id", ""),
        scope_type=scope_dict.get("scope_type", SCOPE_ACTION),
        policy_decision_id=policy_decision.get("policy_decision_id", policy_decision.get("decision_id")),
        risk_level=scope_dict.get("risk_level", policy_decision.get("risk_level")),
        allowed_effects=scope_dict.get("allowed_effects", policy_decision.get("allowed_effects", [])),
        blocked_effects=scope_dict.get("blocked_effects", policy_decision.get("blocked_effects", [])),
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
            requested_action=requested_action,
            requested_effect=requested_effect,
            status=VALIDATION_BLOCKED,
            reason="Policy/Capability Registry dependency unavailable; validation blocked",
            allowed=False,
            non_overridable_block_present=True,
        )
    return result
