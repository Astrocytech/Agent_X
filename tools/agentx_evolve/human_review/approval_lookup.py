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


def _decision_from_dict(data: dict) -> HumanApprovalDecision:
    return HumanApprovalDecision(
        decision_id=data.get("decision_id", ""),
        request_id=data.get("request_id", ""),
        decided_at=data.get("decided_at", ""),
        decision=data.get("decision", "APPROVED"),
        reason=data.get("reason", ""),
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
