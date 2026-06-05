from __future__ import annotations
from pathlib import Path
from agentx_evolve.model.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    ApprovalReference, ReleaseCandidate, canonical_json, sha256_dict,
    from_dict, to_dict, append_jsonl,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


def load_approval_references(path: Path) -> list[ApprovalReference]:
    if not path.exists():
        return []
    import json
    approvals: list[ApprovalReference] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            approvals.append(from_dict(ApprovalReference, data))
    return approvals


def find_required_approvals(
    candidate: ReleaseCandidate,
    approvals: list[ApprovalReference],
) -> dict:
    result: dict = {
        "matched": [],
        "missing": [],
        "expired": [],
        "revoked": [],
        "mismatched_commit": [],
        "mismatched_candidate": [],
    }
    required = set(candidate.required_approvals)
    for approval in approvals:
        if approval.approval_type in required or not required:
            if approval.revoked:
                result["revoked"].append(approval.approval_id)
            elif approval.expires_at and _is_past(approval.expires_at):
                result["expired"].append(approval.approval_id)
            elif approval.approved_commit and approval.approved_commit != candidate.source_commit:
                result["mismatched_commit"].append(approval.approval_id)
            elif approval.candidate_id and approval.candidate_id != candidate.candidate_id:
                result["mismatched_candidate"].append(approval.approval_id)
            else:
                result["matched"].append(approval.approval_id)
    for req in required:
        found = any(a for a in approvals if a.approval_id == req)
        if not found:
            result["missing"].append(req)
    return result


def _is_past(iso_str: str) -> bool:
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= dt
    except ValueError:
        return True


def validate_approval_reference(
    approval: ApprovalReference,
    candidate: ReleaseCandidate,
) -> list[str]:
    errors: list[str] = []
    if approval.schema_id != "promotion_approval_reference.schema.json":
        errors.append(f"schema_id mismatch: {approval.schema_id}")
    if not approval.approval_hash:
        errors.append("approval_hash is empty")
    if approval.revoked:
        errors.append(f"approval {approval.approval_id} is revoked")
    if approval.approved_commit and approval.approved_commit != candidate.source_commit:
        errors.append(
            f"approved_commit {approval.approved_commit} != "
            f"candidate source_commit {candidate.source_commit}"
        )
    if approval.candidate_id and approval.candidate_id != candidate.candidate_id:
        errors.append(
            f"candidate_id {approval.candidate_id} != "
            f"candidate candidate_id {candidate.candidate_id}"
        )
    return errors


def validate_required_approvals(
    candidate: ReleaseCandidate,
    approvals: list[ApprovalReference],
) -> list[str]:
    errors: list[str] = []
    required_set = set(candidate.required_approvals)
    if not required_set:
        return errors
    found_ids = {a.approval_id for a in approvals}
    for req in required_set:
        if req not in found_ids:
            errors.append(f"required approval {req} not found")
    for approval in approvals:
        errors.extend(validate_approval_reference(approval, candidate))
    return errors


def compute_approval_references_hash(approvals: list[ApprovalReference]) -> str:
    payloads = []
    for a in approvals:
        p = {
            "approval_id": a.approval_id,
            "approved_by": a.approved_by,
            "approval_type": a.approval_type,
            "component_id": a.component_id,
            "candidate_id": a.candidate_id,
            "approved_commit": a.approved_commit,
            "scope": sorted(a.scope) if a.scope else [],
            "revoked": a.revoked,
        }
        payloads.append(p)
    return sha256_dict({"approvals": sorted([canonical_json(p) for p in payloads])})
