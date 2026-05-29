from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

KERNEL_STATE_SCHEMA_VERSION = "1.0"


class RunState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    ROUTING = "routing"
    AUTHORIZING = "authorizing"
    EXECUTING = "executing"
    OBSERVING = "observing"
    INTERPRETING = "interpreting"
    EVALUATING = "evaluating"
    MEMORIZING = "memorizing"
    CHECKPOINTING = "checkpointing"
    RESPONDING = "responding"
    WAITING_FOR_HUMAN = "waiting_for_human"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    INVALID_INPUT = "invalid_input"
    POLICY_BLOCKED = "policy_blocked"
    PLANNER_FAILED = "planner_failed"
    TOOL_FAILED = "tool_failed"
    GATEWAY_FAILED = "gateway_failed"
    RECOVERY_PLANNING = "recovery_planning"
    DEGRADED_MODE = "degraded_mode"
    ROLLBACK_PENDING = "rollback_pending"
    RESUMED_FROM_CHECKPOINT = "resumed_from_checkpoint"


ALLOWED_STATE_TRANSITIONS = {
    RunState.IDLE: {RunState.PLANNING},
    RunState.PLANNING: {RunState.ROUTING, RunState.AUTHORIZING, RunState.FAILED, RunState.DEGRADED_MODE},
    RunState.ROUTING: {RunState.AUTHORIZING, RunState.FAILED},
    RunState.AUTHORIZING: {RunState.EXECUTING, RunState.WAITING_FOR_HUMAN, RunState.FAILED},
    RunState.EXECUTING: {RunState.OBSERVING, RunState.TOOL_FAILED, RunState.POLICY_BLOCKED, RunState.FAILED},
    RunState.OBSERVING: {RunState.INTERPRETING, RunState.EVALUATING},
    RunState.INTERPRETING: {RunState.EVALUATING, RunState.RECOVERY_PLANNING, RunState.FAILED},
    RunState.EVALUATING: {RunState.MEMORIZING, RunState.CHECKPOINTING, RunState.RECOVERY_PLANNING, RunState.FAILED},
    RunState.MEMORIZING: {RunState.CHECKPOINTING, RunState.RECOVERY_PLANNING, RunState.FAILED},
    RunState.CHECKPOINTING: {RunState.RESPONDING, RunState.PLANNING, RunState.COMPLETED, RunState.ROLLBACK_PENDING, RunState.FAILED},
    RunState.RESPONDING: {RunState.COMPLETED, RunState.PLANNING, RunState.FAILED},
    RunState.WAITING_FOR_HUMAN: {RunState.AUTHORIZING, RunState.RECOVERY_PLANNING, RunState.FAILED},
    RunState.INVALID_INPUT: {RunState.IDLE},
    RunState.COMPLETED: set(),
    RunState.FAILED: {RunState.ROLLED_BACK},
    RunState.ROLLED_BACK: {RunState.IDLE},
    RunState.POLICY_BLOCKED: {RunState.RECOVERY_PLANNING, RunState.FAILED},
    RunState.PLANNER_FAILED: {RunState.RECOVERY_PLANNING, RunState.FAILED},
    RunState.TOOL_FAILED: {RunState.RECOVERY_PLANNING},
    RunState.GATEWAY_FAILED: {RunState.RECOVERY_PLANNING, RunState.FAILED},
    RunState.RECOVERY_PLANNING: {RunState.PLANNING, RunState.DEGRADED_MODE, RunState.ROLLBACK_PENDING, RunState.WAITING_FOR_HUMAN, RunState.FAILED},
    RunState.DEGRADED_MODE: {RunState.OBSERVING, RunState.ROLLBACK_PENDING, RunState.FAILED},
    RunState.ROLLBACK_PENDING: {RunState.RESUMED_FROM_CHECKPOINT, RunState.FAILED},
    RunState.RESUMED_FROM_CHECKPOINT: {RunState.PLANNING},
}

RECOVERY_STATES = {
    RunState.POLICY_BLOCKED, RunState.PLANNER_FAILED, RunState.TOOL_FAILED,
    RunState.GATEWAY_FAILED, RunState.RECOVERY_PLANNING, RunState.DEGRADED_MODE,
    RunState.ROLLBACK_PENDING, RunState.RESUMED_FROM_CHECKPOINT,
}

