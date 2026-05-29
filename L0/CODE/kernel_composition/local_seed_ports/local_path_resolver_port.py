"""LocalPathResolverPort — resolves paths under .local/runtime."""

from __future__ import annotations

from pathlib import Path


class LocalPathResolverPort:
    runtime_safety_class = "production_seed_port"

    def resolve(self, path_type: str, name: str) -> str:
        return str(Path(".local/runtime") / path_type / name)
