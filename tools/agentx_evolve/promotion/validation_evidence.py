from __future__ import annotations
from pathlib import Path
from agentx_evolve.models.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    ValidationEvidence, ReleaseCandidate, canonical_json, sha256_dict,
    sha256_file, from_dict, to_dict, write_json_atomic,
    CS_NOT_RUN, CS_PASS, CS_FAIL,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


def load_validation_evidence(path: Path) -> ValidationEvidence:
    import json
    data = json.loads(path.read_text())
    return from_dict(ValidationEvidence, data)


def validate_validation_evidence(
    evidence: ValidationEvidence,
    candidate: ReleaseCandidate,
    freshness_minutes: int,
) -> list[str]:
    errors: list[str] = []
    if evidence.schema_id != "promotion_validation_evidence.schema.json":
        errors.append(f"schema_id mismatch: {evidence.schema_id}")
    if evidence.validated_commit != candidate.source_commit:
        errors.append(
            f"validated_commit {evidence.validated_commit} != "
            f"candidate source_commit {candidate.source_commit}"
        )
    if not evidence.evidence_hash:
        errors.append("evidence_hash is empty")
    if not isinstance(evidence.evidence_files, list):
        errors.append("evidence_files must be a list")
    if evidence.compileall_status != CS_NOT_RUN and evidence.compileall_exit_code is None:
        errors.append("compileall_exit_code is None when compileall_status != NOT_RUN")
    if evidence.pytest_status != CS_NOT_RUN and evidence.pytest_exit_code is None:
        errors.append("pytest_exit_code is None when pytest_status != NOT_RUN")
    if evidence.schema_validation_status != CS_NOT_RUN and evidence.schema_validation_exit_code is None:
        errors.append("schema_validation_exit_code is None when schema_validation_status != NOT_RUN")
    for cmd in evidence.commands:
        if "exit_code" not in cmd:
            errors.append(f"command {cmd.get('name', 'unknown')} missing exit_code")
    return errors


def verify_command_passed(evidence: ValidationEvidence, command_name: str) -> bool:
    for cmd in evidence.commands:
        if cmd.get("name") == command_name:
            return cmd.get("exit_code") == 0
    return False


def verify_evidence_hashes(evidence: ValidationEvidence, repo_root: Path) -> list[str]:
    mismatches: list[str] = []
    for entry in evidence.evidence_hashes:
        path_str = entry.get("path", "")
        expected_hash = entry.get("sha256", "")
        if not path_str or not expected_hash:
            mismatches.append(f"incomplete hash entry: {entry}")
            continue
        full_path = repo_root / path_str
        if not full_path.exists():
            mismatches.append(f"evidence file not found: {path_str}")
            continue
        actual_hash = sha256_file(full_path)
        if actual_hash != expected_hash:
            mismatches.append(
                f"hash mismatch for {path_str}: expected {expected_hash}, got {actual_hash}"
            )
    return mismatches


def write_validation_evidence(evidence: ValidationEvidence, repo_root: Path) -> Path:
    path = promotion_runs_dir(repo_root) / "validation_evidence.json"
    return write_json_atomic(path, to_dict(evidence))


def compute_validation_evidence_hash(evidence: ValidationEvidence) -> str:
    payload: dict = {
        "component_id": evidence.component_id,
        "validated_commit": evidence.validated_commit,
        "compileall_status": evidence.compileall_status,
        "compileall_exit_code": evidence.compileall_exit_code,
        "pytest_status": evidence.pytest_status,
        "pytest_exit_code": evidence.pytest_exit_code,
        "schema_validation_status": evidence.schema_validation_status,
        "schema_validation_exit_code": evidence.schema_validation_exit_code,
        "commands": sorted(
            [canonical_json(cmd) for cmd in evidence.commands]
        ) if evidence.commands else [],
        "evidence_files": sorted(evidence.evidence_files) if evidence.evidence_files else [],
    }
    return sha256_dict(payload)
