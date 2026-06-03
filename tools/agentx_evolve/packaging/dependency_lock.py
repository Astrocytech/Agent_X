from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DependencyLock",
]


@dataclass
class DependencyLock:
    lock_id: str = ""
    dependencies: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_dependency(self, name: str, version: str, hash_: str) -> DependencyLock:
        self.dependencies.append({
            "name": name,
            "version": version,
            "sha256": hash_,
        })
        return self

    def check_integrity(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "valid": True,
            "mismatches": [],
            "missing": [],
        }
        for dep in self.dependencies:
            expected_hash = dep.get("sha256", "")
            if not expected_hash:
                result["valid"] = False
                result["missing"].append(dep["name"])
        return result
