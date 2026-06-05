from __future__ import annotations
from pathlib import Path
from agentx_evolve.model.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    GitEvidence, ReleaseCandidate, canonical_json, sha256_dict,
    from_dict, to_dict, write_json_atomic,
    WT_CLEAN, WT_DIRTY, WT_EXPECTED_RUNTIME_ARTIFACTS_ONLY, WT_UNKNOWN,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


def load_git_evidence(path: Path) -> GitEvidence | None:
    if not path.exists():
        return None
    import json
    data = json.loads(path.read_text())
    return from_dict(GitEvidence, data)


def validate_git_evidence(
    git_evidence: GitEvidence,
    candidate: ReleaseCandidate,
) -> list[str]:
    errors: list[str] = []
    if git_evidence.schema_id != "promotion_git_evidence.schema.json":
        errors.append(f"schema_id mismatch: {git_evidence.schema_id}")
    if not git_evidence.git_evidence_hash:
        errors.append("git_evidence_hash is empty")
    if git_evidence.source_commit != candidate.source_commit:
        errors.append(
            f"source_commit mismatch: {git_evidence.source_commit} != "
            f"{candidate.source_commit}"
        )
    if git_evidence.candidate_id != candidate.candidate_id:
        errors.append(
            f"candidate_id mismatch: {git_evidence.candidate_id} != "
            f"{candidate.candidate_id}"
        )
    return errors


def verify_git_state_allows_promotion(
    git_evidence: GitEvidence,
    candidate: ReleaseCandidate,
    policy_context: dict,
) -> list[str]:
    errors: list[str] = []
    require_clean = policy_context.get("require_clean_git_state", True)
    if require_clean:
        if git_evidence.working_tree_status == WT_DIRTY:
            errors.append("Git working tree is dirty")
        elif git_evidence.working_tree_status == WT_UNKNOWN:
            errors.append("Git working tree status unknown")
        elif git_evidence.working_tree_status == WT_EXPECTED_RUNTIME_ARTIFACTS_ONLY:
            allowed = policy_context.get("allow_expected_runtime_artifacts_only", True)
            if not allowed:
                errors.append("Expected runtime artifacts only not allowed by policy")
    if not git_evidence.commit_reachable:
        errors.append(f"Source commit {git_evidence.source_commit} is not reachable")
    if git_evidence.forbidden_git_actions_detected:
        errors.append(
            f"Forbidden git actions detected: {git_evidence.forbidden_git_actions_detected}"
        )
    if candidate.changed_files:
        ev_changed = set(git_evidence.changed_files)
        cand_changed = set(candidate.changed_files)
        if ev_changed != cand_changed:
            errors.append(
                f"Changed files mismatch: evidence has {len(ev_changed)}, "
                f"candidate has {len(cand_changed)}"
            )
    return errors


def write_git_evidence(git_evidence: GitEvidence, repo_root: Path) -> Path:
    path = promotion_runs_dir(repo_root) / "git_evidence.json"
    return write_json_atomic(path, to_dict(git_evidence))


def compute_git_evidence_hash(git_evidence: GitEvidence) -> str:
    payload: dict = {
        "component_id": git_evidence.component_id,
        "candidate_id": git_evidence.candidate_id,
        "source_commit": git_evidence.source_commit,
        "source_branch": git_evidence.source_branch,
        "working_tree_status": git_evidence.working_tree_status,
        "commit_reachable": git_evidence.commit_reachable,
        "changed_files": sorted(git_evidence.changed_files) if git_evidence.changed_files else [],
        "forbidden_git_actions_detected": sorted(
            git_evidence.forbidden_git_actions_detected
        ) if git_evidence.forbidden_git_actions_detected else [],
    }
    return sha256_dict(payload)
