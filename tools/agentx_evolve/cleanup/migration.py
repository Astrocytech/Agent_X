"""General artifact migration and deprecation system.

Item 46 (40.1/40.2): Migration records for schema/data format
changes; deprecation tracking for old commands, paths, schemas.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MigrationRecord:
    migration_id: str
    source_schema_version: str
    target_schema_version: str
    artifact_type: str  # evidence | review | promotion | benchmark | event_log | patch | context
    changed_fields: list[str] = field(default_factory=list)
    fields_dropped: list[str] = field(default_factory=list)
    fields_added: list[str] = field(default_factory=list)
    reversibility_status: str = "unknown"  # reversible | irreversible | unknown
    validation_result: str = "pending"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class DeprecationRecord:
    deprecation_id: str
    old_path_or_name: str
    replacement: str
    artifact_type: str  # command | path | schema | cli | make_target | report
    compatibility_window: str = "3 months"
    warning_behavior: str = "log_warning"
    final_removal_condition: str = "next_major_version"
    alias_mapping: str = ""
    migration_path: str = ""
    created_at: str = ""


class MigrationManager:
    def __init__(self, storage_dir: str | Path = ".agentx-init/migrations"):
        self._storage = Path(storage_dir)
        self._storage.mkdir(parents=True, exist_ok=True)
        self._migrations: dict[str, MigrationRecord] = {}
        self._deprecations: dict[str, DeprecationRecord] = {}
        self._load()

    def _load(self) -> None:
        mig_file = self._storage / "migrations.json"
        if mig_file.exists():
            try:
                data = json.loads(mig_file.read_text())
                for item in data:
                    r = MigrationRecord(**item)
                    self._migrations[r.migration_id] = r
            except (json.JSONDecodeError, KeyError):
                pass
        dep_file = self._storage / "deprecations.json"
        if dep_file.exists():
            try:
                data = json.loads(dep_file.read_text())
                for item in data:
                    r = DeprecationRecord(**item)
                    self._deprecations[r.deprecation_id] = r
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self) -> None:
        self._storage.mkdir(parents=True, exist_ok=True)
        with open(self._storage / "migrations.json", "w") as f:
            json.dump([asdict(m) for m in self._migrations.values()], f, indent=2)
        with open(self._storage / "deprecations.json", "w") as f:
            json.dump([asdict(d) for d in self._deprecations.values()], f, indent=2)

    def register_migration(self, record: MigrationRecord) -> None:
        self._migrations[record.migration_id] = record
        self._save()

    def register_deprecation(self, record: DeprecationRecord) -> None:
        self._deprecations[record.deprecation_id] = record
        self._save()

    def get_migration(self, migration_id: str) -> MigrationRecord | None:
        return self._migrations.get(migration_id)

    def get_deprecation(self, deprecation_id: str) -> DeprecationRecord | None:
        return self._deprecations.get(deprecation_id)

    def find_migrations_by_artifact(self, artifact_type: str) -> list[MigrationRecord]:
        return [m for m in self._migrations.values() if m.artifact_type == artifact_type]

    def apply_migration(self, migration_id: str, data: dict) -> dict | None:
        """Apply a migration to transform data from old format to new."""
        mig = self._migrations.get(migration_id)
        if not mig:
            return None
        result = dict(data)
        for field in mig.fields_dropped:
            result.pop(field, None)
        for field in mig.fields_added:
            if field not in result:
                result[field] = None
        for old_field, new_field in zip(mig.fields_dropped, mig.changed_fields):
            if old_field in result:
                result[new_field] = result.pop(old_field)
        mig.validation_result = "applied"
        self._save()
        return result

    def check_deprecated(self, path_or_name: str) -> DeprecationRecord | None:
        for dep in self._deprecations.values():
            if dep.old_path_or_name == path_or_name:
                return dep
        return None

    def summary(self) -> dict:
        return {
            "migrations": len(self._migrations),
            "deprecations": len(self._deprecations),
            "recent_migrations": [asdict(m) for m in list(self._migrations.values())[-5:]],
        }
