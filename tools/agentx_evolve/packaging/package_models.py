from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "PackageInfo",
    "PackageBuildInfo",
    "PackageValidationResult",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PackageInfo:
    name: str = ""
    version: str = ""
    path: str = ""
    sha256: str = ""
    size_bytes: int = 0
    created_at: str = ""


@dataclass
class PackageBuildInfo:
    build_id: str = ""
    package_name: str = ""
    package_version: str = ""
    format: str = "tar.gz"
    artifact_path: str = ""
    status: str = ""
    files_included: int = 0
    files_rejected: int = 0
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackageValidationResult:
    validation_id: str = ""
    package_path: str = ""
    status: str = "NOT_CHECKED"
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    created_at: str = ""
