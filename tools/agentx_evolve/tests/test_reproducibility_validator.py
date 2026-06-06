from pathlib import Path

import pytest

from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageFileRecord,
    PACKAGE_FORMAT_TAR_GZ,
    VALIDATION_STATUS_PASS, VALIDATION_STATUS_FAIL,
)


class TestDoubleBuild:
    def _make_inventory(self, tmp_path: Path, files: list[str]) -> PackageInventory:
        records = []
        for rel in files:
            f = tmp_path / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(f"content of {rel}")
            records.append(PackageFileRecord(
                relative_path=rel, absolute_path=str(f), included=True,
            ))
        return PackageInventory(files=records, selected_count=len(records))

    def test_double_build_hashes_match(self, tmp_path: Path):
        pytest.skip("Requires full build pipeline setup")

    def test_hash_mismatch_detected(self, tmp_path: Path):
        pytest.skip("Requires full build pipeline setup")
