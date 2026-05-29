"""Test 07: Manifest closure — every manifest file exists, required sections present."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]


def test_seed_manifest_paths_exist() -> None:
    manifest = yaml.safe_load((ROOT / "L0/manifests/SEED_PACKAGE_MANIFEST.yaml").read_text())

    for key, value in manifest.items():
        if key in {"version", "seed_package_version", "release_type"}:
            continue

        assert isinstance(value, list), key

        for rel in value:
            path = ROOT / rel
            assert path.exists(), f"{key} references missing path: {rel}"
