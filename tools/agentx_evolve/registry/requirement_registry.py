"""Central requirement registry with query API, alias/conflict/supersession handling.

Item 17.1: Replaces per-benchmark requirement lists with a system-wide registry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Requirement:
    requirement_id: str
    statement: str
    source_plans: list[str] = field(default_factory=list)
    requirement_class: str = "mandatory"  # mandatory | optional | deferred
    status: str = "implemented"  # implemented | pending | deferred | rejected
    aliases: list[str] = field(default_factory=list)
    superseded_by: str = ""
    conflicts_with: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RequirementRegistry:
    def __init__(self, path: Path | None = None):
        self._requirements: dict[str, Requirement] = {}
        self._alias_map: dict[str, str] = {}
        self.path = path
        if path and path.is_file():
            self.load(path)

    def register(self, req: Requirement) -> None:
        if req.requirement_id in self._requirements:
            raise ValueError(f"Duplicate requirement_id: {req.requirement_id}")
        self._requirements[req.requirement_id] = req
        for alias in req.aliases:
            self._alias_map[alias] = req.requirement_id
        # Resolve aliases
        for alias in req.aliases:
            self._alias_map[alias] = req.requirement_id

    def get(self, req_id: str) -> Requirement | None:
        if req_id in self._alias_map:
            req_id = self._alias_map[req_id]
        return self._requirements.get(req_id)

    def query(self, **filters: Any) -> list[Requirement]:
        results = list(self._requirements.values())
        for key, value in filters.items():
            results = [r for r in results if getattr(r, key, None) == value]
        return results

    def check_conflicts(self) -> list[dict[str, Any]]:
        conflicts = []
        for req_id, req in self._requirements.items():
            for conflict_id in req.conflicts_with:
                other = self.get(conflict_id)
                if other is not None:
                    conflicts.append({
                        "requirement_id": req_id,
                        "conflicts_with": conflict_id,
                        "both_active": req.status == "implemented" and other.status == "implemented",
                    })
        return conflicts

    def check_supersessions(self) -> list[dict[str, Any]]:
        supersessions = []
        for req_id, req in self._requirements.items():
            if req.superseded_by:
                superseder = self.get(req.superseded_by)
                if superseder is not None:
                    supersessions.append({
                        "superseded": req_id,
                        "superseded_by": req.superseded_by,
                        "superseder_active": superseder.status == "implemented",
                    })
        return supersessions

    def all_requirements(self) -> list[Requirement]:
        return list(self._requirements.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_size": len(self._requirements),
            "requirements": {k: v.to_dict() for k, v in self._requirements.items()},
            "alias_map": self._alias_map,
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load(self, path: Path) -> None:
        with open(path) as f:
            data = json.load(f)
        for req_id, req_data in data.get("requirements", {}).items():
            self._requirements[req_id] = Requirement(**req_data)
        self._alias_map.update(data.get("alias_map", {}))
