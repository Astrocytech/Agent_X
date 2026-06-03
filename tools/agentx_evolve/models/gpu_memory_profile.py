from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "GPUMemoryProfile",
    "detect_gpu",
]


@dataclass
class GPUMemoryProfile:
    total_mb: int = 0
    available_mb: int = 0
    compute_capability: str = ""
    gpu_name: str = ""
    driver_version: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def detect_gpu() -> GPUMemoryProfile | None:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,compute_cap",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return None

        for line in result.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4:
                return GPUMemoryProfile(
                    total_mb=int(parts[1]),
                    available_mb=int(parts[2]),
                    compute_capability=parts[3],
                    gpu_name=parts[0],
                )
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return None

    try:
        import pynvml

        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count == 0:
            return None
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        cap = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
        return GPUMemoryProfile(
            total_mb=mem.total // (1024 * 1024),
            available_mb=mem.free // (1024 * 1024),
            compute_capability=f"{cap[0]}.{cap[1]}",
            gpu_name=name,
        )
    except ImportError:
        return None
    except Exception:
        return None
