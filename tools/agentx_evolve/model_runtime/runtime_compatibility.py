from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.model_runtime.runtime_models import (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_DEGRADED,
    QUANT_F32,
    QUANT_F16,
    QUANT_Q8,
    QUANT_Q6,
    QUANT_Q5,
    QUANT_Q4,
    QUANT_UNKNOWN,
    utc_now_iso,
    new_id,
)

RC_SCHEMA_VERSION = "1.0"
RC_SCHEMA_ID = "runtime_compatibility.schema.json"


@dataclass
class RuntimeCompatibilityResult:
    schema_version: str = RC_SCHEMA_VERSION
    schema_id: str = RC_SCHEMA_ID
    result_id: str = ""
    model_id: str = ""
    model_format: str = ""
    backend: str = ""
    device: str = ""
    quantization: str = QUANT_UNKNOWN
    compatibility: str = COMPATIBILITY_INCOMPATIBLE
    reason: str = ""
    timestamp: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {}
        for f in self.__dataclass_fields__:
            val = getattr(self, f)
            result[f] = val
        return result


_KNWON_FORMATS = {"gguf", "ggml", "pt", "pth", "bin", "safetensors", "onnx", "ot"}
_CPU_COMPATIBLE_FORMATS = {"gguf", "ggml", "onnx", "ot"}
_GPU_REQUIRED_FORMATS = {"pt", "pth", "bin", "safetensors"}
_QUANT_RANK = {
    QUANT_F32: 5,
    QUANT_F16: 4,
    QUANT_Q8: 3,
    QUANT_Q6: 2,
    QUANT_Q5: 1,
    QUANT_Q4: 0,
}


def check_model_runtime_compatibility(
    model_id: str,
    model_format: str,
    backend: str,
    device: str,
    quantization: str = QUANT_UNKNOWN,
    gpu_available: bool = False,
    gpu_vram_mb: float = 0.0,
    estimated_model_size_mb: float = 0.0,
) -> RuntimeCompatibilityResult:
    result = RuntimeCompatibilityResult(
        result_id=new_id("rc"),
        model_id=model_id,
        model_format=model_format.lower(),
        backend=backend.lower(),
        device=device.upper(),
        quantization=quantization,
        timestamp=utc_now_iso(),
    )

    fmt = model_format.lower()
    if fmt not in _KNWON_FORMATS:
        result.compatibility = COMPATIBILITY_INCOMPATIBLE
        result.reason = f"Unknown model format: {model_format}"
        return result

    if fmt in _GPU_REQUIRED_FORMATS and not gpu_available:
        result.compatibility = COMPATIBILITY_INCOMPATIBLE
        result.reason = f"Format {model_format} requires GPU but none available"
        return result

    if fmt in _CPU_COMPATIBLE_FORMATS:
        result.compatibility = COMPATIBILITY_COMPATIBLE
        result.reason = f"Format {model_format} compatible with {device}"
    else:
        result.compatibility = COMPATIBILITY_DEGRADED
        result.reason = f"Format {model_format} may require GPU"

    if gpu_available and gpu_vram_mb > 0 and estimated_model_size_mb > 0:
        if estimated_model_size_mb > gpu_vram_mb * 0.9:
            result.compatibility = COMPATIBILITY_DEGRADED
            result.warnings.append(
                f"Model size {estimated_model_size_mb:.0f}MB exceeds 90% of GPU VRAM {gpu_vram_mb:.0f}MB"
            )

    return result


def is_quantization_supported(quantization: str, device: str) -> bool:
    if device == "CPU":
        return quantization in {QUANT_F32, QUANT_Q8, QUANT_Q6, QUANT_Q5, QUANT_Q4, QUANT_UNKNOWN}
    if device == "GPU":
        return quantization in {QUANT_F32, QUANT_F16, QUANT_Q8, QUANT_Q6, QUANT_Q5, QUANT_Q4, QUANT_UNKNOWN}
    return True
