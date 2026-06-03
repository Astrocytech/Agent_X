from __future__ import annotations

from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    ArtifactHashManifest,
    ArtifactHashRecord,
    new_id,
    sha256_file,
    sha256_bytes,
    utc_now_iso,
    to_dict,
    write_json_atomic,
)


def hash_artifact(path: Path) -> ArtifactHashRecord:
    sha256 = sha256_file(path)
    size_bytes = path.stat().st_size
    kind = _infer_artifact_kind(path)
    return ArtifactHashRecord(
        artifact_path=str(path),
        artifact_kind=kind,
        sha256=sha256,
        size_bytes=size_bytes,
        created_at=utc_now_iso(),
    )


def write_hash_manifest(artifacts: list[Path], output_path: Path) -> ArtifactHashManifest:
    records = [hash_artifact(p) for p in artifacts]
    manifest = ArtifactHashManifest(
        hash_manifest_id=new_id("hash"),
        created_at=utc_now_iso(),
        artifacts=records,
    )
    write_json_atomic(output_path, to_dict(manifest))
    return manifest


def verify_artifact_hash(path: Path, expected_sha256: str) -> bool:
    return sha256_file(path) == expected_sha256


def hash_bytes(data: bytes) -> str:
    return sha256_bytes(data)


def _infer_artifact_kind(path: Path) -> str:
    name = path.name
    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        return "tar.gz"
    if name.endswith(".zip"):
        return "zip"
    if name.endswith(".whl"):
        return "wheel"
    if name.endswith(".tar"):
        return "tar"
    if path.is_dir():
        return "directory"
    ext = path.suffix.lstrip(".") or "unknown"
    return ext
