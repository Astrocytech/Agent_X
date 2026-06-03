import pytest
from agentx_evolve.model_runtime.runtime_models import (
    LocalRuntimeProfile,
    RuntimeProfile,
    HostedProviderProfile,
    make_local_default_runtime,
    make_hosted_default_runtime,
)


class TestRuntimeProfile:
    def test_defaults(self):
        r = RuntimeProfile()
        assert r.profile_id == ""
        assert r.max_total_context_tokens == 8192
        assert r.max_loaded_models == 1

    def test_custom(self):
        r = RuntimeProfile(
            profile_id="my_runtime",
            max_total_context_tokens=16384,
            max_loaded_models=4,
        )
        assert r.profile_id == "my_runtime"
        assert r.max_total_context_tokens == 16384
        assert r.max_loaded_models == 4


class TestLocalRuntimeProfile:
    def test_defaults(self):
        r = make_local_default_runtime()
        assert r.runtime_id == "local_default"
        assert r.enabled is True

    def test_custom(self):
        r = LocalRuntimeProfile(runtime_id="custom", runtime_name="Custom", runtime_kind="local",
                                max_context_tokens=16384)
        assert r.max_context_tokens == 16384


class TestHostedProviderProfile:
    def test_defaults(self):
        r = HostedProviderProfile()
        assert r.profile_id == "hosted_default"
        assert r.local_only is False
        assert r.network_allowed is True

    def test_custom(self):
        r = HostedProviderProfile(max_total_context_tokens=65536)
        assert r.max_total_context_tokens == 65536


class TestMakeLocalDefaultRuntime:
    def test_returns_local_runtime_profile(self):
        r = make_local_default_runtime()
        assert isinstance(r, LocalRuntimeProfile)
        assert r.runtime_id == "local_default"


class TestMakeHostedDefaultRuntime:
    def test_returns_hosted_profile(self):
        h = make_hosted_default_runtime()
        assert isinstance(h, LocalRuntimeProfile)
        assert h.runtime_id == "hosted_default"