FAILURE_TYPE_MAP: dict[RunState, str] = {
    RunState.POLICY_BLOCKED: "policy_denial",
    RunState.PLANNER_FAILED: "planner_error",
    RunState.TOOL_FAILED: "tool_error",
    RunState.GATEWAY_FAILED: "gateway_error",
    RunState.EVALUATING: "evaluation_failure",
    RunState.CHECKPOINTING: "checkpoint_error",
}


class KernelStateError(Exception):
    def __init__(self, message: str = "", reason: str = "") -> None:
        self.reason = reason
        super().__init__(f"[{reason}] {message}" if reason else message)


@dataclass
class KernelState:
    kernel_version: str = ""
    schema_version: str = KERNEL_STATE_SCHEMA_VERSION
    state_id: str = ""
    profile_id: str = ""
    active_constraints: list[str] = field(default_factory=list)
    memory_references: list[str] = field(default_factory=list)
    last_checkpoint_id: str = ""
    last_trace_id: str = ""
    capability_manifest_hash: str = ""
    policy_hash: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        profile_id: str = "",
        constraints: list[str] | None = None,
        manifest_hash: str = "",
        policy_hash: str = "",
    ) -> KernelState:
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            state_id=f"st-{uuid.uuid4().hex[:12]}",
            profile_id=profile_id,
            active_constraints=constraints or [],
            capability_manifest_hash=manifest_hash,
            policy_hash=policy_hash,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KernelState:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def save(self, path: Path | str) -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str))
        return self.state_id

    @classmethod
    def restore(cls, path: Path | str) -> KernelState:
        path = Path(path)
        if not path.exists():
            raise KernelStateError(
                f"State file not found: {path}",
                reason="file_not_found",
            )
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            raise KernelStateError(
                f"Corrupt state file: {exc}",
                reason="corrupt_file",
            ) from exc
        schema_version = data.get("schema_version", "")
        if schema_version != KERNEL_STATE_SCHEMA_VERSION:
            raise KernelStateError(
                f"Schema version mismatch: file={schema_version}, expected={KERNEL_STATE_SCHEMA_VERSION}",
                reason="schema_mismatch",
            )
        return cls.from_dict(data)

    def update_from_turn(
        self,
        trace_id: str = "",
        checkpoint_id: str = "",
        memory_refs: list[str] | None = None,
        policy_hash: str = "",
    ) -> None:
        if trace_id:
            self.last_trace_id = trace_id
        if checkpoint_id:
            self.last_checkpoint_id = checkpoint_id
        if memory_refs:
            self.memory_references = list(set(self.memory_references + memory_refs))
        if policy_hash:
            self.policy_hash = policy_hash
        self.updated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class StateModel:
    run_id: str = ""
    state: RunState = RunState.IDLE
    history: list[str] = field(default_factory=list)
    blocked_reason: str = ""
    unblock_condition: str = ""
    recovery_context: dict[str, Any] = field(default_factory=dict)

    def transition(self, new_state: RunState) -> tuple[bool, str]:
        allowed = ALLOWED_STATE_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            return (
                False,
                f"Cannot transition from {self.state.value} to {new_state.value}",
            )
        self.history.append(f"{self.state.value} -> {new_state.value}")
        self.state = new_state
        return True, ""

    def get_valid_transitions(self) -> set[RunState]:
        return ALLOWED_STATE_TRANSITIONS.get(self.state, set())

    def is_terminal(self) -> bool:
        return self.state in (RunState.COMPLETED, RunState.FAILED, RunState.ROLLED_BACK)

    def is_recovery_state(self) -> bool:
        return self.state in RECOVERY_STATES

    def set_recovery_context(self, **kwargs: Any) -> None:
        self.recovery_context.update(kwargs)

    def get_failure_type(self) -> str:
        return FAILURE_TYPE_MAP.get(self.state, "unknown")

    def get_recovery_action(self, target: RunState) -> str:
        return "unknown"
