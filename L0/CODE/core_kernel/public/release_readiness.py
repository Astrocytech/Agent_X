"""Release readiness reporting for the governed seed kernel."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReleaseReadiness:
    status: str
    proof_artifact_found: bool
    proof_artifact_path: str
    seed_package_hash_found: bool
    seed_package_hash_path: str


def get_release_readiness(root: Path | None = None) -> ReleaseReadiness:
    if root is None:
        root = Path(__file__).resolve().parents[3]

    proof_path = root / ".local" / "runtime" / "seed_proof.json"
    hash_path = root / ".local" / "runtime" / "seed_package_hash.txt"

    proof_found = proof_path.exists()
    hash_found = hash_path.exists()

    if proof_found and hash_found:
        status = "ready"
    elif proof_found:
        status = "proof_only"
    else:
        status = "unknown_without_make_prove"

    return ReleaseReadiness(
        status=status,
        proof_artifact_found=proof_found,
        proof_artifact_path=str(proof_path),
        seed_package_hash_found=hash_found,
        seed_package_hash_path=str(hash_path),
    )
