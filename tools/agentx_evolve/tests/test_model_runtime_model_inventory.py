import pytest
from pathlib import Path
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelInventory, LocalModelProfile,
)
from agentx_evolve.model_runtime.model_inventory import (
    load_model_inventory, validate_model_inventory,
    get_inventory_record, list_inventory_models,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_load_valid_model_inventory():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    assert inv.inventory_id == "inv-test"
    assert len(inv.models) == 2
    assert "/tmp/models" in inv.approved_model_roots


def test_load_model_inventory_empty():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    assert inv is not None


def test_validate_model_inventory_all_known():
    model_profiles = [
        LocalModelProfile(model_id="small-q4"),
        LocalModelProfile(model_id="small-q8"),
    ]
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    result = validate_model_inventory(inv, model_profiles)
    assert result["valid"] is True
    assert len(result["issues"]) == 0


def test_validate_model_inventory_unknown_reference():
    empty_profiles = []
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    result = validate_model_inventory(inv, empty_profiles)
    assert result["valid"] is False
    assert any("unknown model profile" in issue for issue in result["issues"])


def test_get_inventory_record_found():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    record = get_inventory_record(inv, "small-q4")
    assert record is not None
    assert record["model_id"] == "small-q4"


def test_get_inventory_record_not_found():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    record = get_inventory_record(inv, "nonexistent")
    assert record is None


def test_list_inventory_models():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    models = list_inventory_models(inv)
    assert len(models) == 2
    assert all(isinstance(m, dict) for m in models)
