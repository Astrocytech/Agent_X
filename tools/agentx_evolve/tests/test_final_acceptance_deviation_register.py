import json
import pytest
from pathlib import Path

from tools.agentx_evolve.final_acceptance.deviation_register import (
    load_deviation_register, validate_deviation_register, write_deviation_register,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceDeviation,
)


class TestLoadDeviationRegister:
    def test_no_file_returns_empty(self, tmp_path: Path):
        devs = load_deviation_register(tmp_path)
        assert devs == []

    def test_loads_existing_file(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        data = {
            "deviations": [
                {"deviation_id": "D001", "area": "test", "layer_id": "L1",
                 "description": "desc", "reason": "reason"},
            ]
        }
        (runtime / "final_acceptance_deviation_register.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        devs = load_deviation_register(tmp_path)
        assert len(devs) == 1
        assert devs[0].deviation_id == "D001"

    def test_corrupt_json_returns_empty(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        (runtime / "final_acceptance_deviation_register.json").write_text(
            "not json", encoding="utf-8"
        )
        devs = load_deviation_register(tmp_path)
        assert devs == []

    def test_empty_deviations_list(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        data = {"deviations": []}
        (runtime / "final_acceptance_deviation_register.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        devs = load_deviation_register(tmp_path)
        assert devs == []

    def test_loads_multiple_deviations(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        data = {
            "deviations": [
                {"deviation_id": "D001", "area": "a", "layer_id": "L1",
                 "description": "d1", "reason": "r1"},
                {"deviation_id": "D002", "area": "b", "layer_id": "L2",
                 "description": "d2", "reason": "r2"},
            ]
        }
        (runtime / "final_acceptance_deviation_register.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        devs = load_deviation_register(tmp_path)
        assert len(devs) == 2


class TestValidateDeviationRegister:
    def test_empty_list(self):
        errors = validate_deviation_register([])
        assert errors == []

    def test_no_safety_impact(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="test", layer_id="L1",
                description="desc", reason="reason", safety_impact="none",
            )
        ]
        errors = validate_deviation_register(devs)
        assert errors == []

    def test_critical_safety_impact(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="test", layer_id="L1",
                description="desc", reason="reason", safety_impact="critical",
            )
        ]
        errors = validate_deviation_register(devs)
        assert len(errors) == 1
        assert "D001" in errors[0]
        assert "critical" in errors[0]

    def test_high_safety_with_accepted_status(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D002", area="test", layer_id="L1",
                description="desc", reason="reason",
                safety_impact="high", accepted_status="NOT_APPLICABLE",
            )
        ]
        errors = validate_deviation_register(devs)
        assert errors == []

    def test_high_safety_without_accepted_status(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D003", area="test", layer_id="L1",
                description="desc", reason="reason",
                safety_impact="high", accepted_status="ACCEPTED",
            )
        ]
        errors = validate_deviation_register(devs)
        assert len(errors) == 1

    def test_mixed_validity(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="a", layer_id="L1",
                description="d1", reason="r1", safety_impact="critical",
            ),
            FinalAcceptanceDeviation(
                deviation_id="D002", area="b", layer_id="L2",
                description="d2", reason="r2", safety_impact="none",
            ),
        ]
        errors = validate_deviation_register(devs)
        assert len(errors) == 1
        assert "D001" in errors[0]

    def test_low_impact_passes(self):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D004", area="test", layer_id="L1",
                description="desc", reason="reason", safety_impact="low",
            )
        ]
        errors = validate_deviation_register(devs)
        assert errors == []


class TestWriteDeviationRegister:
    def test_writes_file(self, tmp_path: Path):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="test", layer_id="L1",
                description="desc", reason="reason",
            )
        ]
        path = write_deviation_register(devs, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_deviation_register.json"

    def test_content(self, tmp_path: Path):
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001", area="test", layer_id="L1",
                description="desc", reason="reason", safety_impact="high",
                compensating_control="manual review",
                accepted_status="DEFERRED_SAFELY", reviewer_decision="approved",
                evidence_refs=["ref1"],
            )
        ]
        path = write_deviation_register(devs, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_id"] == "final_acceptance_deviation.schema.json"
        assert len(data["deviations"]) == 1
        assert data["deviations"][0]["deviation_id"] == "D001"
        assert data["deviations"][0]["compensating_control"] == "manual review"

    def test_empty_list(self, tmp_path: Path):
        path = write_deviation_register([], tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["deviations"] == []

    def test_writes_to_runtime_root(self, tmp_path: Path):
        devs = [FinalAcceptanceDeviation(
            deviation_id="D001", area="a", layer_id="L1",
            description="d", reason="r",
        )]
        path = write_deviation_register(devs, tmp_path)
        expected = tmp_path / ".agentx-init" / "final_acceptance" / "final_acceptance_deviation_register.json"
        assert path.resolve() == expected.resolve()
