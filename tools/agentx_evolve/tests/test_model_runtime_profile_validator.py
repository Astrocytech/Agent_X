import pytest
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalModelInventory, LocalModelSelectionConstraints, LocalRuntimeRequestLimits,
)
from agentx_evolve.model_runtime.profile_validator import (
    validate_runtime_profiles, validate_profile_references,
    validate_selection_constraints, validate_request_limits,
)


def _make_model(**kw):
    defaults = dict(model_id="m1", supported_runtime_ids=["rt1"])
    defaults.update(kw)
    return LocalModelProfile(**defaults)


def _make_runtime(**kw):
    defaults = dict(runtime_id="rt1")
    defaults.update(kw)
    return LocalRuntimeProfile(**defaults)


def _make_inventory(**kw):
    defaults = dict(inventory_id="inv1", models=[])
    defaults.update(kw)
    return LocalModelInventory(**defaults)


def test_validate_runtime_profiles_valid():
    models = [_make_model()]
    runtimes = [_make_runtime()]
    hw = LocalHardwareProfile()
    inv = _make_inventory()
    result = validate_runtime_profiles(models, runtimes, hw, inv)
    assert result["valid"] is True


def test_validate_runtime_profiles_unknown_runtime_ref():
    models = [_make_model(supported_runtime_ids=["nonexistent"])]
    runtimes = [_make_runtime()]
    hw = LocalHardwareProfile()
    inv = _make_inventory()
    result = validate_runtime_profiles(models, runtimes, hw, inv)
    assert result["valid"] is False
    assert "references unknown runtime" in result["issues"][0]


def test_validate_profile_references():
    repo = {"model_profiles": [], "runtime_profiles": [], "inventory": None}
    result = validate_profile_references(repo)
    assert result["valid"] is True


def test_validate_selection_constraints_valid():
    constraints = LocalModelSelectionConstraints(max_model_size_bytes=1000, max_context_tokens=4096)
    result = validate_selection_constraints(constraints)
    assert result["valid"] is True


def test_validate_selection_constraints_negative_max_size():
    constraints = LocalModelSelectionConstraints(max_model_size_bytes=-1)
    result = validate_selection_constraints(constraints)
    assert result["valid"] is False
    assert "max_model_size_bytes is negative" in result["issues"]


def test_validate_selection_constraints_negative_context():
    constraints = LocalModelSelectionConstraints(max_context_tokens=-100)
    result = validate_selection_constraints(constraints)
    assert result["valid"] is False
    assert "max_context_tokens is negative" in result["issues"]


def test_validate_request_limits_valid():
    limits = LocalRuntimeRequestLimits(
        max_prompt_tokens=4096, max_response_tokens=2048, max_total_context_tokens=8192,
    )
    result = validate_request_limits(limits)
    assert result["valid"] is True


def test_validate_request_limits_zero_prompt():
    limits = LocalRuntimeRequestLimits(max_prompt_tokens=0)
    result = validate_request_limits(limits)
    assert result["valid"] is False
    assert "max_prompt_tokens must be positive" in result["issues"]


def test_validate_request_limits_zero_response():
    limits = LocalRuntimeRequestLimits(max_response_tokens=0)
    result = validate_request_limits(limits)
    assert result["valid"] is False
    assert "max_response_tokens must be positive" in result["issues"]


def test_validate_request_limits_zero_context():
    limits = LocalRuntimeRequestLimits(max_total_context_tokens=0)
    result = validate_request_limits(limits)
    assert result["valid"] is False
    assert "max_total_context_tokens must be positive" in result["issues"]
