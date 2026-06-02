from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional


PLAN_STATUSES = ["DRAFT", "IN_PROGRESS", "COMPLETED", "BLOCKED"]
PRIORITIES = ["P0", "P1", "P2", "P3"]
CATEGORIES = [
    "GOVERNANCE", "STRUCTURE", "VALIDATION", "TESTING",
    "SCHEMA", "SPECIALIZATION", "INTEGRATION", "UNKNOWN",
]


@dataclass
class EvolutionDependency:
    schema_version: str = "1.0"
    dependency_id: str = ""
    required_id: str = ""
    description: str = ""
    dependency_type: str = "blocks"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvolutionStep:
    schema_version: str = "1.0"
    step_id: str = ""
    priority: str = "P2"
    category: str = "UNKNOWN"
    action: str = ""
    detail: str = ""
    dependencies: list = field(default_factory=list)
    status: str = "PENDING"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvolutionManifest:
    schema_version: str = "1.0"
    manifest_id: str = ""
    plan_id: str = ""
    step_count: int = 0
    completed_count: int = 0
    total_dependencies: int = 0
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvolutionAudit:
    schema_version: str = "1.0"
    audit_id: str = ""
    event_type: str = ""
    plan_id: str = ""
    timestamp: str = ""
    source_component: str = "EvolutionPlanner"
    status: str = "INITIATED"
    artifacts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvolutionPlan:
    schema_version: str = "1.0"
    plan_id: str = ""
    timestamp: str = ""
    source_component: str = "EvolutionPlanner"
    status: str = "DRAFT"
    steps: list = field(default_factory=list)
    manifest: Optional[dict] = None
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
