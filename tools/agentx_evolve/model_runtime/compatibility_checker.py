from __future__ import annotations
from typing import Any
from .runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalRuntimeRequestLimits, LocalRuntimeCompatibilityDecision,
    COMPATIBILITY_COMPATIBLE, COMPATIBILITY_INCOMPATIBLE, COMPATIBILITY_DEGRADED,
    utc_now_iso, new_id,
)


def check_runtime_compatibility(
    model_profile: LocalModelProfile,
    runtime_profile: LocalRuntimeProfile,
    hardware_profile: LocalHardwareProfile,
    request_limits: LocalRuntimeRequestLimits,
) -> LocalRuntimeCompatibilityDecision:
    decision = LocalRuntimeCompatibilityDecision(
        decision_id=new_id("compat"),
        timestamp=utc_now_iso(),
        model_id=model_profile.model_id,
        runtime_id=runtime_profile.runtime_id,
        compatibility=COMPATIBILITY_INCOMPATIBLE,
        device="CPU",
        profile_repository_hash="",
        reason="",
    )

    fmt_ok = check_runtime_format_compatibility(model_profile, runtime_profile).get("compatible", False)
    quant_ok = check_quantization_compatibility(model_profile, runtime_profile).get("compatible", False)
    ctx_ok = check_context_window_compatibility(model_profile, request_limits.max_total_context_tokens).get("compatible", False)

    from .memory_budget import check_memory_fit, estimate_memory_budget
    mem_est = estimate_memory_budget(model_profile, hardware_profile, request_limits)
    mem_ok = check_memory_fit(mem_est, hardware_profile).get("fits", False)

    decision.format_compatible = fmt_ok
    decision.quantization_compatible = quant_ok
    decision.context_compatible = ctx_ok
    decision.memory_compatible = mem_ok

    if runtime_profile.uses_network:
        decision.compatibility = COMPATIBILITY_INCOMPATIBLE
        decision.reason = "Runtime requires network"
        decision.failure_class = "LOCAL_NETWORK_BLOCKED"
        return decision

    if not runtime_profile.enabled:
        decision.compatibility = COMPATIBILITY_INCOMPATIBLE
        decision.reason = f"Runtime {runtime_profile.runtime_id} is disabled"
        decision.failure_class = "LOCAL_RUNTIME_DISABLED"
        return decision

    if not fmt_ok:
        decision.compatibility = COMPATIBILITY_INCOMPATIBLE
        decision.reason = f"Model format {model_profile.model_format} not supported by runtime"
        decision.failure_class = "LOCAL_FORMAT_UNSUPPORTED"
        return decision

    if not quant_ok:
        decision.compatibility = COMPATIBILITY_INCOMPATIBLE
        decision.reason = f"Quantization {model_profile.quantization} not supported"
        decision.failure_class = "LOCAL_QUANTIZATION_UNSUPPORTED"
        return decision

    if not ctx_ok:
        decision.compatibility = COMPATIBILITY_INCOMPATIBLE
        decision.reason = "Context window limit exceeded"
        decision.failure_class = "LOCAL_CONTEXT_LIMIT_EXCEEDED"
        return decision

    if not mem_ok:
        decision.compatibility = COMPATIBILITY_INCOMPATIBLE
        decision.reason = "Memory budget exceeded"
        decision.failure_class = "LOCAL_MEMORY_LIMIT_EXCEEDED"
        return decision

    gpu_needed = model_profile.requires_gpu and not hardware_profile.gpu_present
    if gpu_needed:
        if runtime_profile.supports_cpu_fallback and model_profile.supports_cpu:
            decision.compatibility = COMPATIBILITY_DEGRADED
            decision.device = "CPU"
            decision.degradation_applied = True
            decision.degradation_reason = "GPU required but unavailable; CPU degradation used"
            return decision
        decision.compatibility = COMPATIBILITY_INCOMPATIBLE
        decision.reason = "GPU required but unavailable and CPU degradation is not permitted"
        decision.failure_class = "LOCAL_GPU_UNAVAILABLE"
        return decision

    decision.compatibility = COMPATIBILITY_COMPATIBLE
    decision.device = "GPU" if hardware_profile.gpu_present else "CPU"
    decision.reason = "All compatibility checks passed"
    return decision


def check_quantization_compatibility(
    model_profile: LocalModelProfile,
    runtime_profile: LocalRuntimeProfile,
) -> dict:
    if model_profile.quantization == "UNKNOWN":
        return {"compatible": False, "reason": "Unknown quantization"}
    compatible = model_profile.quantization in runtime_profile.supported_quantizations
    return {"compatible": compatible, "reason": "" if compatible else f"Quantization {model_profile.quantization} not supported"}


def check_context_window_compatibility(
    model_profile: LocalModelProfile,
    requested_context_tokens: int,
) -> dict:
    max_ctx = model_profile.max_context_tokens
    if max_ctx <= 0:
        return {"compatible": False, "reason": "Model has no declared context window"}
    compatible = requested_context_tokens <= max_ctx
    return {"compatible": compatible, "reason": "" if compatible else f"Requested {requested_context_tokens} exceeds max {max_ctx}"}


def check_runtime_format_compatibility(
    model_profile: LocalModelProfile,
    runtime_profile: LocalRuntimeProfile,
) -> dict:
    compatible = model_profile.model_format in runtime_profile.supported_model_formats
    return {"compatible": compatible, "reason": "" if compatible else f"Format {model_profile.model_format} not in {runtime_profile.supported_model_formats}"}
