import hashlib
import json
from pathlib import Path

from .scheduler_models import (
    sha256_file, sha256_bytes, canonical_json,
)


def compute_file_hash(path: str | Path) -> str:
    return sha256_file(Path(path))


def compute_state_hash(state: dict) -> str:
    return sha256_bytes(canonical_json(state))


def compute_evidence_hash(evidence: dict) -> str:
    excluded = {"evidence_manifest_sha256", "review_report_sha256", "completion_record_sha256", "hash"}
    data = {k: v for k, v in evidence.items() if k not in excluded}
    return sha256_bytes(canonical_json(data))


def verify_file_hash(path: str | Path, expected_hash: str) -> bool:
    if not Path(path).exists():
        return False
    actual = compute_file_hash(path)
    return actual == expected_hash


def hash_scheduler_artifact(
    artifact_path: str | Path,
    repo_root: str | Path,
) -> dict:
    full_path = Path(repo_root) / artifact_path
    if not full_path.exists():
        return {"path": str(artifact_path), "exists": False, "hash": ""}
    h = compute_file_hash(full_path)
    return {
        "path": str(artifact_path),
        "exists": True,
        "hash": h,
        "algorithm": "sha256",
    }
