"""Central schema registry for JSON Schema discovery, versioning, and artifact-type mapping.

Item 36 (31.1/31.2): Replaces scattered schema directories with a central catalog.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class SchemaEntry:
    schema_id: str
    path: str
    version: str
    artifact_types: list[str] = field(default_factory=list)
    description: str = ""
    valid: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SchemaRegistry:
    def __init__(self, path: Path | None = None):
        self._entries: dict[str, SchemaEntry] = {}
        self._artifact_map: dict[str, str] = {}
        self.path = path
        if path and path.is_file():
            self.load(path)

    def register(self, entry: SchemaEntry) -> None:
        self._entries[entry.schema_id] = entry
        for at in entry.artifact_types:
            self._artifact_map[at] = entry.schema_id

    def get(self, schema_id: str) -> SchemaEntry | None:
        return self._entries.get(schema_id)

    def find_by_artifact_type(self, artifact_type: str) -> SchemaEntry | None:
        sid = self._artifact_map.get(artifact_type)
        if sid:
            return self.get(sid)
        return None

    def discover(self, roots: list[Path]) -> list[SchemaEntry]:
        discovered = []
        for root in roots:
            if not root.is_dir():
                continue
            for f in root.rglob("*.schema.json"):
                rel = f.relative_to(root)
                sid = str(rel).replace("/", ".").replace("\\", ".").replace(".schema.json", "")
                # Attempt to read version from the schema itself
                version = "0.0.0"
                try:
                    with open(f) as fh:
                        schema_data = json.load(fh)
                    version = schema_data.get("version") or schema_data.get("$version", "0.0.0")
                except Exception:
                    pass
                entry = SchemaEntry(
                    schema_id=sid,
                    path=str(f),
                    version=str(version),
                    artifact_types=[str(rel.parent)],
                    description=f"Schema at {rel}",
                )
                self.register(entry)
                discovered.append(entry)
        return discovered

    def all_entries(self) -> list[SchemaEntry]:
        return list(self._entries.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_size": len(self._entries),
            "entries": {k: v.to_dict() for k, v in self._entries.items()},
            "artifact_type_map": self._artifact_map,
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load(self, path: Path) -> None:
        with open(path) as f:
            data = json.load(f)
        for sid, entry_data in data.get("entries", {}).items():
            self._entries[sid] = SchemaEntry(**entry_data)
        self._artifact_map.update(data.get("artifact_type_map", {}))
