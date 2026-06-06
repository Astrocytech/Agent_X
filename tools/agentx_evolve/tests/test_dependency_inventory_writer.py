from pathlib import Path

import pytest

from agentx_evolve.packaging.dependency_inventory_writer import write_dependency_inventory
from agentx_evolve.packaging.packaging_models import (
    PackageManifest, DependencyLockReport,
    VALIDATION_STATUS_PASS,
)


class TestInventoryWrittenWithoutNetwork:
    def test_inventory_written_without_network(self, tmp_path: Path):
        manifest = PackageManifest()
        dlr = DependencyLockReport()
        output = tmp_path / "dep_inventory.json"
        inv = write_dependency_inventory(tmp_path, manifest, dlr, output)
        assert inv.network_resolution_used is False
        assert output.exists()

    def test_inventory_records_dependency_files(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("[project]\ndependencies = []\n")
        manifest = PackageManifest()
        dlr = DependencyLockReport()
        output = tmp_path / "dep_inventory.json"
        inv = write_dependency_inventory(tmp_path, manifest, dlr, output)
        assert len(inv.dependency_files) > 0
        assert any("pyproject.toml" in f for f in inv.dependency_files)

    def test_inventory_records_unpinned(self, tmp_path: Path):
        (tmp_path / "requirements.txt").write_text("requests\n")
        manifest = PackageManifest()
        dlr = DependencyLockReport(unpinned_dependencies=["requests"])
        output = tmp_path / "dep_inventory.json"
        inv = write_dependency_inventory(tmp_path, manifest, dlr, output)
        assert "requests" in inv.unpinned_dependencies

    def test_inventory_empty_repo(self, tmp_path: Path):
        manifest = PackageManifest()
        dlr = DependencyLockReport()
        output = tmp_path / "dep_inventory.json"
        inv = write_dependency_inventory(tmp_path, manifest, dlr, output)
        assert inv.status == VALIDATION_STATUS_PASS
        assert inv.inventory_id.startswith("dii_")
