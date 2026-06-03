from __future__ import annotations
from typing import Any
from .runtime_models import LocalModelProfile, LocalHardwareProfile, LocalRuntimeRequestLimits


def estimate_memory_budget(
    model_profile: LocalModelProfile,
    hardware_profile: LocalHardwareProfile,
    request_limits: LocalRuntimeRequestLimits,
) -> dict:
    model_bytes = estimate_model_memory_bytes(model_profile)
    context_bytes = estimate_context_memory_bytes(model_profile, request_limits.max_total_context_tokens)
    total = model_bytes + context_bytes
    conservative_limit = hardware_profile.conservative_ram_limit_bytes or (4 * 1024 ** 3)
    fits = total <= conservative_limit
    return {
        "estimated_model_bytes": model_bytes,
        "estimated_context_bytes": context_bytes,
        "estimated_total_bytes": total,
        "conservative_limit_bytes": conservative_limit,
        "fits": fits,
        "margin_bytes": conservative_limit - total if fits else 0,
    }


def estimate_model_memory_bytes(model_profile: LocalModelProfile) -> int:
    if model_profile.model_size_bytes:
        return model_profile.model_size_bytes
    if model_profile.parameter_count:
        bytes_per_param = {"F32": 4, "F16": 2, "Q8": 1, "Q6": 0.75, "Q5": 0.625, "Q4": 0.5}
        bpp = bytes_per_param.get(model_profile.quantization, 2)
        return int(model_profile.parameter_count * bpp)
    return 2 * 1024 ** 3


def estimate_context_memory_bytes(model_profile: LocalModelProfile, requested_context_tokens: int) -> int:
    return min(requested_context_tokens, model_profile.max_context_tokens or 8192) * 2


def check_memory_fit(estimated: dict, hardware_profile: LocalHardwareProfile) -> dict:
    total = estimated.get("estimated_total_bytes", 0)
    limit = hardware_profile.conservative_ram_limit_bytes or (4 * 1024 ** 3)
    fits = total <= limit
    return {"fits": fits, "total_bytes": total, "limit_bytes": limit, "excess_bytes": max(0, total - limit)}
