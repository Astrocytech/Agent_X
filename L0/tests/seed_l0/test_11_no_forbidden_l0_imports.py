"""Test 11: Forbidden imports — L0 code must not import forbidden top-level modules."""

from __future__ import annotations

import yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]

import sys
sys.path.insert(0, str(ROOT / "L0/scripts"))
from proofs.validate_seed_manifests import validate_seed_import_boundary  # type: ignore[import-untyped]


def test_l0_seed_import_boundary_is_clean() -> None:
    manifest = yaml.safe_load((ROOT / "L0/manifests/SEED_PACKAGE_MANIFEST.yaml").read_text())
    validate_seed_import_boundary(manifest)
