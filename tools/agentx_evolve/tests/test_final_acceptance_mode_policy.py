import pytest

from agentx_evolve.final_acceptance.mode_policy import (
    build_mode_policy, is_layer_required_for_mode,
    is_deferral_allowed_for_mode, validate_acceptance_mode,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
)


class TestBuildModePolicy:
    def test_implementation_mode(self):
        policy = build_mode_policy(MODE_IMPLEMENTATION_ACCEPTANCE)
        assert policy["acceptance_mode"] == MODE_IMPLEMENTATION_ACCEPTANCE
        assert "FINAL_SYSTEM_ACCEPTANCE" in policy["required_layers"]
        assert "L0_SEED_KERNEL" in policy["required_layers"]
        assert "GOVERNED_PATCH_EXECUTION" not in policy["required_layers"]
        assert policy["deferral_allowed_layers"] == []

    def test_source_only_mode(self):
        policy = build_mode_policy(MODE_SOURCE_ONLY_ACCEPTANCE)
        assert policy["acceptance_mode"] == MODE_SOURCE_ONLY_ACCEPTANCE
        assert "GOVERNED_PATCH_EXECUTION" in policy["deferral_allowed_layers"]
        assert "PACKAGING_DISTRIBUTION" in policy["deferral_allowed_layers"]

    def test_non_production_mode(self):
        policy = build_mode_policy(MODE_NON_PRODUCTION_ACCEPTANCE)
        assert "MODEL_ADAPTER" in policy["required_layers"]
        assert "LLM_IMPLEMENTATION_WORKER" in policy["required_layers"]
        assert "BACKUP_DISASTER_RECOVERY" in policy["deferral_allowed_layers"]
        assert "PACKAGING_DISTRIBUTION" not in policy["required_layers"]

    def test_production_mode(self):
        policy = build_mode_policy(MODE_PRODUCTION_ACCEPTANCE)
        assert "MONITORING_OBSERVABILITY" in policy["required_layers"]
        assert "BACKUP_DISASTER_RECOVERY" in policy["required_layers"]
        assert "PACKAGING_DISTRIBUTION" not in policy["required_layers"]
        assert "TASK_QUEUE_SESSION_SCHEDULER" in policy["deferral_allowed_layers"]

    def test_release_mode(self):
        policy = build_mode_policy(MODE_RELEASE_ACCEPTANCE)
        assert "PACKAGING_DISTRIBUTION" in policy["required_layers"]
        assert "BACKUP_DISASTER_RECOVERY" in policy["required_layers"]
        assert "FINAL_SYSTEM_ACCEPTANCE" in policy["required_layers"]

    def test_schema_fields(self):
        policy = build_mode_policy(MODE_IMPLEMENTATION_ACCEPTANCE)
        assert policy["schema_version"] == "1.0"
        assert policy["schema_id"] == "final_acceptance_mode_policy.schema.json"
        assert "source_component" in policy

    def test_unknown_mode(self):
        policy = build_mode_policy("UNKNOWN")
        assert policy["required_layers"] == []
        assert policy["deferral_allowed_layers"] == []


