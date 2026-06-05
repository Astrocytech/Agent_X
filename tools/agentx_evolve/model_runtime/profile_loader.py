from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalModelSelectionConstraints, LocalRuntimeRequestLimits,
)


def _load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _warn(msg: str) -> str:
    return msg


def load_model_profiles(profile_paths: list[Path]) -> list[LocalModelProfile]:
    seen: set[str] = set()
    profiles: list[LocalModelProfile] = []
    for path in profile_paths:
        data = _load_json(path)
        if data.get("schema_id") not in (None, "local_model_profile.schema.json"):
            continue
        model_id = data.get("model_id", "")
        if not model_id:
            continue
        if model_id in seen:
            continue
        seen.add(model_id)
        p = LocalModelProfile(
            model_id=model_id,
            model_name=data.get("model_name", model_id),
            model_family=data.get("model_family", ""),
            model_format=data.get("model_format", ""),
            model_path=data.get("model_path"),
            model_size_bytes=data.get("model_size_bytes"),
            parameter_count=data.get("parameter_count"),
            quantization=data.get("quantization", "UNKNOWN"),
            max_context_tokens=data.get("max_context_tokens", 0),
            supported_task_types=data.get("supported_task_types", []),
            supported_output_modes=data.get("supported_output_modes", []),
            supported_runtime_ids=data.get("supported_runtime_ids", []),
            preferred_runtime_ids=data.get("preferred_runtime_ids", []),
            requires_gpu=data.get("requires_gpu", False),
            supports_cpu=data.get("supports_cpu", True),
            supports_gpu=data.get("supports_gpu", False),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 100),
            profile_source_path=str(path),
            warnings=data.get("warnings", []),
            errors=data.get("errors", []),
        )
        profiles.append(p)
    profiles.sort(key=lambda p: p.model_id)
    return profiles


def load_runtime_profiles(profile_paths: list[Path]) -> list[LocalRuntimeProfile]:
    seen: set[str] = set()
    profiles: list[LocalRuntimeProfile] = []
    for path in profile_paths:
        data = _load_json(path)
        if data.get("schema_id") not in (None, "local_runtime_profile.schema.json"):
            continue
        rid = data.get("runtime_id", "")
        if not rid:
            continue
        if rid in seen:
            continue
        seen.add(rid)
        r = LocalRuntimeProfile(
            runtime_id=rid,
            runtime_name=data.get("runtime_name", rid),
            runtime_kind=data.get("runtime_kind", ""),
            supported_model_formats=data.get("supported_model_formats", []),
            supported_quantizations=data.get("supported_quantizations", []),
            supported_devices=data.get("supported_devices", []),
            max_context_tokens=data.get("max_context_tokens", 0),
            requires_server=data.get("requires_server", False),
            can_start_server=data.get("can_start_server", False),
            uses_network=data.get("uses_network", False),
            supports_cpu_fallback=data.get("supports_cpu_fallback", True),
            supports_gpu_fallback=data.get("supports_gpu_fallback", False),
            command_probe_allowed=data.get("command_probe_allowed", False),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 100),
            profile_source_path=str(path),
            warnings=data.get("warnings", []),
            errors=data.get("errors", []),
        )
        profiles.append(r)
    profiles.sort(key=lambda r: r.runtime_id)
    return profiles


def load_hardware_profile(profile_path: Path) -> LocalHardwareProfile:
    data = _load_json(profile_path)
    return LocalHardwareProfile(
        hardware_profile_id=data.get("hardware_profile_id", "hw-default"),
        probe_mode=data.get("probe_mode", "STATIC_ONLY"),
        cpu_arch=data.get("cpu_arch"),
        os_name=data.get("os_name"),
        ram_total_bytes=data.get("ram_total_bytes"),
        ram_available_bytes=data.get("ram_available_bytes"),
        gpu_present=data.get("gpu_present", False),
        gpu_name=data.get("gpu_name"),
        gpu_vram_total_bytes=data.get("gpu_vram_total_bytes"),
        gpu_vram_available_bytes=data.get("gpu_vram_available_bytes"),
        conservative_ram_limit_bytes=data.get("conservative_ram_limit_bytes", 0),
        conservative_vram_limit_bytes=data.get("conservative_vram_limit_bytes"),
        probe_timestamp=data.get("probe_timestamp"),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
    )


def load_selection_constraints(path: Path) -> LocalModelSelectionConstraints:
    data = _load_json(path)
    return LocalModelSelectionConstraints(
        allowed_model_ids=data.get("allowed_model_ids", []),
        blocked_model_ids=data.get("blocked_model_ids", []),
        allowed_runtime_ids=data.get("allowed_runtime_ids", []),
        blocked_runtime_ids=data.get("blocked_runtime_ids", []),
        allowed_quantizations=data.get("allowed_quantizations", []),
        blocked_quantizations=data.get("blocked_quantizations", []),
        allowed_devices=data.get("allowed_devices", []),
        max_model_size_bytes=data.get("max_model_size_bytes", 0),
        max_context_tokens=data.get("max_context_tokens", 0),
        max_estimated_memory_bytes=data.get("max_estimated_memory_bytes", 0),
        local_only=data.get("local_only", True),
        network_allowed=data.get("network_allowed", False),
        allow_model_download=data.get("allow_model_download", False),
        allow_server_start=data.get("allow_server_start", False),
        allow_cpu_fallback=data.get("allow_cpu_fallback", False),
        allow_gpu_fallback=data.get("allow_gpu_fallback", False),
        allow_hosted_fallback=data.get("allow_hosted_fallback", False),
        preferred_runtime_order=data.get("preferred_runtime_order", []),
        preferred_quantization_order=data.get("preferred_quantization_order", []),
        preferred_model_order=data.get("preferred_model_order", []),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
    )


def load_request_limits(path: Path) -> LocalRuntimeRequestLimits:
    data = _load_json(path)
    return LocalRuntimeRequestLimits(
        max_prompt_tokens=data.get("max_prompt_tokens", 4096),
        max_response_tokens=data.get("max_response_tokens", 2048),
        max_total_context_tokens=data.get("max_total_context_tokens", 8192),
        max_input_bytes=data.get("max_input_bytes", 0),
        max_output_bytes=data.get("max_output_bytes", 0),
        max_batch_size=data.get("max_batch_size", 1),
        max_concurrent_requests=data.get("max_concurrent_requests", 1),
        reserved_response_tokens=data.get("reserved_response_tokens", 512),
        safety_margin_tokens=data.get("safety_margin_tokens", 256),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
    )
