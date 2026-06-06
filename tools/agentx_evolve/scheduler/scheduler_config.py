from __future__ import annotations
import warnings
from dataclasses import dataclass, field

try:
    from agentx_evolve.scheduler.scheduler_models import SchedulerConfig as _SchedulerConfig

    warnings.warn(
        "scheduler_models.SchedulerConfig is deprecated; use scheduler_config.SchedulerConfig",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    _SchedulerConfig = None  # type: ignore

__all__ = [
    "SchedulerConfig",
]


@dataclass
class SchedulerConfig:
    max_concurrent: int = 10
    poll_interval: float = 5.0
    default_timeout: int = 300
    config_id: str = ""
