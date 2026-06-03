from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentx_evolve.model.model_models import new_id, utc_now_iso, to_dict

SC_CREATED = "CREATED"
SC_SCANNED = "SCANNED"
SC_PLANNED = "PLANNED"
SC_PROPOSED = "PROPOSED"
SC_GOVERNANCE_CHECKED = "GOVERNANCE_CHECKED"
SC_CONTEXT_BUILT = "CONTEXT_BUILT"
SC_MODEL_PROPOSED = "MODEL_PROPOSED"
SC_PATCH_APPLIED = "PATCH_APPLIED"
SC_VALIDATED = "VALIDATED"
SC_ROLLED_BACK = "ROLLED_BACK"
SC_ACCEPTED = "ACCEPTED"
SC_FAILED = "FAILED"
SC_BLOCKED = "BLOCKED"

SESSION_STATES = [
    SC_CREATED, SC_SCANNED, SC_PLANNED, SC_PROPOSED,
    SC_GOVERNANCE_CHECKED, SC_CONTEXT_BUILT, SC_MODEL_PROPOSED,
    SC_PATCH_APPLIED, SC_VALIDATED, SC_ROLLED_BACK,
    SC_ACCEPTED, SC_FAILED, SC_BLOCKED,
]

_TERMINAL_STATES = {SC_ACCEPTED, SC_FAILED, SC_BLOCKED, SC_ROLLED_BACK}

SESSION_TRANSITIONS: dict[str, list[str]] = {
    SC_CREATED: [SC_SCANNED, SC_FAILED, SC_BLOCKED],
    SC_SCANNED: [SC_PLANNED, SC_FAILED, SC_BLOCKED],
    SC_PLANNED: [SC_PROPOSED, SC_FAILED, SC_BLOCKED],
    SC_PROPOSED: [SC_GOVERNANCE_CHECKED, SC_FAILED, SC_BLOCKED],
    SC_GOVERNANCE_CHECKED: [SC_CONTEXT_BUILT, SC_FAILED, SC_BLOCKED],
    SC_CONTEXT_BUILT: [SC_MODEL_PROPOSED, SC_FAILED, SC_BLOCKED],
    SC_MODEL_PROPOSED: [SC_PATCH_APPLIED, SC_FAILED, SC_BLOCKED],
    SC_PATCH_APPLIED: [SC_VALIDATED, SC_ROLLED_BACK, SC_FAILED, SC_BLOCKED],
    SC_VALIDATED: [SC_ACCEPTED, SC_PLANNED, SC_MODEL_PROPOSED, SC_FAILED, SC_BLOCKED],
    SC_ROLLED_BACK: [SC_PLANNED, SC_FAILED, SC_BLOCKED],
    SC_ACCEPTED: [],
    SC_FAILED: [],
    SC_BLOCKED: [],
}

MAX_REPAIR_LOOPS = 3


@dataclass
class SessionRecord:
    session_id: str = ""
    status: str = SC_CREATED
    timestamp: str = ""
    description: str = ""
    scan_result: dict | None = None
    status_result: dict | None = None
    plan_result: list | None = None
    selected_candidate: dict | None = None
    proposal_result: dict | None = None
    governance_result: dict | None = None
    risk_assessment: dict | None = None
    task_packet_id: str = ""
    worker_output_id: str = ""
    patch_session_id: str = ""
    validation_result: dict | None = None
    completion_record: dict | None = None
    repair_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATES

    def can_transition_to(self, new_status: str) -> bool:
        allowed = SESSION_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    def transition_to(self, new_status: str) -> bool:
        if self.is_terminal():
            return False
        if not self.can_transition_to(new_status):
            return False
        self.status = new_status
        return True
