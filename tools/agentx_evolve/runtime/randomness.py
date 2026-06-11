from __future__ import annotations

import hashlib
import uuid


class MvpSeededRandomness:
    def __init__(self, seed: str | None = None):
        if seed is None:
            seed = uuid.uuid4().hex
        self._seed = seed
        self._index = 0

    def next_hex(self, length: int = 8) -> str:
        raw = hashlib.sha256(f"{self._seed}:{self._index}".encode()).hexdigest()
        self._index += 1
        return raw[:length]

    def next_id(self, prefix: str = "") -> str:
        return f"{prefix}{self.next_hex(12)}"

    def reset(self) -> None:
        self._index = 0

    @property
    def seed(self) -> str:
        return self._seed

    def serialize(self) -> dict:
        return {"seed": self._seed, "index": self._index}

    @classmethod
    def deserialize(cls, data: dict) -> MvpSeededRandomness:
        obj = cls(seed=data.get("seed", uuid.uuid4().hex))
        obj._index = data.get("index", 0)
        return obj
