import hashlib
import json
from pathlib import Path

from .acceptance_models import FinalAcceptanceArtifactHash
from .artifact_writer import write_json_artifact


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(65536)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_artifacts(
    paths: list[Path], exclude_self_hash_file: Path | None = None
) -> list[FinalAcceptanceArtifactHash]:
    hashes: list[FinalAcceptanceArtifactHash] = []
    for p in sorted(set(str(p) for p in paths)):
        path = Path(p)
        if exclude_self_hash_file and path.resolve() == exclude_self_hash_file.resolve():
            continue
        if not path.exists():
            continue
        hashes.append(
            FinalAcceptanceArtifactHash(
                artifact_path=str(path),
                sha256=sha256_file(path),
            )
        )
    return hashes


def write_artifact_hashes(
    hashes: list[FinalAcceptanceArtifactHash],
    repo_root: Path,
    self_hash_mode: str = "EXCLUDED_FROM_SELF_HASH",
) -> Path:
    data = {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_artifact_hash.schema.json",
        "source_component": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "self_hash_mode": self_hash_mode,
        "self_hash_reason": "EXCLUDED_TO_AVOID_CYCLIC_HASH",
        "hashed_artifacts": [
            {"artifact_path": h.artifact_path, "sha256": h.sha256}
            for h in hashes
        ],
        "unhashed_artifacts": [
            {
                "artifact_path": "final_acceptance_artifact_hashes.json",
                "reason": "EXCLUDED_TO_AVOID_CYCLIC_HASH",
            }
        ],
        "warnings": [],
        "errors": [],
    }
    return write_json_artifact(repo_root, "final_acceptance_artifact_hashes.json", data)


def validate_acyclic_hash_manifest(repo_root: Path) -> list[str]:
    errors: list[str] = []
    hash_file = repo_root / ".agentx-init" / "final_acceptance" / "final_acceptance_artifact_hashes.json"
    if not hash_file.exists():
        errors.append("Hash manifest does not exist")
        return errors

    try:
        data = json.loads(hash_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"Cannot read hash manifest: {e}")
        return errors

    if data.get("self_hash_mode") != "EXCLUDED_FROM_SELF_HASH":
        errors.append(
            f"self_hash_mode is {data.get('self_hash_mode')}, expected EXCLUDED_FROM_SELF_HASH"
        )

    hashed_paths = {h["artifact_path"] for h in data.get("hashed_artifacts", [])}
    for artifact_name in [
        "final_acceptance_report.json",
        "final_acceptance_completion_record.json",
        "latest_final_acceptance_result.json",
    ]:
        artifact_path = str(
            (repo_root / ".agentx-init" / "final_acceptance" / artifact_name).resolve()
        )
        if artifact_path in hashed_paths:
            try:
                art_data = json.loads(
                    Path(artifact_path).read_text(encoding="utf-8")
                )
                embedded_sha = art_data.get("artifact_hashes_sha256")
                if embedded_sha and embedded_sha != "null" and embedded_sha is not None:
                    errors.append(
                        f"{artifact_name} embeds artifact_hashes_sha256={embedded_sha} "
                        f"while being hashed by the manifest"
                    )
            except (json.JSONDecodeError, OSError):
                pass

    return errors
