"""Deterministic time/clock-control abstraction.

Item 40 (34.1): Replace direct time/now calls with a controlled
clock for deterministic test replay.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Clock:
    """Clock abstraction that can be frozen for deterministic replay."""

    fixed_time: float | None = None
    fixed_iso: str | None = None

    def now(self) -> float:
        if self.fixed_time is not None:
            return self.fixed_time
        return time.time()

    def iso(self) -> str:
        if self.fixed_iso is not None:
            return self.fixed_iso
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def freeze(self, when: float | None = None) -> None:
        if when is not None:
            self.fixed_time = when
        else:
            self.fixed_time = time.time()
        self.fixed_iso = datetime.fromtimestamp(
            self.fixed_time, tz=timezone.utc
        ).isoformat(timespec="seconds")

    def unfreeze(self) -> None:
        self.fixed_time = None
        self.fixed_iso = None

    def is_frozen(self) -> bool:
        return self.fixed_time is not None

    def advance(self, seconds: float) -> None:
        if self.fixed_time is not None:
            self.freeze(self.fixed_time + seconds)
        else:
            self.freeze(time.time() + seconds)


SYSTEM_CLOCK = Clock()


def now() -> float:
    return SYSTEM_CLOCK.now()


def iso() -> str:
    return SYSTEM_CLOCK.iso()
