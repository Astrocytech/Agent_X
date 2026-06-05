import pytest
import jsonschema
import json
from pathlib import Path
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalModelInventory, LocalModelAvailabilityDecision,
    LocalRuntimeCompatibilityDecision,
    COMPATIBILITY_COMPATIBLE, COMPATIBILITY_INCOMPATIBLE,
    AVAILABILITY_AVAILABLE, AVAILABILITY_MISSING, AVAILABILITY_BLOCKED,
)

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def _load_schema(name):
    with open(SCHEMAS / name) as f:
        return json.load(f)


def test_unknown_model_id_blocked():
    from agentx_evolve.model_runtime.model_inventory import load_model_inventory
    inv = load_model_inventory(FIXTURES / "valid_model_inventory.json")
    from agentx_evolve.model_runtime.availability_checker import check_model_availability
    decision = check_model_availability("unknown", inv, {"repository_hash": ""})
    assert decision.availability in (AVAILABILITY_MISSING, AVAILABILITY_BLOCKED)


def test_gpu_requested_but_unavailable():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
        requires_gpu=True, supports_cpu=False,
    )
    runtime = LocalRuntimeProfile(
        runtime_id="r1", runtime_name="R1", runtime_kind="local",
        supported_model_formats=["gguf"], supported_quantizations=["Q4"],
        enabled=True,
    )
    hw = LocalHardwareProfile(
        hardware_profile_id="hw1", probe_mode="STATIC_ONLY",
        gpu_present=False, conservative_ram_limit_bytes=8589934592,
    )
    from agentx_evolve.model_runtime.compatibility_checker import check_runtime_compatibility
    limits = __import__("agentx_evolve.model_runtime.runtime_models").model_runtime.runtime_models.LocalRuntimeRequestLimits(max_total_context_tokens=2048)
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility != COMPATIBILITY_COMPATIBLE


def test_hosted_fallback_blocked():
    from agentx_evolve.model_runtime.runtime_mode import is_hosted_fallback_allowed
    assert is_hosted_fallback_allowed({}) is False


def test_schema_invalid_profile(tmp_path):
    schema = _load_schema("local_model_profile.schema.json")
    bad = {"model_name": "no-id"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_model_path_outside_boundary():
    from agentx_evolve.model_runtime.availability_checker import check_model_path_allowed
    result = check_model_path_allowed(Path("/etc/passwd"), [Path("/tmp/models")])
    assert result["allowed"] is False


def test_network_runtime_blocked():
    runtime = LocalRuntimeProfile(
        runtime_id="net-rt", runtime_name="Net Runtime", runtime_kind="local",
        supported_model_formats=["gguf"], supported_quantizations=["Q4"],
        uses_network=True, enabled=True,
    )
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
    )
    hw = LocalHardwareProfile(
        hardware_profile_id="hw1", probe_mode="STATIC_ONLY",
        conservative_ram_limit_bytes=8589934592,
    )
    from agentx_evolve.model_runtime.compatibility_checker import check_runtime_compatibility
    limits = __import__("agentx_evolve.model_runtime.runtime_models").model_runtime.runtime_models.LocalRuntimeRequestLimits(max_total_context_tokens=2048)
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE


def test_disabled_runtime_blocked():
    runtime = LocalRuntimeProfile(
        runtime_id="disabled-rt", runtime_name="Disabled", runtime_kind="local",
        supported_model_formats=["gguf"], supported_quantizations=["Q4"],
        enabled=False,
    )
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
    )
    hw = LocalHardwareProfile(
        hardware_profile_id="hw1", probe_mode="STATIC_ONLY",
        conservative_ram_limit_bytes=8589934592,
    )
    from agentx_evolve.model_runtime.compatibility_checker import check_runtime_compatibility
    limits = __import__("agentx_evolve.model_runtime.runtime_models").model_runtime.runtime_models.LocalRuntimeRequestLimits(max_total_context_tokens=2048)
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
