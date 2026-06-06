from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

DD_PASS = "PASS"
DD_FAIL = "FAIL"


@dataclass
class DrillResult:
    status: str = DD_PASS
    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RecoveryDrill:
    drill_id: str = ""
    timestamp: str = ""
    scope: str = ""
    result: DrillResult | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = ["RecoveryDrill", "DrillResult", "DD_PASS", "DD_FAIL"]
