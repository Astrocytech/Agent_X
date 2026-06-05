from __future__ import annotations
from agentx_evolve.human_review.review_models import (
    HumanApprovalScope, HumanReviewValidationResult,
    new_id, utc_now_iso,
    SCOPE_ACTION, SCOPE_TOOL_CALL, SCOPE_PATCH_SESSION,
    SCOPE_FILE_PATH, SCOPE_COMMIT, SCOPE_PROMOTION, SCOPE_SESSION,
    VALIDATION_VALID, VALIDATION_INVALID, VALIDATION_BLOCKED, VALIDATION_OUT_OF_SCOPE,
)


def scope_matches_action(
    scope: HumanApprovalScope,
    requested_action: str,
    requested_effect: str,
    scope_context: dict,
) -> bool:
    if scope.scope_type == SCOPE_ACTION:
        if scope.action_id and scope.action_id != requested_action:
            return False
        if scope.allowed_effects and requested_effect not in scope.allowed_effects:
            return False
        if scope.blocked_effects and requested_effect in scope.blocked_effects:
            return False
        return True

    if scope.scope_type == SCOPE_TOOL_CALL:
        tool_call_id = scope_context.get("tool_call_id")
        if not tool_call_id:
            return False
        if scope.tool_call_id and scope.tool_call_id != tool_call_id:
            return False
        return True

    if scope.scope_type == SCOPE_PATCH_SESSION:
        patch_session_id = scope_context.get("patch_session_id")
        if not patch_session_id:
            return False
        if scope.patch_session_id and scope.patch_session_id != patch_session_id:
            return False
        return True

    if scope.scope_type == SCOPE_FILE_PATH:
        file_paths = scope_context.get("file_paths", [])
        if not file_paths:
            return False
        if scope.file_paths:
            return any(fp in file_paths for fp in scope.file_paths)
        return True

    if scope.scope_type == SCOPE_COMMIT:
        commit_hashes = scope_context.get("commit_hashes", [])
        if not commit_hashes:
            return False
        if scope.commit_hashes:
            return any(ch in commit_hashes for ch in scope.commit_hashes)
        return True

    if scope.scope_type == SCOPE_PROMOTION:
        promotion_request_id = scope_context.get("promotion_request_id")
        if not promotion_request_id:
            return False
        if scope.promotion_request_id and scope.promotion_request_id != promotion_request_id:
            return False
        return True

    if scope.scope_type == SCOPE_SESSION:
        session_id = scope_context.get("session_id")
        if not session_id:
            return False
        if scope.session_id and scope.session_id != session_id:
            return False
        return True

    return False


def normalize_scope(scope: HumanApprovalScope) -> HumanApprovalScope:
    return HumanApprovalScope(
        scope_id=scope.scope_id,
        scope_type=scope.scope_type,
        action_id=scope.action_id,
        tool_call_id=scope.tool_call_id,
        patch_session_id=scope.patch_session_id,
        promotion_request_id=scope.promotion_request_id,
        policy_decision_id=scope.policy_decision_id,
        file_paths=sorted(scope.file_paths) if scope.file_paths else [],
        commit_hashes=sorted(scope.commit_hashes) if scope.commit_hashes else [],
        artifact_hashes=sorted(scope.artifact_hashes) if scope.artifact_hashes else [],
        session_id=scope.session_id,
        allowed_effects=sorted(scope.allowed_effects) if scope.allowed_effects else [],
        blocked_effects=sorted(scope.blocked_effects) if scope.blocked_effects else [],
        risk_level=scope.risk_level,
        repo_identity_hash=scope.repo_identity_hash,
        warnings=list(scope.warnings),
        errors=list(scope.errors),
    )


def validate_scope(scope: HumanApprovalScope) -> HumanReviewValidationResult:
    errors = []
    if not scope.scope_id:
        errors.append("scope_id is required")
    if not scope.scope_type:
        errors.append("scope_type is required")
    if scope.errors:
        errors.extend(scope.errors)
    if errors:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            status=VALIDATION_INVALID,
            reason="; ".join(errors),
            allowed=False,
        )
    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        status=VALIDATION_VALID,
        allowed=True,
    )


def assert_scope_not_broadened(
    requested_scope: HumanApprovalScope,
    approval_scope: HumanApprovalScope,
) -> HumanReviewValidationResult:
    errors = []
    if approval_scope.scope_type != requested_scope.scope_type:
        errors.append(
            f"scope_type mismatch: requested={requested_scope.scope_type}, "
            f"approval={approval_scope.scope_type}"
        )

    if approval_scope.file_paths and requested_scope.file_paths:
        extra_paths = set(approval_scope.file_paths) - set(requested_scope.file_paths)
        if extra_paths:
            errors.append(f"approval includes file_paths not in request: {sorted(extra_paths)}")

    if approval_scope.commit_hashes and requested_scope.commit_hashes:
        extra_hashes = set(approval_scope.commit_hashes) - set(requested_scope.commit_hashes)
        if extra_hashes:
            errors.append(f"approval includes commit_hashes not in request: {sorted(extra_hashes)}")

    if approval_scope.artifact_hashes and requested_scope.artifact_hashes:
        extra_artifacts = set(approval_scope.artifact_hashes) - set(requested_scope.artifact_hashes)
        if extra_artifacts:
            errors.append(f"approval includes artifact_hashes not in request: {sorted(extra_artifacts)}")

    if approval_scope.allowed_effects and requested_scope.allowed_effects:
        extra_effects = set(approval_scope.allowed_effects) - set(requested_scope.allowed_effects)
        if extra_effects:
            errors.append(f"approval includes allowed_effects not in request: {sorted(extra_effects)}")

    if approval_scope.action_id and requested_scope.action_id:
        if approval_scope.action_id != requested_scope.action_id:
            errors.append("approval action_id differs from requested action_id")

    if approval_scope.tool_call_id and requested_scope.tool_call_id:
        if approval_scope.tool_call_id != requested_scope.tool_call_id:
            errors.append("approval tool_call_id differs from requested tool_call_id")

    if approval_scope.patch_session_id and requested_scope.patch_session_id:
        if approval_scope.patch_session_id != requested_scope.patch_session_id:
            errors.append("approval patch_session_id differs from requested patch_session_id")

    if errors:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            status=VALIDATION_BLOCKED,
            reason="; ".join(errors),
            allowed=False,
            non_overridable_block_present=True,
        )
    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        status=VALIDATION_VALID,
        allowed=True,
    )
