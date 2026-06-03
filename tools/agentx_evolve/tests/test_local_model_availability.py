import pytest
from pathlib import Path
from agentx_evolve.model_runtime.availability_checker import (
    check_model_availability, check_model_file_present,
)
from agentx_evolve.model_runtime.model_inventory import load_model_inventory
from agentx_evolve.model_runtime.runtime_models import AVAILABILITY_AVAILABLE, AVAILABILITY_MISSING, AVAILABILITY_BLOCKED

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_model_availability_available_missing_blocked():
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    repo = {"repository_hash": "abc123"}

    decision = check_model_availability("small-q4", inv, repo)
    assert decision.availability in (AVAILABILITY_AVAILABLE, AVAILABILITY_MISSING)

    decision2 = check_model_availability("nonexistent", inv, repo)
    assert decision2.availability == AVAILABILITY_MISSING


def test_model_file_present():
    result = check_model_file_present(Path("/nonexistent/file.bin"))
    assert result["present"] is False
