import pytest
from pathlib import Path
from agentx_evolve.model_runtime.profile_loader import load_selection_constraints
from agentx_evolve.model_runtime.profile_validator import validate_selection_constraints
from agentx_evolve.model_runtime.runtime_models import LocalModelSelectionConstraints

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_valid_constraints_load():
    c = load_selection_constraints(FIXTURES / "valid_selection_constraints_local_only.json")
    assert c.local_only is True


def test_selection_constraints_reject_unbounded_values():
    c = LocalModelSelectionConstraints(max_model_size_bytes=-1)
    result = validate_selection_constraints(c)
    assert result["valid"] is False
