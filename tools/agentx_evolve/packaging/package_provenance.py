from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "PackageProvenance",
]


@dataclass
class PackageProvenance:
    source_repo: str = ""
    build_command: str = ""
    builder: str = ""
    build_id: str = ""
    built_at: str = ""
    package_name: str = ""
    package_version: str = ""
    commit_sha: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_repo": self.source_repo,
            "build_command": self.build_command,
            "builder": self.builder,
            "build_id": self.build_id,
            "built_at": self.built_at,
            "package_name": self.package_name,
            "package_version": self.package_version,
            "commit_sha": self.commit_sha,
            "metadata": self.metadata,
            "warnings": self.warnings,
            "errors": self.errors,
        }
