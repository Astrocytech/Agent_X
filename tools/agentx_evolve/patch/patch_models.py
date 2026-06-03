from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

SESSION_CREATED = "CREATED"
SESSION_LOADED = "LOADED"
SESSION_PROPOSAL_LOADED = "PROPOSAL_LOADED"
SESSION_GOVERNANCE_CHECKED = "GOVERNANCE_CHECKED"
SESSION_PATCH_APPLIED = "PATCH_APPLIED"
SESSION_VALIDATED = "VALIDATED"
SESSION_ACCEPTED = "ACCEPTED"
SESSION_ROLLED_BACK = "ROLLED_BACK"
SESSION_FAILED = "FAILED"
SESSION_BLOCKED = "BLOCKED"

ACTION_UPDATE = "UPDATE"
ACTION_CREATE = "CREATE"
ACTION_DELETE = "DELETE"

VALID_TRANSITIONS: dict[str, list[str]] = {
    SESSION_CREATED: [SESSION_LOADED, SESSION_FAILED, SESSION_BLOCKED],
    SESSION_LOADED: [SESSION_PROPOSAL_LOADED, SESSION_FAILED, SESSION_BLOCKED],
    SESSION_PROPOSAL_LOADED: [SESSION_GOVERNANCE_CHECKED, SESSION_FAILED, SESSION_BLOCKED],
    SESSION_GOVERNANCE_CHECKED: [SESSION_PATCH_APPLIED, SESSION_FAILED, SESSION_BLOCKED],
    SESSION_PATCH_APPLIED: [SESSION_VALIDATED, SESSION_ROLLED_BACK, SESSION_FAILED, SESSION_BLOCKED],
    SESSION_VALIDATED: [SESSION_ACCEPTED, SESSION_ROLLED_BACK, SESSION_FAILED, SESSION_BLOCKED],
    SESSION_ACCEPTED: [],
    SESSION_ROLLED_BACK: [],
    SESSION_FAILED: [SESSION_ROLLED_BACK],
    SESSION_BLOCKED: [],
}


def _validate_transition(current: str, next_state: str) -> str:
    allowed = VALID_TRANSITIONS.get(current, [])
    if next_state not in allowed:
        raise ValueError(
            f"Invalid state transition: {current} -> {next_state}. "
            f"Allowed from {current}: {allowed}"
        )
    return next_state


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, Path):
                result[f] = str(val)
            elif isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


@dataclass
class ImplementationSessionStatus:
    current: str = SESSION_CREATED
    history: list[dict] = field(default_factory=list)

    def transition_to(self, next_state: str) -> ImplementationSessionStatus:
        _validate_transition(self.current, next_state)
        self.history.append({
            "from": self.current,
            "to": next_state,
            "timestamp": utc_now_iso(),
        })
        self.current = next_state
        return self


@dataclass
class PatchAction:
    schema_version: str = "1.0"
    schema_id: str = "patch_action.schema.json"
    action_id: str = ""
    timestamp: str = ""
    target_file: str = ""
    change_type: str = ACTION_UPDATE
    old_text: str = ""
    new_text: str = ""
    old_hash: str | None = None
    new_hash: str | None = None
    status: str = "PENDING"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PatchSession:
    schema_version: str = "1.0"
    schema_id: str = "patch_session.schema.json"
    session_id: str = ""
    timestamp: str = ""
    source_component: str = "PatchExecution"
    proposal_id: str = ""
    governance_decision_id: str = ""
    risk_assessment_id: str = ""
    status: ImplementationSessionStatus = field(default_factory=ImplementationSessionStatus)
    target_paths: list[str] = field(default_factory=list)
    actions: list[PatchAction] = field(default_factory=list)
    rollback_snapshot_paths: list[str] = field(default_factory=list)
    validation_result: dict = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = to_dict(self)
        d["status"] = {
            "current": self.status.current,
            "history": self.status.history,
        }
        d["actions"] = [a.to_dict() for a in self.actions]
        return d


@dataclass
class RollbackSnapshot:
    schema_version: str = "1.0"
    schema_id: str = "rollback_snapshot.schema.json"
    snapshot_id: str = ""
    timestamp: str = ""
    session_id: str = ""
    file_path: str = ""
    before_hash: str = ""
    snapshot_path: str = ""
    restored: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ApprovedMutation:
    schema_version: str = "1.0"
    schema_id: str = "approved_mutation.schema.json"
    mutation_id: str = ""
    target_path: str = ""
    allowed_change_types: list[str] = field(default_factory=lambda: ["UPDATE", "CREATE"])
    governance_decision_id: str = ""
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def allows_path(self, path: str) -> bool:
        return path == self.target_path or path.startswith(self.target_path.rstrip("/") + "/")

    def allows_change_type(self, change_type: str) -> bool:
        return change_type in self.allowed_change_types


@dataclass
class MutationAllowlist:
    schema_version: str = "1.0"
    schema_id: str = "mutation_allowlist.schema.json"
    allowlist_id: str = ""
    timestamp: str = ""
    governance_decision_id: str = ""
    mutations: list[ApprovedMutation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"mutations": [m.to_dict() for m in self.mutations]} if self.mutations else {}

    def allows_mutation(self, target_path: str, change_type: str) -> bool:
        return any(
            m.allows_path(target_path) and m.allows_change_type(change_type)
            for m in self.mutations
        )

    def is_empty(self) -> bool:
        return len(self.mutations) == 0


@dataclass
class ImplementationEvidence:
    schema_version: str = "1.0"
    schema_id: str = "implementation_evidence.schema.json"
    evidence_id: str = ""
    timestamp: str = ""
    session_id: str = ""
    event_type: str = ""
    summary: str = ""
    details: dict = field(default_factory=dict)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
