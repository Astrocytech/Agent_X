from __future__ import annotations
from pathlib import Path
from agentx_evolve.models.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, canonical_json, sha256_dict, from_dict, to_dict,
    write_json_atomic,
)


def promotion_runs_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "promotion"


def create_release_candidate(
    component_id: str,
    component_name: str,
    roadmap_layer: str | int,
    source_commit: str,
    changed_files: list[str],
    changed_schemas: list[str],
    changed_tests: list[str],
    required_validations: list[str],
    required_approvals: list[str],
    required_evidence: list[str],
    repo_root: Path,
    **kwargs,
) -> ReleaseCandidate:
    candidate = ReleaseCandidate(
        candidate_id=new_id("rc-"),
        created_at=utc_now_iso(),
        component_id=component_id,
        component_name=component_name,
        roadmap_layer=roadmap_layer,
        source_commit=source_commit,
        changed_files=changed_files,
        changed_schemas=changed_schemas,
        changed_tests=changed_tests,
        required_validations=required_validations,
        required_approvals=required_approvals,
        required_evidence=required_evidence,
    )
    for k, v in kwargs.items():
        if hasattr(candidate, k):
            setattr(candidate, k, v)
    candidate.candidate_hash = compute_candidate_hash(candidate)
    return candidate


def load_release_candidate(path: Path) -> ReleaseCandidate:
    import json
    data = json.loads(path.read_text())
    return from_dict(ReleaseCandidate, data)


def validate_release_candidate(candidate: ReleaseCandidate) -> list[str]:
    errors: list[str] = []
    if candidate.schema_id != "promotion_release_candidate.schema.json":
        errors.append(f"schema_id mismatch: {candidate.schema_id}")
    if not candidate.source_commit:
        errors.append("source_commit is empty")
    if not candidate.candidate_id:
        errors.append("candidate_id is empty")
    if not candidate.candidate_hash:
        errors.append("candidate_hash is empty")
    if not isinstance(candidate.changed_files, list):
        errors.append("changed_files must be a list")
    if not isinstance(candidate.warnings, list):
        errors.append("warnings must be a list")
    if not isinstance(candidate.errors, list):
        errors.append("errors must be a list")
    return errors


def write_release_candidate(candidate: ReleaseCandidate, repo_root: Path) -> Path:
    path = promotion_runs_dir(repo_root) / "release_candidate.json"
    return write_json_atomic(path, to_dict(candidate))


def compute_candidate_hash(candidate: ReleaseCandidate) -> str:
    payload: dict = {
        "component_id": candidate.component_id,
        "source_commit": candidate.source_commit,
        "changed_files": sorted(candidate.changed_files),
        "changed_schemas": sorted(candidate.changed_schemas),
        "changed_tests": sorted(candidate.changed_tests),
        "required_validations": sorted(candidate.required_validations),
        "required_approvals": sorted(candidate.required_approvals),
        "required_evidence": sorted(candidate.required_evidence),
        "risk_ids": sorted(candidate.risk_ids),
    }
    if candidate.supersedes_candidate_id:
        payload["supersedes_candidate_id"] = candidate.supersedes_candidate_id
    if candidate.release_scope:
        payload["release_scope"] = sorted(candidate.release_scope)
    return sha256_dict(payload)
