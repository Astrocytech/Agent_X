import json
import pytest
from pathlib import Path

from agentx_evolve.final_acceptance.cross_layer_checker import (
    run_cross_layer_checks, write_cross_layer_matrix,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceLayerRegistry, FinalAcceptanceEvidenceManifest,
    FinalAcceptanceLayer, CrossLayerCheck,
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
    STATUS_PASS, STATUS_FAIL, STATUS_NOT_APPLICABLE,
    SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING,
)


def _reg_for_mode(mode: str) -> FinalAcceptanceLayerRegistry:
    return FinalAcceptanceLayerRegistry(
        created_at="t", acceptance_mode=mode,
        layers=[
            FinalAcceptanceLayer(
                layer_id=layer_id,
                acceptance_modes_required=mode_reqs,
                deferral_modes_allowed=def_modes,
            )
            for layer_id, mode_reqs, def_modes in [
                ("L0_SEED_KERNEL", [mode], []),
                ("SECURITY_SANDBOX", [mode] if mode in (MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE, MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE) else [], []),
                ("POLICY_CAPABILITY_REGISTRY", [mode], []),
                ("FAILURE_TAXONOMY", [mode], []),
                ("TOOL_MCP_ADAPTER", [mode], []),
                ("GOVERNED_PATCH_EXECUTION", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("MODEL_ADAPTER", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("PROMPT_CONTRACT_VERSIONING", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("LLM_IMPLEMENTATION_WORKER", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("SELF_EVOLUTION_ORCHESTRATOR", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("HUMAN_REVIEW_APPROVAL", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("PROMOTION_RELEASE_GATE", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("GIT_INTEGRATION", [MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE]),
                ("EVALUATION_HARNESS", [mode], []),
                ("PACKAGING_DISTRIBUTION", [MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE, MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE]),
                ("BACKUP_DISASTER_RECOVERY", [MODE_RELEASE_ACCEPTANCE], [MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE, MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE]),
                ("FINAL_SYSTEM_ACCEPTANCE", [mode], []),
            ]
        ],
    )


class TestRunCrossLayerChecks:
    def test_returns_15_checks(self, tmp_path: Path):
        reg = _reg_for_mode(MODE_IMPLEMENTATION_ACCEPTANCE)
        manifest = FinalAcceptanceEvidenceManifest(created_at="t")
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_IMPLEMENTATION_ACCEPTANCE)
        assert len(checks) == 15

    def test_cl015_always_pass(self, tmp_path: Path):
        reg = _reg_for_mode(MODE_IMPLEMENTATION_ACCEPTANCE)
        manifest = FinalAcceptanceEvidenceManifest(created_at="t")
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_IMPLEMENTATION_ACCEPTANCE)
        cl015 = [c for c in checks if c.check_id == "CL-015"]
        assert len(cl015) == 1
        assert cl015[0].status == STATUS_PASS

    def test_cl001_through_cl015_ids_present(self, tmp_path: Path):
        reg = _reg_for_mode(MODE_RELEASE_ACCEPTANCE)
        manifest = FinalAcceptanceEvidenceManifest(created_at="t")
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_RELEASE_ACCEPTANCE)
        check_ids = [c.check_id for c in checks]
        expected = [f"CL-{i:03d}" for i in range(1, 16)]
        for eid in expected:
            assert eid in check_ids

    def test_implementation_mode_passes_when_active(self, tmp_path: Path):
        reg = _reg_for_mode(MODE_IMPLEMENTATION_ACCEPTANCE)
        manifest = FinalAcceptanceEvidenceManifest(created_at="t")
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_IMPLEMENTATION_ACCEPTANCE)
        for c in checks:
            if c.check_id == "CL-015":
                continue
            assert c.status in (STATUS_PASS, STATUS_NOT_APPLICABLE)

    def test_source_only_has_not_applicable_for_gov_patch(self, tmp_path: Path):
        reg = _reg_for_mode(MODE_SOURCE_ONLY_ACCEPTANCE)
        manifest = FinalAcceptanceEvidenceManifest(created_at="t")
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_SOURCE_ONLY_ACCEPTANCE)
        cl004 = next(c for c in checks if c.check_id == "CL-004")
        assert cl004.status == STATUS_NOT_APPLICABLE

    def test_all_severities_used(self, tmp_path: Path):
        reg = _reg_for_mode(MODE_RELEASE_ACCEPTANCE)
        manifest = FinalAcceptanceEvidenceManifest(created_at="t")
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_RELEASE_ACCEPTANCE)
        severities = {c.severity for c in checks}
        assert SEVERITY_BLOCKER in severities
        assert SEVERITY_HIGH in severities
        assert SEVERITY_NON_BLOCKING in severities

    def test_each_check_has_requirement(self, tmp_path: Path):
        reg = _reg_for_mode(MODE_IMPLEMENTATION_ACCEPTANCE)
        manifest = FinalAcceptanceEvidenceManifest(created_at="t")
        checks = run_cross_layer_checks(tmp_path, reg, manifest, MODE_IMPLEMENTATION_ACCEPTANCE)
        for c in checks:
            assert c.requirement, f"{c.check_id} has empty requirement"
            assert c.source_layer, f"{c.check_id} has no source"
            assert c.target_layer, f"{c.check_id} has no target"


class TestWriteCrossLayerMatrix:
    def test_writes_file(self, tmp_path: Path):
        checks = [
            CrossLayerCheck(
                check_id="CL-001", source_layer="A", target_layer="B",
                requirement="req", status=STATUS_PASS, severity=SEVERITY_NON_BLOCKING,
            )
        ]
        path = write_cross_layer_matrix(checks, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_cross_layer_matrix.json"

    def test_content_structure(self, tmp_path: Path):
        checks = [
            CrossLayerCheck(
                check_id="CL-001", source_layer="A", target_layer="B",
                requirement="test dependency", status=STATUS_PASS,
                severity=SEVERITY_BLOCKER, reason="all good",
            )
        ]
        path = write_cross_layer_matrix(checks, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_id"] == "final_acceptance_cross_layer_check.schema.json"
        assert len(data["checks"]) == 1
        check = data["checks"][0]
        assert check["check_id"] == "CL-001"
        assert check["severity"] == SEVERITY_BLOCKER

    def test_empty_checks(self, tmp_path: Path):
        path = write_cross_layer_matrix([], tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["checks"] == []
