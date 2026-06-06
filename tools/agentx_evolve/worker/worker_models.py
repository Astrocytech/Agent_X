from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentx_evolve.models.model_models import new_id, to_dict

WO_SCHEMA_VERSION = "1.0"
WO_PROPOSED = "PROPOSED"
WO_NEEDS_MORE_CONTEXT = "NEEDS_MORE_CONTEXT"
WO_FAILED = "FAILED"
ALL_WORKER_STATUSES = [WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED]

CT_UPDATE = "UPDATE"
CT_CREATE = "CREATE"
CT_DELETE = "DELETE"
ALL_CHANGE_TYPES = [CT_UPDATE, CT_CREATE, CT_DELETE]


@dataclass
class ReplacementBlock:
    old_string: str = ""
    new_string: str = ""
    description: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class Change:
    target_file: str = ""
    change_type: str = CT_UPDATE
    instructions: str = ""
    replacement_blocks: list[ReplacementBlock] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class WorkerOutput:
    schema_version: str = WO_SCHEMA_VERSION
    worker_output_id: str = ""
    task_packet_id: str = ""
    parent_task_packet_id: str = ""
    status: str = WO_PROPOSED
    allowed_files_only: bool = True
    changes: list[Change] = field(default_factory=list)
    tests_to_run: list[str] = field(default_factory=list)
    edit_plan: str = ""
    explanation: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def target_files(self) -> list[str]:
        return sorted(set(c.target_file for c in self.changes))
