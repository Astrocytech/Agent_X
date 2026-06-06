from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    ArtifactHashManifest,
    PackageProvenance,
    ReleaseBundleManifest,
    new_id,
    sha256_file,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def _dir_sha256(directory: Path) -> str:
    hasher = hashlib.sha256()
    for fpath in sorted(directory.rglob("*")):
        if fpath.is_file():
            rel = str(fpath.relative_to(directory))
            file_hash = sha256_file(fpath)
            hasher.update(f"{rel}:{file_hash}\n".encode("utf-8"))
    return hasher.hexdigest()


def create_release_bundle(
    package_artifact: Path,
    evidence_files: list[Path],
    hash_manifest: ArtifactHashManifest,
    provenance: PackageProvenance,
    output_root: Path,
) -> ReleaseBundleManifest:
    bundle_name = f"release_bundle_{provenance.package_name}_{provenance.package_version}"
    bundle_dir = output_root / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=True)

    artifacts_dir = bundle_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    included_artifacts: list[str] = []
    included_hashes: list[dict] = []

    artifact_dest = artifacts_dir / package_artifact.name
    shutil.copy2(package_artifact, artifact_dest)
    included_artifacts.append(str(artifact_dest.resolve()))
    included_hashes.append({
        "path": str(artifact_dest.resolve()),
        "sha256": sha256_file(artifact_dest),
    })

    evidence_dir_path = bundle_dir / "evidence"
    evidence_dir_path.mkdir(parents=True, exist_ok=True)

    for ev_path in evidence_files:
        if ev_path.exists():
            dest = evidence_dir_path / ev_path.name
            shutil.copy2(ev_path, dest)

    included_artifacts.append(str(evidence_dir_path.resolve()))

    bundle_sha256 = _dir_sha256(bundle_dir)

    manifest = ReleaseBundleManifest(
        bundle_manifest_id=new_id("bundle"),
        created_at=utc_now_iso(),
        bundle_name=bundle_name,
        bundle_version=provenance.package_version,
        bundle_artifact=str(bundle_dir.resolve()),
        bundle_sha256=bundle_sha256,
        included_artifacts=included_artifacts,
        included_hashes=included_hashes,
        provenance_ref=str(bundle_dir.resolve()),
        evidence_ref=str(evidence_dir_path.resolve()),
        promotion_status="NOT_PROMOTED",
    )

    manifest_path = bundle_dir / "release_bundle_manifest.json"
    write_json_atomic(manifest_path, to_dict(manifest))

    return manifest
