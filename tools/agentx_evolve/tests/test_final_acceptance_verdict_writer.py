from pathlib import Path

from agentx_evolve.final_acceptance.verdict_writer import (
    build_verdict_record, write_verdict_record,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceEvidenceManifest, FinalAcceptanceEvidenceItem,
    FinalAcceptanceArtifactHash,
    VERDICT_ACCEPTED, VERDICT_NOT_ACCEPTED,
    STATUS_PASS, STATUS_FAIL,
)
from agentx_evolve.final_acceptance.artifact_writer import runtime_root


class TestBuildVerdictRecord:
    def test_minimal(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None,
            reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
        )
        assert record["final_verdict"] == VERDICT_ACCEPTED
        assert record["go_criteria_status"] == "PASS"
        assert record["no_go_criteria_status"] == "PASS"

    def test_not_accepted(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0,
            blockers=["Blocker"],
            accepted_deviations=[],
            non_blocking_followups=[],
        )
        assert record["final_verdict"] == VERDICT_NOT_ACCEPTED
        assert record["go_criteria_status"] == "FAIL"
        assert record["no_go_criteria_status"] == "FAIL"

    def test_with_all_optional_params(self):
        items = [FinalAcceptanceEvidenceItem(layer_id="L1")]
        manifest = FinalAcceptanceEvidenceManifest(items=items)
        hashes = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="ff")]
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit="abc123",
            reviewed_branch="main",
            acceptance_mode="PRODUCTION_ACCEPTANCE",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.9,
            blockers=["b1"],
            accepted_deviations=[{"id": "D001"}],
            non_blocking_followups=["n1"],
            evidence_manifest=manifest,
            artifact_hashes=hashes,
            layer_statuses={"L1": STATUS_PASS},
            validation_status="PASS",
            schema_validation_status="PASS",
            release_readiness_status="RELEASE_READY",
        )
        assert record["reviewed_commit"] == "abc123"
        assert record["acceptance_score"] == 0.9
        assert record["blockers"] == ["b1"]
        assert record["accepted_deviations"] == [{"id": "D001"}]
        assert record["layer_matrix_status"] == "PASS"
        assert record["validation_status"] == "PASS"
        assert record["schema_validation_status"] == "PASS"
        assert record["release_readiness_status"] == "RELEASE_READY"

    def test_with_blockers(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0,
            blockers=["Blocker 1", "Blocker 2"],
            accepted_deviations=[],
            non_blocking_followups=["Followup"],
        )
        assert len(record["blockers"]) == 2
        assert len(record["non_blocking_followups"]) == 1

    def test_accepted_deviations(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[{"deviation_id": "D001", "area": "security"}],
            non_blocking_followups=[],
        )
        assert len(record["accepted_deviations"]) == 1

    def test_layer_statuses_all_pass(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
            layer_statuses={"L1": STATUS_PASS},
        )
        assert record["layer_matrix_status"] == "PASS"

    def test_layer_statuses_all_fail(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
            layer_statuses={"L1": STATUS_FAIL},
        )
        assert record["layer_matrix_status"] == "FAIL"

    def test_layer_statuses_mixed(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.5,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
            layer_statuses={"L1": STATUS_PASS, "L2": STATUS_FAIL},
        )
        assert record["layer_matrix_status"] == "FAIL"

    def test_safety_freeze_default(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
        )
        assert record["safety_freeze_status"] == "PASS"

    def test_empty_layers(self):
        record = build_verdict_record(
            repo_root=Path("/tmp"),
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
            layer_statuses={},
        )
        assert record["layer_matrix_status"] == "PASS"


class TestWriteVerdictRecord:
    def test_writes_file(self, tmp_path: Path):
        record = build_verdict_record(
            repo_root=tmp_path,
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
        )
        path = write_verdict_record(record, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_verdict.json"

    def test_writes_to_runtime_root(self, tmp_path: Path):
        record = build_verdict_record(
            repo_root=tmp_path,
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
        )
        path = write_verdict_record(record, tmp_path)
        assert runtime_root(tmp_path) in path.parents

    def test_written_json_valid(self, tmp_path: Path):
        record = build_verdict_record(
            repo_root=tmp_path,
            reviewed_commit=None, reviewed_branch=None,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            blockers=[],
            accepted_deviations=[],
            non_blocking_followups=[],
        )
        write_verdict_record(record, tmp_path)
        import json
        path = runtime_root(tmp_path) / "final_acceptance_verdict.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["final_verdict"] == VERDICT_ACCEPTED
