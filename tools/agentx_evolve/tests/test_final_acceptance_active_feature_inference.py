from pathlib import Path

from agentx_evolve.final_acceptance.active_feature_inference import (
    is_feature_active, infer_active_features,
)
from agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceLayer


class TestIsFeatureActive:
    def test_unknown_layer_id_returns_true(self, tmp_path: Path):
        assert is_feature_active(tmp_path, "NONEXISTENT_LAYER") is True

    def test_active_when_module_exists(self, tmp_path: Path):
        module_dir = tmp_path / "tools" / "agentx_evolve"
        module_dir.mkdir(parents=True)
        (module_dir / "patch_execution.py").touch()
        assert is_feature_active(tmp_path, "GOVERNED_PATCH_EXECUTION") is True

    def test_inactive_when_module_missing(self, tmp_path: Path):
        assert is_feature_active(tmp_path, "GOVERNED_PATCH_EXECUTION") is False

    def test_active_when_subdir_exists(self, tmp_path: Path):
        subdir = tmp_path / "tools" / "agentx_evolve" / "patch"
        subdir.mkdir(parents=True)
        assert is_feature_active(tmp_path, "GOVERNED_PATCH_EXECUTION") is True

    def test_active_via_root_subdir(self, tmp_path: Path):
        subdir = tmp_path / "tools" / "patch"
        subdir.mkdir(parents=True)
        assert is_feature_active(tmp_path, "GOVERNED_PATCH_EXECUTION") is True

    def test_active_via_top_level_subdir(self, tmp_path: Path):
        subdir = tmp_path / "patch"
        subdir.mkdir(parents=True)
        assert is_feature_active(tmp_path, "GOVERNED_PATCH_EXECUTION") is True

    def test_module_py_file_check(self, tmp_path: Path):
        module_dir = tmp_path / "tools" / "agentx_evolve"
        module_dir.mkdir(parents=True)
        (module_dir / "model_adapter.py").touch()
        assert is_feature_active(tmp_path, "MODEL_ADAPTER") is True

    def test_module_dir_check(self, tmp_path: Path):
        module_dir = tmp_path / "tools" / "agentx_evolve" / "self_evolution_orchestrator"
        module_dir.mkdir(parents=True)
        (module_dir / "__init__.py").touch()
        assert is_feature_active(tmp_path, "SELF_EVOLUTION_ORCHESTRATOR") is True


class TestInferActiveFeatures:
    def test_no_layers(self, tmp_path: Path):
        result = infer_active_features(tmp_path, [])
        assert result == {}

    def test_required_layers_not_included(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(
            layer_id="TEST_LAYER", required_for_acceptance=True,
        )
        result = infer_active_features(tmp_path, [layer])
        assert result == {}

    def test_non_required_inactive_layer(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(
            layer_id="GOVERNED_PATCH_EXECUTION", required_for_acceptance=False,
        )
        result = infer_active_features(tmp_path, [layer])
        assert result.get("GOVERNED_PATCH_EXECUTION") is False

    def test_non_required_active_layer(self, tmp_path: Path):
        module_dir = tmp_path / "tools" / "agentx_evolve"
        module_dir.mkdir(parents=True)
        (module_dir / "patch_execution.py").touch()
        layer = FinalAcceptanceLayer(
            layer_id="GOVERNED_PATCH_EXECUTION", required_for_acceptance=False,
        )
        result = infer_active_features(tmp_path, [layer])
        assert result.get("GOVERNED_PATCH_EXECUTION") is True

    def test_mixed_required_and_non_required(self, tmp_path: Path):
        module_dir = tmp_path / "tools" / "agentx_evolve"
        module_dir.mkdir(parents=True)
        (module_dir / "patch_execution.py").touch()
        layers = [
            FinalAcceptanceLayer(layer_id="REQUIRED_ONE", required_for_acceptance=True),
            FinalAcceptanceLayer(layer_id="GOVERNED_PATCH_EXECUTION", required_for_acceptance=False),
            FinalAcceptanceLayer(layer_id="MODEL_ADAPTER", required_for_acceptance=False),
        ]
        result = infer_active_features(tmp_path, layers)
        assert "REQUIRED_ONE" not in result
        assert result.get("GOVERNED_PATCH_EXECUTION") is True
        assert result.get("MODEL_ADAPTER") is False
