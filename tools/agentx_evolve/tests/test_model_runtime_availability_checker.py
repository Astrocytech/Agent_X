import os
import pytest
from pathlib import Path
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelInventory, AVAILABILITY_AVAILABLE, AVAILABILITY_MISSING, AVAILABILITY_BLOCKED,
)
from agentx_evolve.model_runtime.availability_checker import (
    check_model_availability, check_model_path_allowed, check_model_file_present,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"
MODEL_FILE = Path("/tmp/models/small-q4.gguf")


@pytest.fixture(autouse=True)
def ensure_model_file():
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODEL_FILE.touch()
    yield
    MODEL_FILE.unlink(missing_ok=True)


def _load_inventory(name="valid_model_inventory.json"):
    from agentx_evolve.model_runtime.model_inventory import load_model_inventory
    return load_model_inventory(FIXTURES / name)


def test_check_availability_known_model():
    inv = _load_inventory()
    decision = check_model_availability("small-q4", inv, {"repository_hash": "abc"})
    assert decision.availability in (AVAILABILITY_AVAILABLE, AVAILABILITY_BLOCKED)
    assert decision.model_id == "small-q4"
    assert decision.profile_repository_hash == "abc"


def test_check_availability_unknown_model():
    inv = _load_inventory()
    decision = check_model_availability("nonexistent", inv, {"repository_hash": ""})
    assert decision.availability == AVAILABILITY_MISSING
    assert decision.failure_class == "LOCAL_MODEL_NOT_FOUND"


def test_check_availability_disabled_model():
    inv = _load_inventory()
    import copy
    inv = copy.deepcopy(inv)
    inv.models[0] = dict(inv.models[0], enabled=False)
    inv.models[0]["model_id"] = "disabled-model"
    decision = check_model_availability("disabled-model", inv, {})
    assert decision.availability == AVAILABILITY_BLOCKED
    assert decision.failure_class == "LOCAL_MODEL_DISABLED"


def test_check_model_path_allowed_within_root():
    result = check_model_path_allowed(Path("/tmp/models/small-q4.gguf"), [Path("/tmp/models")])
    assert result["allowed"] is True


def test_check_model_path_allowed_outside_root():
    result = check_model_path_allowed(Path("/etc/passwd"), [Path("/tmp/models")])
    assert result["allowed"] is False


def test_check_model_file_present():
    result = check_model_file_present(Path(__file__))
    assert result["present"] is True
    assert result["size_bytes"] > 0


def test_check_model_file_not_present():
    result = check_model_file_present(Path("/tmp/nonexistent_file_abc123.xyz"))
    assert result["present"] is False
    assert result["size_bytes"] == 0


def test_check_availability_empty_inventory():
    empty_inv = LocalModelInventory(inventory_id="empty", models=[])
    decision = check_model_availability("m1", empty_inv, {})
    assert decision.availability == AVAILABILITY_MISSING
