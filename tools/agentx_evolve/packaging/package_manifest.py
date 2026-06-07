from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.packaging.package_builder import build_package, create_staging_tree

__all__ = [
    "PackageManifest",
]


@dataclass
class PackageManifest:
    manifest_id: str = ""
    package_name: str = ""
    package_version: str = ""
    files: list[dict[str, str]] = field(default_factory=list)
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_file(self, path: str, hash_: str) -> PackageManifest:
        entry = {"path": path, "sha256": hash_}
        if entry not in self.files:
            self.files.append(entry)
        return self

    def validate(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "valid": True,
            "missing_files": [],
            "hash_mismatches": [],
            "errors": [],
        }
        for entry in self.files:
            path = Path(entry["path"])
            if not path.exists():
                result["valid"] = False
                result["missing_files"].append(entry["path"])
                continue
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual_hash != entry.get("sha256", ""):
                result["valid"] = False
                result["hash_mismatches"].append({
                    "path": entry["path"],
                    "expected": entry.get("sha256", ""),
                    "actual": actual_hash,
                })
        return result
