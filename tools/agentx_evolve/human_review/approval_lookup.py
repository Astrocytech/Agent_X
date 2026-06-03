from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanApprovalDecision, HumanReviewValidationResult, HumanApprovalScope,
    new_id, utc_now_iso, append_jsonl, human_review_runs_dir,
    VALIDATION_VALID, VALIDATION_INVALID, VALIDATION_MISSING,
    VALIDATION_OUT_OF_SCOPE, VALIDATION_REPLAYED,
    VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH, VALIDATION_BLOCKED,
)
from agentx_evolve.human_review.approval_expiry import check_expiry
from agentx_evolve.human_review.approval_revocation import is_revoked


def lookup_approval(approval_id: str, repo_root: Path) -> HumanApprovalDecision | None:
    import json
    path = human_review_runs_dir(repo_root) / "approval_decision_history.jsonl"
    if not path.exists():
        return None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("decision_id") == approval_id:
                return _decision_from_dict(data)
    return None


def _scope_from_dict(data: dict) -> HumanApprovalScope | None:
    if not data:
        return None
    return HumanApprovalScope(
        scope_id=data.get("scope_id", ""),
        scope_type=data.get("scope_type", ""),
        action_id=data.get("action_id"),
        tool_call_id=data.get("tool_call_id"),
        patch_session_id=data.get("patch_session_id"),
        promotion_request_id=data.get("promotion_request_id"),
        policy_decision_id=data.get("policy_decision_id"),
        file_paths=data.get("file_paths", []),
        commit_hashes=data.get("commit_hashes", []),
        artifact_hashes=data.get("artifact_hashes", []),
        session_id=data.get("session_id"),
        allowed_effects=data.get("allowed_effects", []),
        blocked_effects=data.get("blocked_effects", []),
        risk_level=data.get("risk_level"),
        repo_identity_hash=data.get("repo_identity_hash"),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
    )


def _decision_from_dict(data: dict) -> HumanApprovalDecision:
    return HumanApprovalDecision(
        decision_id=data.get("decision_id", ""),
        request_id=data.get("request_id", ""),
        decided_at=data.get("decided_at", ""),
        decision=data.get("decision", "APPROVED"),
        reason=data.get("reason", ""),
        scope=_scope_from_dict(data.get("scope")),
        expires_at=data.get("expires_at"),
        no_expiry_reason=data.get("no_expiry_reason"),
        request_hash=data.get("request_hash"),
        decision_hash=data.get("decision_hash"),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
    )


def find_active_approval_for_action(
    requested_action: str,
    requested_effect: str,
    scope_context: dict,
    repo_root: Path,
) -> HumanApprovalDecision | None:
    import json
    path = human_review_runs_dir(repo_root) / "approval_decision_history.jsonl"
    if not path.exists():
        return None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("decision") != "APPROVED":
                continue
            decision = _decision_from_dict(data)
            if is_revoked(decision.decision_id, repo_root):
                continue
            expiry = check_expiry(decision.decision_id, repo_root)
            if expiry.expired:
                continue
            return decision
    return None


def validate_approval_id(
    approval_decision_id: str | None,
    required_action: str,
    required_effect: str,
    scope_context: dict,
    repo_root: Path,
) -> HumanReviewValidationResult:
    if not approval_decision_id:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            requested_action=required_action,
            requested_effect=required_effect,
            status=VALIDATION_MISSING,
            reason="No approval_decision_id provided",
            allowed=False,
        )
    return validate_approval(approval_decision_id, required_action, required_effect, None, repo_root)


def validate_approval(
    approval_id: str,
    requested_action: str,
    requested_effect: str,
    scope: HumanApprovalScope | None,
    repo_root: Path,
) -> HumanReviewValidationResult:
    decision = lookup_approval(approval_id, repo_root)
    if decision is None:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            requested_action=requested_action,
            requested_effect=requested_effect,
            status=VALIDATION_MISSING,
            reason=f"Approval {approval_id} not found",
            allowed=False,
        )
    if decision.decision != "APPROVED":
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            approval_decision_id=approval_id,
            request_id=decision.request_id,
            requested_action=requested_action,
            requested_effect=requested_effect,
            status=VALIDATION_INVALID,
            reason=f"Decision is {decision.decision}, not APPROVED",
            allowed=False,
        )
    expiry_check = check_expiry(approval_id, repo_root)
    if expiry_check.expired:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            approval_decision_id=approval_id,
            request_id=decision.request_id,
            requested_action=requested_action,
            requested_effect=requested_effect,
            status="EXPIRED",
            reason="Approval has expired",
            expired=True,
            allowed=False,
        )
    revoke_check = is_revoked(approval_id, repo_root)
    if revoke_check:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            approval_decision_id=approval_id,
            request_id=decision.request_id,
            requested_action=requested_action,
            requested_effect=requested_effect,
            status="REVOKED",
            reason="Approval has been revoked",
            revoked=True,
            allowed=False,
        )
    if scope and not _scope_matches(decision, scope):
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            approval_decision_id=approval_id,
            request_id=decision.request_id,
            requested_action=requested_action,
            requested_effect=requested_effect,
            status=VALIDATION_OUT_OF_SCOPE,
            reason="Scope mismatch",
            matched_scope=False,
            allowed=False,
        )
    _log_validation(approval_id, decision.request_id, "VALID", repo_root)
    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        approval_decision_id=approval_id,
        request_id=decision.request_id,
        requested_action=requested_action,
        requested_effect=requested_effect,
        status=VALIDATION_VALID,
        matched_scope=True,
        allowed=True,
    )


def _scope_matches(decision: HumanApprovalDecision, scope: HumanApprovalScope) -> bool:
    ds = decision.scope
    if ds is None:
        return True
    if ds.action_id and scope.action_id and ds.action_id != scope.action_id:
        return False
    if ds.session_id and scope.session_id and ds.session_id != scope.session_id:
        return False
    if ds.tool_call_id and scope.tool_call_id and ds.tool_call_id != scope.tool_call_id:
        return False
    if ds.patch_session_id and scope.patch_session_id and ds.patch_session_id != scope.patch_session_id:
        return False
    if ds.file_paths and scope.file_paths:
        if not any(p in ds.file_paths for p in scope.file_paths):
            return False
    if ds.allowed_effects and scope.allowed_effects:
        if not any(e in ds.allowed_effects for e in scope.allowed_effects):
            return False
    return True


def _log_validation(approval_id: str, request_id: str, status: str, repo_root: Path) -> None:
    entry = {
        "validation_id": new_id("val"),
        "approval_decision_id": approval_id,
        "request_id": request_id,
        "status": status,
        "validated_at": utc_now_iso(),
    }
    append_jsonl(human_review_runs_dir(repo_root) / "approval_validation_history.jsonl", entry)
