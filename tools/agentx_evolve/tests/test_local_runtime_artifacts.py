import pytest
import json
from pathlib import Path
from agentx_evolve.model_runtime.runtime_artifacts import (
    write_profile_snapshot, write_inventory_snapshot, write_hardware_snapshot,
    calculate_sha256,
)
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelInventory, LocalHardwareProfile,
)

RUNTIME_ROOT = Path(".agentx-init") / "model_runtime"


def test_runtime_artifacts_written_under_runtime_root(tmp_path):
    repo = {"repository_id": "test", "approved_model_roots": []}
    result = write_profile_snapshot(repo, tmp_path)
    assert "sha256" in result
    assert (tmp_path / RUNTIME_ROOT / "model_runtime_profile_snapshot.json").exists()


def test_inventory_snapshot(tmp_path):
    inv = LocalModelInventory(inventory_id="inv-test", created_at="now")
    result = write_inventory_snapshot(inv, tmp_path)
    assert "sha256" in result


def test_hardware_snapshot(tmp_path):
    hw = LocalHardwareProfile(hardware_profile_id="hw1", probe_mode="STATIC_ONLY")
    result = write_hardware_snapshot(hw, tmp_path)
    assert "sha256" in result


def test_calculate_sha256(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    h = calculate_sha256(f)
    assert len(h) == 64
