from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryRecallResult:
    status: str = "ok"
    error_type: str = ""
    record_count: int = 0
    degraded: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    recalled_items: list[dict[str, Any]] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return self.status == "failed"