class TestIsLayerRequiredForMode:
    def test_seed_kernel_required_all_modes(self):
        for mode in ALL_MODES_LIST:
            assert is_layer_required_for_mode("L0_SEED_KERNEL", mode)

    def test_final_system_acceptance_required_all_modes(self):
        for mode in ALL_MODES_LIST:
            assert is_layer_required_for_mode("FINAL_SYSTEM_ACCEPTANCE", mode)

    def test_packaging_only_release(self):
        assert is_layer_required_for_mode("PACKAGING_DISTRIBUTION", MODE_RELEASE_ACCEPTANCE)
        assert not is_layer_required_for_mode("PACKAGING_DISTRIBUTION", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert not is_layer_required_for_mode("PACKAGING_DISTRIBUTION", MODE_SOURCE_ONLY_ACCEPTANCE)
        assert not is_layer_required_for_mode("PACKAGING_DISTRIBUTION", MODE_NON_PRODUCTION_ACCEPTANCE)
        assert not is_layer_required_for_mode("PACKAGING_DISTRIBUTION", MODE_PRODUCTION_ACCEPTANCE)

    def test_monitoring_observability(self):
        assert is_layer_required_for_mode("MONITORING_OBSERVABILITY", MODE_PRODUCTION_ACCEPTANCE)
        assert is_layer_required_for_mode("MONITORING_OBSERVABILITY", MODE_RELEASE_ACCEPTANCE)
        assert not is_layer_required_for_mode("MONITORING_OBSERVABILITY", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert not is_layer_required_for_mode("MONITORING_OBSERVABILITY", MODE_SOURCE_ONLY_ACCEPTANCE)

    def test_model_adapter_not_required_impl_source(self):
        assert not is_layer_required_for_mode("MODEL_ADAPTER", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert not is_layer_required_for_mode("MODEL_ADAPTER", MODE_SOURCE_ONLY_ACCEPTANCE)

    def test_model_adapter_required_nonprod_prod_release(self):
        assert is_layer_required_for_mode("MODEL_ADAPTER", MODE_NON_PRODUCTION_ACCEPTANCE)
        assert is_layer_required_for_mode("MODEL_ADAPTER", MODE_PRODUCTION_ACCEPTANCE)
        assert is_layer_required_for_mode("MODEL_ADAPTER", MODE_RELEASE_ACCEPTANCE)

    def test_unknown_layer(self):
        assert not is_layer_required_for_mode("NONEXISTENT_LAYER", MODE_IMPLEMENTATION_ACCEPTANCE)


class TestIsDeferralAllowedForMode:
    def test_seed_kernel_not_deferrable(self):
        for mode in ALL_MODES_LIST:
            assert not is_deferral_allowed_for_mode("L0_SEED_KERNEL", mode)

    def test_governed_patch_deferrable_impl_source(self):
        assert is_deferral_allowed_for_mode("GOVERNED_PATCH_EXECUTION", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert is_deferral_allowed_for_mode("GOVERNED_PATCH_EXECUTION", MODE_SOURCE_ONLY_ACCEPTANCE)

    def test_governed_patch_not_deferrable_nonprod_prod_release(self):
        assert not is_deferral_allowed_for_mode("GOVERNED_PATCH_EXECUTION", MODE_NON_PRODUCTION_ACCEPTANCE)
        assert not is_deferral_allowed_for_mode("GOVERNED_PATCH_EXECUTION", MODE_PRODUCTION_ACCEPTANCE)
        assert not is_deferral_allowed_for_mode("GOVERNED_PATCH_EXECUTION", MODE_RELEASE_ACCEPTANCE)

    def test_task_queue_deferrable_all_modes(self):
        for mode in ALL_MODES_LIST:
            assert is_deferral_allowed_for_mode("TASK_QUEUE_SESSION_SCHEDULER", mode)

    def test_long_term_learning_deferrable_all_modes(self):
        for mode in ALL_MODES_LIST:
            assert is_deferral_allowed_for_mode("LONG_TERM_LEARNING", mode)

    def test_unknown_layer_deferrable(self):
        assert is_deferral_allowed_for_mode("NONEXISTENT", MODE_IMPLEMENTATION_ACCEPTANCE)

    def test_packaging_deferrable_except_release(self):
        assert is_deferral_allowed_for_mode("PACKAGING_DISTRIBUTION", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert is_deferral_allowed_for_mode("PACKAGING_DISTRIBUTION", MODE_SOURCE_ONLY_ACCEPTANCE)
        assert is_deferral_allowed_for_mode("PACKAGING_DISTRIBUTION", MODE_NON_PRODUCTION_ACCEPTANCE)
        assert is_deferral_allowed_for_mode("PACKAGING_DISTRIBUTION", MODE_PRODUCTION_ACCEPTANCE)
        assert not is_deferral_allowed_for_mode("PACKAGING_DISTRIBUTION", MODE_RELEASE_ACCEPTANCE)

    def test_monitoring_observability_deferral_pattern(self):
        assert is_deferral_allowed_for_mode("MONITORING_OBSERVABILITY", MODE_IMPLEMENTATION_ACCEPTANCE)
        assert is_deferral_allowed_for_mode("MONITORING_OBSERVABILITY", MODE_SOURCE_ONLY_ACCEPTANCE)
        assert is_deferral_allowed_for_mode("MONITORING_OBSERVABILITY", MODE_NON_PRODUCTION_ACCEPTANCE)
        assert not is_deferral_allowed_for_mode("MONITORING_OBSERVABILITY", MODE_PRODUCTION_ACCEPTANCE)
        assert not is_deferral_allowed_for_mode("MONITORING_OBSERVABILITY", MODE_RELEASE_ACCEPTANCE)


class TestValidateAcceptanceMode:
    def test_all_valid_modes(self):
        for mode in ALL_MODES_LIST:
            assert validate_acceptance_mode(mode) == []

    def test_invalid_mode(self):
        errors = validate_acceptance_mode("INVALID_MODE")
        assert len(errors) == 1
        assert "INVALID_MODE" in errors[0]

    def test_empty_string(self):
        errors = validate_acceptance_mode("")
        assert len(errors) == 1

    def test_none(self):
        errors = validate_acceptance_mode(None)
        assert len(errors) == 1

    def test_lowercase_valid_mode(self):
        errors = validate_acceptance_mode("implementation_acceptance")
        assert len(errors) == 1


ALL_MODES_LIST = [
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
]
