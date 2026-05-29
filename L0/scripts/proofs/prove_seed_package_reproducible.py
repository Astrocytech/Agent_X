"""Prove seed package reproducibility — build artifact is deterministic."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "L0/manifests/SEED_PACKAGE_MANIFEST.yaml"
HASH_PATH = ROOT / ".local" / "runtime" / "seed_package_hash.txt"
BUILD_SCRIPT = ROOT / "L0/scripts/build_seed_package.py"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def flatten_manifest_files(manifest: dict) -> set[str]:
    files: set[str] = set()
    for value in manifest.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    files.add(item)
    return files


def compute_hash(manifest: dict) -> str:
    hasher = hashlib.sha256()
    for rel in sorted(flatten_manifest_files(manifest)):
        path = ROOT / rel
        if path.exists():
            hasher.update(path.read_bytes())
        else:
            hasher.update(rel.encode())
    return hasher.hexdigest()


def main() -> int:
    errors: list[str] = []

    if not MANIFEST_PATH.exists():
        errors.append(f"manifest not found: {MANIFEST_PATH}")
        print("SEED PACKAGE REPRODUCIBILITY PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    manifest = load_yaml(MANIFEST_PATH)
    manifest_files = flatten_manifest_files(manifest)

    for rel in manifest_files:
        if not (ROOT / rel).exists():
            errors.append(f"manifest file missing: {rel}")

    if not BUILD_SCRIPT.exists():
        errors.append(f"build script not found: {BUILD_SCRIPT}")

    if errors:
        print("SEED PACKAGE REPRODUCIBILITY PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    # Compute and write hash
    HASH_PATH.parent.mkdir(parents=True, exist_ok=True)
    h1 = compute_hash(manifest)
    HASH_PATH.write_text(h1 + "\n")

    # Verify determinism: compute twice
    h2 = compute_hash(manifest)
    if h1 != h2:
        errors.append(f"non-deterministic hash: {h1} != {h2}")
        print("SEED PACKAGE REPRODUCIBILITY PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    print("SEED PACKAGE REPRODUCIBILITY PROOF: OK")
    print(f"- manifest files: {len(manifest_files)}")
    print(f"- hash: {h1}")
    print(f"- hash path: {HASH_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
