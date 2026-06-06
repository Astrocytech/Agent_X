from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "CoverageMatrix",
]


@dataclass
class CoverageMatrix:
    entries: list[dict[str, Any]] = field(default_factory=list)

    def add_entry(self, layer: str, covered: bool) -> None:
        self.entries.append({"layer": layer, "covered": covered})

    def summary(self) -> dict[str, Any]:
        total = len(self.entries)
        covered_count = sum(1 for e in self.entries if e["covered"])
        return {
            "total_layers": total,
            "covered": covered_count,
            "uncovered": total - covered_count,
            "coverage_pct": (covered_count / total * 100) if total else 100.0,
        }
