from __future__ import annotations
from pathlib import Path
import json
from agentx_evolve.human_review.review_models import (
    HumanApprovalRevocation, HumanReviewerIdentity,
    new_id, utc_now_iso, sha256_dict, canonical_hash_payload,
    atomic_write_json, append_jsonl, human_review_runs_dir,
    SOURCE_COMPONENT,
)


def revoke_approval(
    approval_decision_id: str,
    revoked_by: HumanReviewerIdentity,
    reason: str,
    repo_root: Path,
) -> HumanApprovalRevocation:
    now = utc_now_iso()
    revocation = HumanApprovalRevocation(
        revocation_id=new_id("hrev"),
        approval_decision_id=approval_decision_id,
        revoked_at=now,
        revoked_by=revoked_by,
        reason=reason,
    )
    payload = canonical_hash_payload(revocation.to_dict())
    revocation.revocation_hash = sha256_dict(payload)
    append_jsonl(human_review_runs_dir(repo_root) / "revocation_history.jsonl", revocation.to_dict())
    return revocation


def is_revoked(approval_decision_id: str, repo_root: Path) -> bool:
    path = human_review_runs_dir(repo_root) / "revocation_history.jsonl"
    if not path.exists():
        return False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("approval_decision_id") == approval_decision_id:
                return True
    return False
