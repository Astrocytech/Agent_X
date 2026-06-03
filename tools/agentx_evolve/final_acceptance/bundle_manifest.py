import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceArtifactHash
from .artifact_writer import write_json_artifact


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def compute_hash_of_hashes(artifact_hashes: list[FinalAcceptanceArtifactHash]) -> str:
    sorted_hashes = sorted(artifact_hashes, key=lambda h: h.artifact_path)
    combined = "".join(h.sha256 for h in sorted_hashes)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def build_final_acceptance_bundle(
    repo_root: Path,
    reviewed_commit: str | None,
    artifact_hashes: list[FinalAcceptanceArtifactHash],
    layer_evidence_hashes: dict[str, str] | None = None,
    command_output_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    hash_of_hashes = compute_hash_of_hashes(artifact_hashes)
    return {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_bundle.schema.json",
        "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "reviewed_commit": reviewed_commit,
        "created_at": _make_timestamp(),
        "included_artifacts": [
            h.artifact_path for h in sorted(artifact_hashes, key=lambda x: x.artifact_path)
        ],
        "artifact_hashes": {
            h.artifact_path: h.sha256
            for h in sorted(artifact_hashes, key=lambda x: x.artifact_path)
        },
        "layer_evidence_hashes": layer_evidence_hashes or {},
        "command_output_hashes": command_output_hashes or {},
        "hash_of_hashes": hash_of_hashes,
        "bundle_status": "FINALIZED",
        "warnings": [],
        "errors": [],
    }


def write_bundle_manifest(data: dict[str, Any], repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_bundle.json", data)
