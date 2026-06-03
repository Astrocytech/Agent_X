import pytest

from agentx_evolve.runtime.runtime_profile import (
    RuntimeProfile, ModelResourceBudget, DEFAULT_PROFILES,
    RP_CPU_ONLY_SAFE, RP_SMALL_GPU_8GB, RP_BALANCED_LOCAL, RP_HOSTED_OPTIONAL,
    ALL_RUNTIME_PROFILES,
)


def test_runtime_profile_constants():
    assert RP_CPU_ONLY_SAFE == "cpu_only_safe"
    assert RP_SMALL_GPU_8GB == "small_gpu_8gb"
    assert RP_BALANCED_LOCAL == "balanced_local"
    assert RP_HOSTED_OPTIONAL == "hosted_provider_optional"
    assert len(ALL_RUNTIME_PROFILES) == 4
    assert RP_CPU_ONLY_SAFE in ALL_RUNTIME_PROFILES


def test_runtime_profile_defaults():
    p = RuntimeProfile()
    assert p.profile_id == RP_CPU_ONLY_SAFE
    assert p.max_models_loaded == 1
    assert p.max_context_tokens == 4096
    assert p.max_output_tokens == 512
    assert p.max_retries == 2
    assert p.timeout_seconds == 60
    assert p.vram_gb == 0.0
    assert p.supports_json_mode is True


def test_runtime_profile_custom():
    p = RuntimeProfile(
        profile_id=RP_SMALL_GPU_8GB,
        max_models_loaded=2,
        max_context_tokens=8192,
        max_output_tokens=1024,
        max_retries=3,
        timeout_seconds=120,
        vram_gb=8.0,
        supports_json_mode=True,
    )
    assert p.profile_id == RP_SMALL_GPU_8GB
    assert p.vram_gb == 8.0


def test_runtime_profile_to_dict():
    p = RuntimeProfile(profile_id=RP_CPU_ONLY_SAFE)
    d = p.to_dict()
    assert d["profile_id"] == RP_CPU_ONLY_SAFE
    assert d["max_context_tokens"] == 4096


def test_default_profiles_contains_all():
    for pid in ALL_RUNTIME_PROFILES:
        assert pid in DEFAULT_PROFILES
        profile = DEFAULT_PROFILES[pid]
        assert isinstance(profile, RuntimeProfile)
        assert profile.profile_id == pid


def test_cpu_only_safe_default():
    p = DEFAULT_PROFILES[RP_CPU_ONLY_SAFE]
    assert p.max_context_tokens == 2048
    assert p.max_output_tokens == 256
    assert p.max_retries == 1
    assert p.timeout_seconds == 120
    assert p.vram_gb == 0.0


def test_small_gpu_default():
    p = DEFAULT_PROFILES[RP_SMALL_GPU_8GB]
    assert p.max_context_tokens == 4096
    assert p.vram_gb == 8.0


def test_balanced_local_default():
    p = DEFAULT_PROFILES[RP_BALANCED_LOCAL]
    assert p.max_context_tokens == 8192
    assert p.vram_gb == 16.0


def test_hosted_provider_optional_default():
    p = DEFAULT_PROFILES[RP_HOSTED_OPTIONAL]
    assert p.max_context_tokens == 16384
    assert p.max_retries == 3


def test_model_resource_budget_default_profile():
    budget = ModelResourceBudget()
    assert budget.profile.profile_id == RP_CPU_ONLY_SAFE


def test_model_resource_budget_custom_profile():
    profile = DEFAULT_PROFILES[RP_BALANCED_LOCAL]
    budget = ModelResourceBudget(profile=profile)
    assert budget.profile.profile_id == RP_BALANCED_LOCAL


def test_switch_profile_valid():
    budget = ModelResourceBudget()
    assert budget.switch_profile(RP_SMALL_GPU_8GB) is True
    assert budget.profile.profile_id == RP_SMALL_GPU_8GB


def test_switch_profile_invalid():
    budget = ModelResourceBudget()
    assert budget.switch_profile("nonexistent") is False
    assert budget.profile.profile_id == RP_CPU_ONLY_SAFE


def test_max_context_for_task():
    budget = ModelResourceBudget()
    budget.switch_profile(RP_HOSTED_OPTIONAL)
    assert budget.max_context_for_task("any_task") == 16384


def test_headroom():
    budget = ModelResourceBudget()
    budget.switch_profile(RP_SMALL_GPU_8GB)
    assert budget.headroom(1000) == 3096
    assert budget.headroom(9999) == 0
