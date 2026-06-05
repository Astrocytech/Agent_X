from __future__ import annotations

from agentx_evolve.model_runtime.runtime_models import (
    LocalRuntimeProfile,
    RuntimeProfile,
    make_local_default_runtime,
)


def get_local_runtime_profile() -> LocalRuntimeProfile:
    return make_local_default_runtime()


def get_local_runtime_config() -> dict:
    return {
        "local_only": True,
        "network_allowed": False,
        "max_loaded_models": 1,
        "default_context_window": 4096,
        "max_total_context_tokens": 8192,
        "vram_budget_gb": 0.0,
        "endpoint_allowlisted": False,
        "allowed_endpoints": ["127.0.0.1", "localhost", "[::1]"],
    }


def check_runtime_limits(profile: RuntimeProfile, request_context_tokens: int) -> list[str]:
    issues: list[str] = []
    if request_context_tokens > profile.max_total_context_tokens:
        issues.append(
            f"Request context {request_context_tokens} exceeds runtime max {profile.max_total_context_tokens}"
        )
    return issues
