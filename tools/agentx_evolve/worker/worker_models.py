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


# ── Layer 10 – Sandbox ──────────────────────────────────────────────

SR_ALLOW = "ALLOW"
SR_BLOCK = "BLOCK"


@dataclass
class SandboxResult:
    result_id: str = ""
    allowed: bool = True
    reason: str = ""
    status: str = SR_ALLOW


@dataclass
class WorkerSandbox:
    sandbox_id: str = ""
    allowed: bool = True
    reason: str = ""
    result: SandboxResult | None = None


# ── Layer 10 – Context Provenance ───────────────────────────────────

PC_PASS = "PASS"
PC_FAIL = "FAIL"


@dataclass
class ProvenanceCheck:
    check_id: str = ""
    status: str = PC_PASS
    details: str = ""


@dataclass
class ContextProvenance:
    provenance_id: str = ""
    source: str = ""
    checksum: str = ""
    verified: bool = True
    check: ProvenanceCheck | None = None


# ── Layer 10 – Repair Limit ─────────────────────────────────────────

RL_OK = "OK"
RL_EXCEEDED = "EXCEEDED"


@dataclass
class RepairLimit:
    max_repairs: int = 3
    current_repairs: int = 0
    status: str = RL_OK

    def can_repair(self) -> bool:
        return self.current_repairs < self.max_repairs

    def record_repair(self) -> str:
        self.current_repairs += 1
        if self.current_repairs >= self.max_repairs:
            self.status = RL_EXCEEDED
        return self.status


# ── Layer 10 – Budget ───────────────────────────────────────────────

BC_OK = "OK"
BC_EXCEEDED = "EXCEEDED"


@dataclass
class BudgetCheck:
    check_id: str = ""
    status: str = BC_OK
    message: str = ""


@dataclass
class WorkerBudget:
    budget_id: str = ""
    max_tokens: int = 0
    used_tokens: int = 0
    status: str = BC_OK

    def remaining(self) -> int:
        return max(0, self.max_tokens - self.used_tokens)

    def consume(self, tokens: int) -> str:
        self.used_tokens += tokens
        if self.used_tokens > self.max_tokens:
            self.status = BC_EXCEEDED
        return self.status


# ── Layer 10 – Concurrency ──────────────────────────────────────────


@dataclass
class ConcurrencyLimit:
    max_slots: int = 1
    used_slots: int = 0

    def available_slots(self) -> int:
        return max(0, self.max_slots - self.used_slots)

    def is_full(self) -> bool:
        return self.used_slots >= self.max_slots


@dataclass
class ConcurrencySlot:
    slot_id: str = ""
    occupied: bool = False


def acquire_slot(limit: ConcurrencyLimit, slot_id: str = "") -> ConcurrencySlot | None:
    if limit.is_full():
        return None
    limit.used_slots += 1
    return ConcurrencySlot(slot_id=slot_id or f"slot-{limit.used_slots}", occupied=True)


def release_slot(limit: ConcurrencyLimit, slot: ConcurrencySlot) -> bool:
    if limit.used_slots <= 0:
        return False
    limit.used_slots -= 1
    slot.occupied = False
    return True


# ── Layer 10 – Failure Taxonomy ─────────────────────────────────────

WF_TIMEOUT = "TIMEOUT"
WF_MODEL_ERROR = "MODEL_ERROR"
WF_TOOL_ERROR = "TOOL_ERROR"
WF_POLICY_BLOCK = "POLICY_BLOCK"
WF_UNKNOWN = "UNKNOWN"


@dataclass
class WorkerFailure:
    failure_id: str = ""
    failure_type: str = WF_UNKNOWN
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


def classify_worker_failure(failure: WorkerFailure | dict | str) -> str:
    if isinstance(failure, WorkerFailure):
        return failure.failure_type
    if isinstance(failure, dict):
        return failure.get("failure_type", WF_UNKNOWN)
    return WF_UNKNOWN
