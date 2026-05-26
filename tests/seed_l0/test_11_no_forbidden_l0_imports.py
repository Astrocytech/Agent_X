"""Test 11: Forbidden imports — L0 code must not import forbidden top-level modules."""

from __future__ import annotations

import yaml
from pathlib import Path
from scripts.proofs.validate_seed_manifests import validate_seed_import_boundary

ROOT = Path(__file__).resolve().parents[2]


def test_l0_seed_import_boundary_is_clean() -> None:
    manifest = yaml.safe_load((ROOT / "SEED_PACKAGE_MANIFEST.yaml").read_text())
    validate_seed_import_boundary(manifest)
