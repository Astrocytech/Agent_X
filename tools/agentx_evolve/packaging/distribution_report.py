from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "DistributionReport",
]


@dataclass
class DistributionReport:
    report_id: str = ""
    created_at: str = ""
    layers: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_result(self, layer: str, status: str) -> DistributionReport:
        self.layers[layer] = status
        return self

    def summary(self) -> dict[str, Any]:
        passed = sum(1 for s in self.layers.values() if s in ("PASS", "OK", "SUCCESS"))
        failed = sum(1 for s in self.layers.values() if s in ("FAIL", "BLOCKED", "ERROR"))
        total = len(self.layers)
        return {
            "report_id": self.report_id,
            "created_at": self.created_at,
            "total_layers": total,
            "passed": passed,
            "failed": failed,
            "layers": dict(self.layers),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }
