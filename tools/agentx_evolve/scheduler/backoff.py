from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta

BACKOFF_DEFAULT_BASE_SECONDS = 30
BACKOFF_DEFAULT_MULTIPLIER = 2
BACKOFF_DEFAULT_MAX_DELAY_SECONDS = 86400


def compute_backoff_seconds(
    attempt: int,
    base_seconds: int = BACKOFF_DEFAULT_BASE_SECONDS,
    multiplier: int = BACKOFF_DEFAULT_MULTIPLIER,
    max_delay: int = BACKOFF_DEFAULT_MAX_DELAY_SECONDS,
) -> int:
    delay = base_seconds * (multiplier ** attempt)
    return min(delay, max_delay)


def compute_next_run_at(
    attempt: int,
    base_seconds: int = BACKOFF_DEFAULT_BASE_SECONDS,
    multiplier: int = BACKOFF_DEFAULT_MULTIPLIER,
    max_delay: int = BACKOFF_DEFAULT_MAX_DELAY_SECONDS,
) -> str:
    delay = compute_backoff_seconds(attempt, base_seconds, multiplier, max_delay)
    now = datetime.now(timezone.utc)
    next_time = now + timedelta(seconds=delay)
    return next_time.strftime("%Y-%m-%dT%H:%M:%S.") + f"{next_time.microsecond:06d}Z"


def jitter_backoff_seconds(
    attempt: int,
    base_seconds: int = BACKOFF_DEFAULT_BASE_SECONDS,
    multiplier: int = BACKOFF_DEFAULT_MULTIPLIER,
    max_delay: int = BACKOFF_DEFAULT_MAX_DELAY_SECONDS,
    jitter_factor: float = 0.1,
) -> int:
    import random
    delay = compute_backoff_seconds(attempt, base_seconds, multiplier, max_delay)
    jitter = int(delay * jitter_factor * random.random())
    return delay + jitter


def linear_backoff_seconds(
    attempt: int,
    base_seconds: int = BACKOFF_DEFAULT_BASE_SECONDS,
    increment: int = 30,
    max_delay: int = BACKOFF_DEFAULT_MAX_DELAY_SECONDS,
) -> int:
    delay = base_seconds + (attempt * increment)
    return min(delay, max_delay)


def fibonacci_backoff_seconds(
    attempt: int,
    base_seconds: int = BACKOFF_DEFAULT_BASE_SECONDS,
    max_delay: int = BACKOFF_DEFAULT_MAX_DELAY_SECONDS,
) -> int:
    a, b = 0, 1
    for _ in range(attempt):
        a, b = b, a + b
    delay = base_seconds * a
    return min(delay, max_delay)
