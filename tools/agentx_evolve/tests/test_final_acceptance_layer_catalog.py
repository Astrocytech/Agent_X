import pytest

from tools.agentx_evolve.final_acceptance.layer_catalog import (
    build_canonical_layer_catalog, validate_layer_catalog,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceLayer,
)


class TestBuildCanonicalLayerCatalog:
    def test_has_26_layers(self):
        catalog = build_canonical_layer_catalog()
        assert len(catalog) == 26

    def test_contains_final_system_acceptance(self):
        catalog = build_canonical_layer_catalog()
        ids = [l.layer_id for l in catalog]
        assert "FINAL_SYSTEM_ACCEPTANCE" in ids

    def test_contains_l0_seed_kernel(self):
        catalog = build_canonical_layer_catalog()
        ids = [l.layer_id for l in catalog]
        assert "L0_SEED_KERNEL" in ids

    def test_contains_packaging_distribution(self):
        catalog = build_canonical_layer_catalog()
        ids = [l.layer_id for l in catalog]
        assert "PACKAGING_DISTRIBUTION" in ids

    def test_contains_backup_disaster_recovery(self):
        catalog = build_canonical_layer_catalog()
        ids = [l.layer_id for l in catalog]
        assert "BACKUP_DISASTER_RECOVERY" in ids

    def test_all_have_unique_ids(self):
        catalog = build_canonical_layer_catalog()
        ids = [l.layer_id for l in catalog]
        assert len(ids) == len(set(ids))

    def test_all_have_layer_names(self):
        catalog = build_canonical_layer_catalog()
        for layer in catalog:
            assert layer.layer_name, f"Layer {layer.layer_id} has no name"

    def test_all_have_roadmap_numbers(self):
        catalog = build_canonical_layer_catalog()
        for layer in catalog:
            assert isinstance(layer.roadmap_number, int)

    def test_final_system_acceptance_is_bootstrap(self):
        catalog = build_canonical_layer_catalog()
        fsa = next(l for l in catalog if l.layer_id == "FINAL_SYSTEM_ACCEPTANCE")
        assert fsa.bootstrap_self_layer is True

    def test_final_system_acceptance_not_deferrable(self):
        catalog = build_canonical_layer_catalog()
        fsa = next(l for l in catalog if l.layer_id == "FINAL_SYSTEM_ACCEPTANCE")
        assert fsa.safe_deferral_allowed is False

    def test_layers_have_acceptance_modes(self):
        catalog = build_canonical_layer_catalog()
        for layer in catalog:
            assert isinstance(layer.acceptance_modes_required, list)

    def test_seed_kernel_required_all_modes(self):
        catalog = build_canonical_layer_catalog()
        sk = next(l for l in catalog if l.layer_id == "L0_SEED_KERNEL")
        assert len(sk.acceptance_modes_required) == 5

    def test_packaging_only_release(self):
        catalog = build_canonical_layer_catalog()
        pd = next(l for l in catalog if l.layer_id == "PACKAGING_DISTRIBUTION")
        assert pd.acceptance_modes_required == ["RELEASE_ACCEPTANCE"]

    def test_layer_ids_in_order(self):
        catalog = build_canonical_layer_catalog()
        expected_first = "L0_SEED_KERNEL"
        expected_last = "FINAL_SYSTEM_ACCEPTANCE"
        assert catalog[0].layer_id == expected_first
        assert catalog[-1].layer_id == expected_last


class TestValidateLayerCatalog:
    def test_valid_catalog(self):
        catalog = build_canonical_layer_catalog()
        errors = validate_layer_catalog(catalog)
        assert errors == []

    def test_empty_catalog(self):
        errors = validate_layer_catalog([])
        assert any("FINAL_SYSTEM_ACCEPTANCE" in e for e in errors)

    def test_duplicate_ids(self):
        layers = [
            FinalAcceptanceLayer(layer_id="L1", layer_name="One"),
            FinalAcceptanceLayer(layer_id="L1", layer_name="Duplicate"),
            FinalAcceptanceLayer(layer_id="FINAL_SYSTEM_ACCEPTANCE", layer_name="FSA"),
        ]
        errors = validate_layer_catalog(layers)
        assert any("Duplicate" in e for e in errors)

    def test_empty_layer_id(self):
        layers = [
            FinalAcceptanceLayer(layer_id="FINAL_SYSTEM_ACCEPTANCE", layer_name="FSA"),
            FinalAcceptanceLayer(layer_id="", layer_name="Empty"),
        ]
        errors = validate_layer_catalog(layers)
        assert any("empty layer_id" in e.lower() for e in errors)

    def test_empty_layer_name(self):
        layers = [
            FinalAcceptanceLayer(layer_id="FINAL_SYSTEM_ACCEPTANCE", layer_name="FSA"),
            FinalAcceptanceLayer(layer_id="L1", layer_name=""),
        ]
        errors = validate_layer_catalog(layers)
        assert any("empty layer_name" in e.lower() for e in errors)

    def test_missing_final_system_acceptance(self):
        layers = [
            FinalAcceptanceLayer(layer_id="L1", layer_name="One"),
            FinalAcceptanceLayer(layer_id="L2", layer_name="Two"),
        ]
        errors = validate_layer_catalog(layers)
        assert any("FINAL_SYSTEM_ACCEPTANCE layer missing" in e for e in errors)
