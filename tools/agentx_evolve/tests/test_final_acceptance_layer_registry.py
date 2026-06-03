import json
import pytest
from pathlib import Path

from agentx_evolve.final_acceptance.layer_registry import (
    build_final_acceptance_layer_registry, get_layer_by_id,
    list_required_layers, list_safely_deferred_layers, write_layer_registry,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
    FinalAcceptanceLayer,
)


class TestBuildFinalAcceptanceLayerRegistry:
    def test_defaults(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        assert reg.reviewed_commit is None
        assert reg.reviewed_branch is None
        assert reg.acceptance_mode == MODE_SOURCE_ONLY_ACCEPTANCE
        assert reg.bootstrap_self is False
        assert len(reg.layers) == 26

    def test_with_commit_and_branch(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, reviewed_commit="abc123", reviewed_branch="main",
        )
        assert reg.reviewed_commit == "abc123"
        assert reg.reviewed_branch == "main"

    def test_implementation_mode(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        assert reg.acceptance_mode == MODE_IMPLEMENTATION_ACCEPTANCE

    def test_bootstrap_true(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, bootstrap_self=True,
        )
        assert reg.bootstrap_self is True

    def test_contains_all_modes(self, tmp_path: Path):
        for mode in [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ]:
            reg = build_final_acceptance_layer_registry(tmp_path, acceptance_mode=mode)
            assert reg.acceptance_mode == mode

    def test_created_at_timestamp(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        assert reg.created_at
        assert "T" in reg.created_at


class TestGetLayerById:
    def test_found(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        layer = get_layer_by_id(reg, "FINAL_SYSTEM_ACCEPTANCE")
        assert layer is not None
        assert layer.layer_id == "FINAL_SYSTEM_ACCEPTANCE"
        assert layer.layer_name == "Final System Acceptance"

    def test_seed_kernel(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        layer = get_layer_by_id(reg, "L0_SEED_KERNEL")
        assert layer is not None
        assert layer.roadmap_number == 0

    def test_not_found(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        layer = get_layer_by_id(reg, "NONEXISTENT_LAYER")
        assert layer is None

    def test_empty_string(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        layer = get_layer_by_id(reg, "")
        assert layer is None


class TestListRequiredLayers:
    def test_implementation_mode(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        required = list_required_layers(reg)
        ids = [l.layer_id for l in required]
        assert "FINAL_SYSTEM_ACCEPTANCE" in ids
        assert "L0_SEED_KERNEL" in ids
        assert "PACKAGING_DISTRIBUTION" not in ids

    def test_release_mode(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_RELEASE_ACCEPTANCE,
        )
        required = list_required_layers(reg)
        ids = [l.layer_id for l in required]
        assert "PACKAGING_DISTRIBUTION" in ids
        assert "BACKUP_DISASTER_RECOVERY" in ids


class TestListSafelyDeferredLayers:
    def test_implementation_mode(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        deferred = list_safely_deferred_layers(reg)
        ids = [l.layer_id for l in deferred]
        assert "PACKAGING_DISTRIBUTION" in ids
        assert "MONITORING_OBSERVABILITY" in ids
        assert "FINAL_SYSTEM_ACCEPTANCE" not in ids

    def test_release_mode_has_fewer_deferrals(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_RELEASE_ACCEPTANCE,
        )
        deferred = list_safely_deferred_layers(reg)
        ids = [l.layer_id for l in deferred]
        assert "PACKAGING_DISTRIBUTION" not in ids
        assert "MONITORING_OBSERVABILITY" not in ids

    def test_source_only_has_many_deferrals(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, acceptance_mode=MODE_SOURCE_ONLY_ACCEPTANCE,
        )
        deferred = list_safely_deferred_layers(reg)
        ids = [l.layer_id for l in deferred]
        assert "GOVERNED_PATCH_EXECUTION" in ids
        assert "MODEL_ADAPTER" in ids


class TestWriteLayerRegistry:
    def test_writes_file(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        path = write_layer_registry(reg, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_layer_registry.json"

    def test_content(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(
            tmp_path, reviewed_commit="abc", acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        path = write_layer_registry(reg, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_id"] == "final_acceptance_layer_registry.schema.json"
        assert data["reviewed_commit"] == "abc"
        assert data["acceptance_mode"] == MODE_IMPLEMENTATION_ACCEPTANCE
        assert len(data["layers"]) == 26

    def test_each_layer_has_required_fields(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        path = write_layer_registry(reg, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        for layer in data["layers"]:
            assert "layer_id" in layer
            assert "layer_name" in layer
            assert "roadmap_number" in layer

    def test_writes_to_runtime_root(self, tmp_path: Path):
        reg = build_final_acceptance_layer_registry(tmp_path)
        path = write_layer_registry(reg, tmp_path)
        expected = tmp_path / ".agentx-init" / "final_acceptance" / "final_acceptance_layer_registry.json"
        assert path.resolve() == expected.resolve()
