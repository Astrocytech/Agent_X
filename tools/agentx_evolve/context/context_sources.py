from __future__ import annotations
from pathlib import Path
from typing import Any

__all__ = [
    "load_source",
    "get_source_metadata",
    "list_available_sources",
]


def load_source(path: str | Path) -> dict[str, Any]:
    ...
    return {}


def get_source_metadata(path: str | Path) -> dict[str, Any]:
    ...
    return {}


def list_available_sources() -> list[dict[str, Any]]:
    ...
    return []
