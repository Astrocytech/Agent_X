from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewRequest, HumanApprovalScope, HumanReviewValidationResult,
    new_id, utc_now_iso,
    SCOPE_TOOL_CALL,
    VALIDATION_VALID, VALIDATION_BLOCKED,
)
from agentx_evolve.human_review.approval_requests import create_review_request
from agentx_evolve.human_review.approval_lookup import validate_approval


def create_review_request_from_tool_call(
    tool_call: dict,
    tool_definition: dict,
    policy_decision: dict | None,
    repo_root: Path,
) -> HumanReviewRequest:
    tool_call_id = tool_call.get("tool_call_id", tool_call.get("id", ""))
    tool_name = tool_call.get("tool_name", tool_call.get("name", "unknown_tool"))
    requested_by = tool_call.get("requested_by", tool_call.get("requester_id", "tool_runner"))
    requested_action = f"tool:{tool_name}"
    requested_effect = tool_call.get("effect", tool_definition.get("effect", "execute_tool"))
    risk_level = tool_call.get("risk_level", tool_definition.get("risk_level", "LOW"))
    reason = tool_call.get("reason", tool_call.get("rationale", f"Tool call {tool_name}"))
    arguments = tool_call.get("arguments", tool_call.get("parameters", {}))
    tool_definition_id = tool_definition.get("tool_definition_id", tool_definition.get("id", ""))
    scope = HumanApprovalScope(
        scope_id=new_id("scp"),
        scope_type=SCOPE_TOOL_CALL,
        tool_call_id=tool_call_id,
        risk_level=risk_level,
        session_id=tool_call.get("session_id"),
        repo_identity_hash=tool_call.get("repo_identity_hash"),
        allowed_effects=tool_definition.get("allowed_effects", []),
        blocked_effects=tool_definition.get("blocked_effects", []),
    )
    context = {
        "tool_call_id": tool_call_id,
        "tool_name": tool_name,
        "tool_definition_id": tool_definition_id,
        "arguments": arguments,
        "session_id": tool_call.get("session_id"),
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
    request.tool_call_id = tool_call_id
    if policy_decision:
        request.policy_decision_id = policy_decision.get("policy_decision_id", policy_decision.get("decision_id"))
    return request


def validate_approval_for_tool_call(
    tool_call: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult:
    tool_name = tool_call.get("tool_name", tool_call.get("name", "unknown_tool"))
    requested_action = f"tool:{tool_name}"
    requested_effect = tool_call.get("effect", "execute_tool")
    tool_call_id = tool_call.get("tool_call_id", tool_call.get("id", ""))
    scope = HumanApprovalScope(
        scope_id=new_id("scp"),
        scope_type=SCOPE_TOOL_CALL,
        tool_call_id=tool_call_id,
        session_id=tool_call.get("session_id"),
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
            reason="Tool registry dependency unavailable; validation blocked",
            allowed=False,
            non_overridable_block_present=True,
        )
    return result
