from __future__ import annotations

from datetime import datetime, timezone


class MvpDeterministicClock:
    def __init__(self, fixed_iso: str | None = None):
        self._fixed = fixed_iso

    def now(self) -> datetime:
        if self._fixed:
            return datetime.fromisoformat(self._fixed)
        return datetime.now(timezone.utc)

    def now_iso(self) -> str:
        return self.now().isoformat()

    def set_fixed(self, iso: str) -> None:
        self._fixed = iso

    def serialize(self) -> dict:
        return {"fixed_iso": self._fixed}

    @classmethod
    def deserialize(cls, data: dict) -> MvpDeterministicClock:
        return cls(fixed_iso=data.get("fixed_iso"))
