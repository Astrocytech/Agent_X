from __future__ import annotations
from dataclasses import dataclass
from typing import Any

__all__ = [
    "SchedulerNetworkConfig",
    "check_connectivity",
]


@dataclass
class SchedulerNetworkConfig:
    host: str = "127.0.0.1"
    port: int = 0
    use_ssl: bool = False


def check_connectivity(config: SchedulerNetworkConfig) -> dict[str, Any]:
    return {
        "host": config.host,
        "port": config.port,
        "reachable": False,
        "error": "not implemented",
    }
