from __future__ import annotations

from typing import Any

from agentx_evolve.model_runtime.profile_validator import validate_runtime_profiles

__all__ = [
    "validate_model_profile",
]


def validate_model_profile(profile: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not profile.get("model_id"):
        issues.append("Missing model_id")
    if not profile.get("runtime_ids"):
        issues.append("Missing runtime_ids")
    if not profile.get("model_format"):
        issues.append("Missing model_format")
    if profile.get("max_context_tokens", 0) <= 0:
        issues.append("max_context_tokens must be positive")
    return issues
