from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewRequest, HumanApprovalScope, HumanReviewValidationResult,
    new_id, utc_now_iso,
    SCOPE_PATCH_SESSION,
    VALIDATION_VALID, VALIDATION_BLOCKED,
)
from agentx_evolve.human_review.approval_requests import create_review_request
from agentx_evolve.human_review.approval_lookup import validate_approval


def create_review_request_from_patch_session(
    patch_session: dict,
    risk_summary: dict,
    repo_root: Path,
) -> HumanReviewRequest:
    patch_session_id = patch_session.get("patch_session_id", patch_session.get("session_id", ""))
    requested_by = patch_session.get("requested_by", patch_session.get("requester_id", "patch_agent"))
    requested_action = patch_session.get("action", patch_session.get("description", "patch_session"))
    requested_effect = patch_session.get("effect", "modify_files")
    risk_level = risk_summary.get("risk_level", patch_session.get("risk_level", "MEDIUM"))
    reason = risk_summary.get("reason", patch_session.get("reason", "Patch session requiring human review"))
    file_paths = patch_session.get("file_paths", risk_summary.get("file_paths", []))
    scope = HumanApprovalScope(
        scope_id=new_id("scp"),
        scope_type=SCOPE_PATCH_SESSION,
        patch_session_id=patch_session_id,
        file_paths=file_paths,
        risk_level=risk_level,
        session_id=patch_session.get("session_id"),
        repo_identity_hash=patch_session.get("repo_identity_hash"),
        allowed_effects=risk_summary.get("allowed_effects", ["modify_files"]),
        blocked_effects=risk_summary.get("blocked_effects", []),
    )
    context = {
        "patch_session_id": patch_session_id,
        "risk_summary": risk_summary,
        "file_count": len(file_paths),
        "session_id": patch_session.get("session_id"),
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
    request.patch_session_id = patch_session_id
    return request


def validate_approval_for_patch_session(
    patch_session: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult:
    patch_session_id = patch_session.get("patch_session_id", patch_session.get("session_id", ""))
    requested_action = patch_session.get("action", patch_session.get("description", "patch_session"))
    requested_effect = patch_session.get("effect", "modify_files")
    file_paths = patch_session.get("file_paths", [])
    scope = HumanApprovalScope(
        scope_id=new_id("scp"),
        scope_type=SCOPE_PATCH_SESSION,
        patch_session_id=patch_session_id,
        file_paths=file_paths,
        session_id=patch_session.get("session_id"),
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
            reason="Patch session dependency unavailable; validation blocked",
            allowed=False,
            non_overridable_block_present=True,
        )
    return result
