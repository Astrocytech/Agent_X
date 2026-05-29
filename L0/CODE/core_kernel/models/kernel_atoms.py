"""Core data structures for the universal agent kernel."""

__all__ = [
    "Goal",
    "KernelAtom",
    "PolicyDecision",
    "Task",
]


from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any


@dataclass
class KernelAtom:
    id: str = ""
    created_at: str = ""
    schema_version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        result = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if is_dataclass(value) and not isinstance(value, type):
                if hasattr(value, "to_dict"):
                    result[f.name] = value.to_dict()
                else:
                    result[f.name] = value
            elif isinstance(value, list):
                result[f.name] = [
                    (
                        item.to_dict()
                        if is_dataclass(item)
                        and not isinstance(item, type)
                        and hasattr(item, "to_dict")
                        else item
                    )
                    for item in value
                ]
            else:
                result[f.name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict):
        known_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)


@dataclass
class Goal(KernelAtom):
    text: str = ""
    constraints: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass
class Task(KernelAtom):
    goal_id: str = ""
    parent_task_id: str | None = None
    title: str = ""
    description: str = ""
    status: str = "created"
    task_type: str = ""
    assigned_profile_id: str = ""
    risk_level: str = "low"
    success_criteria: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class PolicyDecision(KernelAtom):
    target_type: str = ""
    target_id: str = ""
    allowed: bool = False
    requires_human_approval: bool = False
    risk_level: str = "low"
    reason: str = ""
