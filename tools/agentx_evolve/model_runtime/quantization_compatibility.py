from __future__ import annotations

from typing import Any

from agentx_evolve.model_runtime.runtime_models import (
    QUANT_F32,
    QUANT_F16,
    QUANT_Q8,
    QUANT_Q6,
    QUANT_Q5,
    QUANT_Q4,
    QUANT_UNKNOWN,
)

__all__ = [
    "check_quantization_compatibility",
]

_KNOWN_QUANTIZATIONS = {QUANT_F32, QUANT_F16, QUANT_Q8, QUANT_Q6, QUANT_Q5, QUANT_Q4}


def check_quantization_compatibility(model: str, quantization: str) -> dict[str, Any]:
    compatible = quantization in _KNOWN_QUANTIZATIONS
    return {
        "model": model,
        "quantization": quantization,
        "compatible": compatible,
        "reason": "" if compatible else f"Quantization '{quantization}' is not recognized",
    }
