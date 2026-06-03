from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SP_CHECK_DRIFT = "CHECK_DRIFT"
SP_ENFORCE_DRIFT = "ENFORCE_DRIFT"


@dataclass
class SyncPolicy:
    mode: str = SP_CHECK_DRIFT
    allowed_operations: list[str] = field(default_factory=list)
    blocked_operations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def allows(self, operation: str) -> bool:
        return operation in self.allowed_operations

    def blocks(self, operation: str) -> bool:
        return operation in self.blocked_operations


__all__ = ["SyncPolicy", "SP_CHECK_DRIFT", "SP_ENFORCE_DRIFT"]
