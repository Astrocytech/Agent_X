import pytest
from pathlib import Path
from agentx_evolve.model_runtime.runtime_models import (
    LocalHardwareProfile, LocalModelAvailabilityDecision,
    LocalRuntimeCompatibilityDecision, LocalModelEligibilityDecision,
    LocalModelInventory,
)
from agentx_evolve.model_runtime.runtime_artifacts import (
    calculate_sha256, write_profile_snapshot, write_inventory_snapshot,
    write_hardware_snapshot, append_runtime_compatibility,
    append_model_availability, append_model_eligibility,
    write_latest_runtime_compatibility, write_latest_model_availability,
    write_latest_model_eligibility, write_evidence_manifest,
    write_review_report, write_runtime_artifact, write_completion_record,
    RUNTIME_ROOT,
)


def test_calculate_sha256_existing_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    h = calculate_sha256(f)
    assert isinstance(h, str)
    assert len(h) == 64


def test_calculate_sha256_missing_file():
    h = calculate_sha256(Path("/tmp/nonexistent_file_xyz"))
    assert h == ""


def test_write_profile_snapshot(tmp_path):
    repo = {"key": "value"}
    result = write_profile_snapshot(repo, tmp_path)
    assert "path" in result
    assert "sha256" in result
    assert result["sha256"] != ""


def test_write_inventory_snapshot(tmp_path):
    inv = LocalModelInventory(inventory_id="inv1")
    result = write_inventory_snapshot(inv, tmp_path)
    assert result["path"].endswith("model_inventory_snapshot.json")
    assert result["sha256"] != ""


def test_write_hardware_snapshot(tmp_path):
    hw = LocalHardwareProfile(hardware_profile_id="hw1")
    result = write_hardware_snapshot(hw, tmp_path)
    assert result["path"].endswith("hardware_profile_snapshot.json")


def test_append_runtime_compatibility(tmp_path):
    decision = LocalRuntimeCompatibilityDecision(decision_id="dc1")
    result = append_runtime_compatibility(decision, tmp_path)
    assert "path" in result


def test_append_model_availability(tmp_path):
    decision = LocalModelAvailabilityDecision(decision_id="da1")
    result = append_model_availability(decision, tmp_path)
    assert "path" in result


def test_append_model_eligibility(tmp_path):
    decision = LocalModelEligibilityDecision(decision_id="de1")
    result = append_model_eligibility(decision, tmp_path)
    assert "path" in result


def test_write_latest_runtime_compatibility(tmp_path):
    decision = LocalRuntimeCompatibilityDecision(decision_id="dc1")
    result = write_latest_runtime_compatibility(decision, tmp_path)
    assert "sha256" in result


def test_write_latest_model_availability(tmp_path):
    decision = LocalModelAvailabilityDecision(decision_id="da1")
    result = write_latest_model_availability(decision, tmp_path)
    assert "sha256" in result


def test_write_latest_model_eligibility(tmp_path):
    decision = LocalModelEligibilityDecision(decision_id="de1")
    result = write_latest_model_eligibility(decision, tmp_path)
    assert "sha256" in result


def test_write_evidence_manifest(tmp_path):
    manifest = {"key": "value"}
    result = write_evidence_manifest(manifest, tmp_path)
    assert "sha256" in result


def test_write_review_report(tmp_path):
    report = {"report": "data"}
    result = write_review_report(report, tmp_path)
    assert "sha256" in result


def test_write_runtime_artifact(tmp_path):
    data = {"artifact": "data"}
    result = write_runtime_artifact("custom_artifact.json", data, tmp_path)
    assert "custom_artifact.json" in result["path"]
    assert result["sha256"] != ""


def test_write_completion_record(tmp_path):
    record = {"status": "done"}
    result = write_completion_record(record, tmp_path)
    assert "sha256" in result
