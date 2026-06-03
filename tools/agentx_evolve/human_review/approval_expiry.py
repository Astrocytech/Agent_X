from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from agentx_evolve.human_review.review_models import (
    new_id, utc_now_iso, append_jsonl, human_review_runs_dir,
)


def check_expiry(approval_id: str, repo_root: Path) -> "ExpiryResult":
    import json
    path = human_review_runs_dir(repo_root) / "approval_decision_history.jsonl"
    if not path.exists():
        return ExpiryResult(approval_id=approval_id, expired=True, reason="No history")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("decision_id") == approval_id:
                expires_at = data.get("expires_at")
                if not expires_at:
                    return ExpiryResult(approval_id=approval_id, expired=False)
                try:
                    expiry_dt = datetime.fromisoformat(expires_at)
                    if expiry_dt.tzinfo is None:
                        expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    if now >= expiry_dt:
                        _record_expiry(approval_id, repo_root)
                        return ExpiryResult(approval_id=approval_id, expired=True, reason="Past expiry", expired_at=expires_at)
                    return ExpiryResult(approval_id=approval_id, expired=False)
                except ValueError:
                    return ExpiryResult(approval_id=approval_id, expired=True, reason="Invalid expiry date")
    return ExpiryResult(approval_id=approval_id, expired=True, reason="Not found")


def _record_expiry(approval_id: str, repo_root: Path) -> None:
    entry = {
        "expiry_id": new_id("exp"),
        "approval_decision_id": approval_id,
        "expired_at": utc_now_iso(),
        "expired": True,
    }
    append_jsonl(human_review_runs_dir(repo_root) / "approval_expiry_history.jsonl", entry)


def is_approval_expired(
    decision: HumanApprovalDecision,
    now_iso: str | None = None,
) -> bool:
    if not decision.expires_at:
        return False
    try:
        expiry_dt = datetime.fromisoformat(decision.expires_at)
        if expiry_dt.tzinfo is None:
            expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
        if now_iso:
            now = datetime.fromisoformat(now_iso)
            if now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
        else:
            now = datetime.now(timezone.utc)
        return now >= expiry_dt
    except ValueError:
        return True


def mark_expired_approvals(
    repo_root: Path,
    now_iso: str | None = None,
) -> list[HumanReviewValidationResult]:
    from agentx_evolve.human_review.review_models import HumanReviewValidationResult
    import json
    results = []
    path = human_review_runs_dir(repo_root) / "approval_decision_history.jsonl"
    if not path.exists():
        return results
    seen = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            decision_id = data.get("decision_id", "")
            if decision_id in seen:
                continue
            seen.add(decision_id)
            if is_approval_expired(data, now_iso):
                _record_expiry(decision_id, repo_root)
                results.append(HumanReviewValidationResult(
                    validation_id=new_id("val"),
                    validated_at=now_iso or utc_now_iso(),
                    approval_decision_id=decision_id,
                    request_id=data.get("request_id", ""),
                    requested_action=data.get("requested_action", ""),
                    requested_effect=data.get("requested_effect", ""),
                    status="EXPIRED",
                    reason="Approval has expired",
                    expired=True,
                    allowed=False,
                ))
    return results


class ExpiryResult:
    def __init__(self, approval_id: str = "", expired: bool = False, reason: str = "", expired_at: str = ""):
        self.approval_id = approval_id
        self.expired = expired
        self.reason = reason
        self.expired_at = expired_at
