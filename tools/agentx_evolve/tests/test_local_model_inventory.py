import pytest
from pathlib import Path
from agentx_evolve.model_runtime.model_inventory import (
    load_model_inventory, validate_model_inventory, get_inventory_record,
)
from agentx_evolve.model_runtime.runtime_models import LocalModelProfile

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_inventory_loads():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    assert inv.inventory_id == "inv-test"
    assert len(inv.models) == 2


def test_inventory_rejects_unknown_model_reference():
    inv = load_model_inventory(FIXTURES / "invalid_model_inventory_unknown_model.json")
    profiles = [LocalModelProfile(model_id="small-q4"), LocalModelProfile(model_id="small-q8")]
    result = validate_model_inventory(inv, profiles)
    assert result["valid"] is False
    assert any("unknown-model" in i for i in result["issues"])


def test_get_inventory_record():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    rec = get_inventory_record(inv, "small-q4")
    assert rec is not None
    assert rec["model_id"] == "small-q4"
    assert get_inventory_record(inv, "nonexistent") is None
