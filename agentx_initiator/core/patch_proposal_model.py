from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional


PATCH_STATUSES = ["DRAFT", "REVIEW", "APPROVED", "REJECTED", "APPLIED"]
ACTION_TYPES = ["CREATE", "MODIFY", "DELETE", "REFACTOR", "NOOP"]
PATCH_PRIORITIES = ["P0", "P1", "P2", "P3"]


@dataclass
class PatchAction:
    schema_version: str = "1.0"
    action_id: str = ""
    action_type: str = "NOOP"
    target_path: str = ""
    content_ref: str = ""
    description: str = ""
    priority: str = "P2"
    status: str = "PENDING"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PatchContext:
    schema_version: str = "1.0"
    context_id: str = ""
    action_refs: list = field(default_factory=list)
    governance_ref: str = ""
    risk_ref: str = ""
    evolution_ref: str = ""
    validation_refs: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PatchValidation:
    schema_version: str = "1.0"
    validation_id: str = ""
    proposal_id: str = ""
    validator: str = ""
    status: str = "PENDING"
    result: str = ""
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PatchManifest:
    schema_version: str = "1.0"
    manifest_id: str = ""
    proposal_id: str = ""
    action_count: int = 0
    applied_count: int = 0
    total_dependencies: int = 0
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PatchAudit:
    schema_version: str = "1.0"
    audit_id: str = ""
    event_type: str = ""
    proposal_id: str = ""
    timestamp: str = ""
    source_component: str = "PatchProposalGenerator"
    status: str = "INITIATED"
    artifacts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PatchSpec:
    schema_version: str = "1.0"
    spec_id: str = ""
    proposal_id: str = ""
    title: str = ""
    task: str = ""
    risk_level: str = ""
    description: str = ""
    actions: list = field(default_factory=list)
    manifest: Optional[dict] = None
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
