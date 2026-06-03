from __future__ import annotations
from typing import Any
from .runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalModelInventory, LocalModelSelectionConstraints, LocalRuntimeRequestLimits,
)


def validate_runtime_profiles(
    model_profiles: list[LocalModelProfile],
    runtime_profiles: list[LocalRuntimeProfile],
    hardware_profile: LocalHardwareProfile,
    inventory: LocalModelInventory,
) -> dict:
    issues: list[str] = []
    runtime_ids = {r.runtime_id for r in runtime_profiles}
    for mp in model_profiles:
        for rid in mp.supported_runtime_ids:
            if rid not in runtime_ids:
                issues.append(f"Model {mp.model_id} references unknown runtime {rid}")
    ref_result = validate_profile_references({
        "model_profiles": model_profiles,
        "runtime_profiles": runtime_profiles,
        "inventory": inventory,
    })
    issues.extend(ref_result.get("issues", []))
    return {"valid": len(issues) == 0, "issues": issues}


def validate_profile_references(repository: dict) -> dict:
    issues: list[str] = []
    return {"valid": len(issues) == 0, "issues": issues}


def validate_selection_constraints(constraints: LocalModelSelectionConstraints) -> dict:
    issues: list[str] = []
    if constraints.max_model_size_bytes < 0:
        issues.append("max_model_size_bytes is negative")
    if constraints.max_context_tokens < 0:
        issues.append("max_context_tokens is negative")
    return {"valid": len(issues) == 0, "issues": issues}


def validate_request_limits(limits: LocalRuntimeRequestLimits) -> dict:
    issues: list[str] = []
    if limits.max_prompt_tokens <= 0:
        issues.append("max_prompt_tokens must be positive")
    if limits.max_response_tokens <= 0:
        issues.append("max_response_tokens must be positive")
    if limits.max_total_context_tokens <= 0:
        issues.append("max_total_context_tokens must be positive")
    return {"valid": len(issues) == 0, "issues": issues}
