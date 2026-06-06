from __future__ import annotations
import math
import warnings
from typing import Any

try:
    from agentx_evolve.scheduler.scheduler_retry import RetryPolicy

    warnings.warn(
        "scheduler_retry.RetryPolicy contains backoff logic; use backoff module directly",
        DeprecationWarning,
        stacklevel=2,
    )
    _HAS_RETRY = True
except ImportError:
    RetryPolicy = None  # type: ignore
    _HAS_RETRY = False

try:
    from agentx_evolve.scheduler.retry_policy import calculate_backoff_seconds

    warnings.warn(
        "retry_policy.calculate_backoff_seconds is deprecated; use backoff.calculate_backoff",
        DeprecationWarning,
        stacklevel=2,
    )
    _HAS_RETRY_POLICY = True
except ImportError:
    calculate_backoff_seconds = None  # type: ignore
    _HAS_RETRY_POLICY = False

__all__ = [
    "calculate_backoff",
    "reset_backoff",
]

_BACKOFF_STATE: dict[str, Any] = {}


def calculate_backoff(
    attempt: int,
    base_delay: float = 30.0,
    max_delay: float = 86400.0,
) -> float:
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def reset_backoff() -> None:
    _BACKOFF_STATE.clear()
