import pytest
from agentx_evolve.model_runtime.local_runtime_profile import (
    get_local_runtime_profile,
    get_local_runtime_config,
    check_runtime_limits,
)
from agentx_evolve.model_runtime.runtime_models import LocalRuntimeProfile, RuntimeProfile


class TestGetLocalRuntimeProfile:
    def test_returns_local_profile(self):
        profile = get_local_runtime_profile()
        assert isinstance(profile, LocalRuntimeProfile)
        assert profile.profile_id == "local_default"


class TestGetLocalRuntimeConfig:
    def test_returns_dict(self):
        config = get_local_runtime_config()
        assert isinstance(config, dict)
        assert config["local_only"] is True
        assert config["network_allowed"] is False
        assert "max_total_context_tokens" in config

    def test_default_values(self):
        config = get_local_runtime_config()
        assert config["max_total_context_tokens"] == 8192
        assert config["default_context_window"] == 4096


class TestCheckRuntimeLimits:
    def test_within_limits(self):
        profile = LocalRuntimeProfile(max_total_context_tokens=8192)
        issues = check_runtime_limits(profile, 100)
        assert issues == []

    def test_exceeds_limits(self):
        profile = LocalRuntimeProfile(max_total_context_tokens=4096)
        issues = check_runtime_limits(profile, 5000)
        assert len(issues) >= 1

    def test_empty_profile(self):
        profile = RuntimeProfile()
        issues = check_runtime_limits(profile, 100)
        assert issues == []
