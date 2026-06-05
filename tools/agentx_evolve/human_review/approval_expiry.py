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


class ExpiryResult:
    def __init__(self, approval_id: str = "", expired: bool = False, reason: str = "", expired_at: str = ""):
        self.approval_id = approval_id
        self.expired = expired
        self.reason = reason
        self.expired_at = expired_at
