from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.backup.backup_models import BackupPolicy, SCHEMA_VERSION


@dataclass
class BackupPolicyRule:
    rule_id: str = ""
    pattern: str = ""
    allow: bool = True
    scope: str = ""
    priority: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


__all__ = ["BackupPolicyRule", "BackupPolicy"]
