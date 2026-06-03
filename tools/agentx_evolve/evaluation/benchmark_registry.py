from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional
from agentx_evolve.evaluation.path_guards import reject_path_traversal


class BenchmarkRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, Path] = {}

    def register(self, name: str, path: Path) -> None:
        reject_path_traversal(name)
        if not path.exists():
            raise FileNotFoundError(f"Suite path does not exist: {path}")
        if not path.suffix == ".json":
            raise ValueError(f"Suite path must be a JSON file: {path}")
        self._entries[name] = path.resolve()

    def lookup(self, name: str) -> Optional[Path]:
        return self._entries.get(name)

    def list_suites(self) -> Dict[str, str]:
        return {k: str(v) for k, v in sorted(self._entries.items())}

    def is_registered(self, name: str) -> bool:
        return name in self._entries

    def __len__(self) -> int:
        return len(self._entries)
