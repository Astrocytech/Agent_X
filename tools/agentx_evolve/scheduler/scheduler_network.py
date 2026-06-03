from __future__ import annotations
from dataclasses import dataclass

__all__ = [
    "SchedulerNetworkConfig",
]


@dataclass
class SchedulerNetworkConfig:
    host: str = "127.0.0.1"
    port: int = 0
    use_ssl: bool = False

