from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class CommandEntry:
    name: str
    category: str
    description: str
    handler: Optional[Callable] = None
    arguments: dict = field(default_factory=dict)
    requested_effect: str = ""
    requires_governance: bool = False
    writes_artifacts: bool = False
    allowed_output_formats: list[str] = field(default_factory=lambda: ["text"])


_REGISTRY: dict[str, CommandEntry] = {}


def register(entry: CommandEntry):
    _REGISTRY[entry.name] = entry


def get(name: str) -> Optional[CommandEntry]:
    return _REGISTRY.get(name)


def list_commands() -> list[CommandEntry]:
    return list(_REGISTRY.values())


def list_active() -> list[CommandEntry]:
    return [e for e in _REGISTRY.values() if e.category in ("HELP", "SCAN", "STATUS")]


def list_reserved() -> list[CommandEntry]:
    return [e for e in _REGISTRY.values() if e.category == "RESERVED"]


def clear():
    _REGISTRY.clear()
