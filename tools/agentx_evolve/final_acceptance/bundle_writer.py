from __future__ import annotations
from pathlib import Path
from typing import Any

__all__ = [
    "write_release_bundle",
]


def write_release_bundle(manifest: Any, output_dir: str | Path) -> str:
    ...
    return str(Path(output_dir) / "release_bundle.json")
