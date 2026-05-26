"""Seed-owned trace contracts — TraceRecord, ReplayRecord, RunManifest, ID generation, event types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import time
import uuid


class RecordType(Enum):
    SESSION = "session"
    TURN = "turn"
    TRACE = "trace"
    CHECKPOINT = "checkpoint"
    POLICY_DECISION = "policy_decision"
    GOVERNANCE_DECISION = "governance_decision"
    SECURITY_DECISION = "security_decision"
    TOOL_CALL = "tool_call"
    MEMORY_RECORD = "memory_record"
    EVALUATION = "evaluation"
    EVIDENCE = "evidence"
    ARTIFACT = "artifact"
    PATCH_CANDIDATE = "patch_candidate"
    PROMOTION_DECISION = "promotion_decision"
    ROLLBACK = "rollback"
    FEEDBACK = "feedback"
    AUDIT = "audit"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESUME_TOKEN = "approval_resume_token"
    EVENT = "event"


def generate_id(record_type: RecordType, seed: str | None = None) -> str:
    prefix_map = {
        RecordType.SESSION: "sess",
        RecordType.TURN: "turn",
        RecordType.TRACE: "trc",
        RecordType.CHECKPOINT: "chk",
        RecordType.POLICY_DECISION: "pol",
        RecordType.GOVERNANCE_DECISION: "gov",
        RecordType.SECURITY_DECISION: "sec",
        RecordType.TOOL_CALL: "tc",
        RecordType.MEMORY_RECORD: "mem",
        RecordType.EVALUATION: "eval",
        RecordType.EVIDENCE: "evid",
        RecordType.ARTIFACT: "art",
        RecordType.PATCH_CANDIDATE: "pc",
        RecordType.PROMOTION_DECISION: "promo",
        RecordType.ROLLBACK: "rb",
        RecordType.FEEDBACK: "fb",
        RecordType.AUDIT: "aud",
        RecordType.APPROVAL_REQUEST: "apr",
        RecordType.APPROVAL_RESUME_TOKEN: "resume",
        RecordType.EVENT: "evt",
    }
    prefix = prefix_map[record_type]
    if seed:
        return f"{prefix}_{seed[:16]}"
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def generate_timestamp_id(record_type: RecordType) -> str:
    prefix_map = {
        RecordType.TRACE: "trc",
        RecordType.EVENT: "evt",
    }
    prefix = prefix_map.get(record_type, "rec")
    ts = int(time.time() * 1000)
    return f"{prefix}_{ts:x}_{uuid.uuid4().hex[:8]}"


@dataclass(frozen=True)
class AuditRecord:
    audit_id: str
    record_type: RecordType
    action: str
    subject_id: str
    profile_id: str
    timestamp: str
    decision: str
    reason: str
    parent_id: str = ""
    integrity_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ArtifactManifest:
    artifact_id: str
    artifact_type: str
    source_trace_id: str
    created_by: str
    integrity_hash: str
    storage_location: str
    retention_policy: str
    redaction_status: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PausedTurn:
    approval_request_id: str
    resume_token: str
    run_id: str
    profile_id: str
    requested_action: str
    risk_summary: str
    expires_at: str
    terminal_state: str = "paused_for_approval"


@dataclass(frozen=True)
class ApprovalDecision:
    approval_request_id: str
    approved: bool
    decided_by: str
    timestamp: str
    reason: str
    resume_token: str = ""


# Event schema types — used by trace recording and event routing

_EVENT_TYPES_LIST = [
    "kernel_started", "kernel_shutdown", "kernel_config_changed",
    "session_created", "session_restored", "session_paused", "session_resumed", "session_closed",
    "agent_created", "agent_bootstrapped", "agent_activated", "agent_terminated",
    "profile_loaded", "profile_updated", "profile_switched",
    "plan_created", "plan_validated", "plan_approved", "plan_rejected",
    "plan_execution_started", "plan_execution_completed",
    "tool_requested", "tool_authorized", "tool_denied", "tool_started", "tool_succeeded", "tool_failed",
    "event_handler_failed",
    "evaluation_started", "evaluation_completed",
    "memory_scope_allocated", "memory_scope_released", "memory_checkpoint_created",
    "approval_requested", "approval_granted", "approval_denied", "approval_expired",
    "resource_limit_exceeded", "resource_reservation_committed",
    "checkpoint_created", "rollback_started", "rollback_completed",
]

EVENT_TYPES: set[str] = set(_EVENT_TYPES_LIST)


class EventValidationError(ValueError):
    """Raised when an event fails schema validation."""


@dataclass(frozen=True)
class KernelEvent:
    event_id: str
    event_type: str
    source_type: str
    source_id: str
    target_type: str | None
    target_id: str | None
    session_id: str
    agent_id: str | None
    run_id: str
    task_id: str
    payload: dict[str, Any]
    timestamp: str
    sequence_number: int
    policy_context_id: str | None


def validate_event(event: KernelEvent) -> None:
    if event.event_type not in EVENT_TYPES:
        raise EventValidationError(f"Unknown event type: {event.event_type}")
    if not event.event_id.strip():
        raise EventValidationError("event_id must not be empty")
    if not event.session_id.strip():
        raise EventValidationError("session_id must not be empty")
    if not event.run_id:
        raise EventValidationError("run_id must not be empty")
    if event.sequence_number < 0:
        raise EventValidationError(
            f"sequence_number must be non-negative, got {event.sequence_number}"
        )


@dataclass
class TraceRecord:
    trace_id: str = ""
    run_id: str = ""
    input_hash: str = ""
    profile_id: str = ""
    config_hash: str = ""
    planner_decision_id: str = ""
    governance_decision_id: str = ""
    tool_request_id: str = ""
    tool_result_id: str = ""
    memory_ref_ids: list[str] = field(default_factory=list)
    evaluation_verdict_id: str = ""
    checkpoint_id: str = ""
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = ""
    timestamp: str = ""

    @classmethod
    def create(cls, run_id: str, events: list[dict], **kwargs: Any) -> TraceRecord:
        return cls(
            trace_id=f"trace-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            events=list(events),
            timestamp=datetime.now(timezone.utc).isoformat(),
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "input_hash": self.input_hash,
            "profile_id": self.profile_id,
            "config_hash": self.config_hash,
            "planner_decision_id": self.planner_decision_id,
            "governance_decision_id": self.governance_decision_id,
            "tool_request_id": self.tool_request_id,
            "tool_result_id": self.tool_result_id,
            "memory_ref_ids": list(self.memory_ref_ids),
            "evaluation_verdict_id": self.evaluation_verdict_id,
            "checkpoint_id": self.checkpoint_id,
            "event_count": len(self.events),
            "status": self.status,
            "timestamp": self.timestamp,
        }


@dataclass
class ReplayRecord:
    replay_id: str = ""
    trace_id: str = ""
    input_hash: str = ""
    output_hash: str = ""
    decision_ids: list[str] = field(default_factory=list)
    verified: bool = False
    errors: list[str] = field(default_factory=list)
    timestamp: str = ""

    @classmethod
    def create(cls, trace_id: str, **kwargs: Any) -> ReplayRecord:
        return cls(
            replay_id=f"replay-{uuid.uuid4().hex[:12]}",
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            **kwargs,
        )


@dataclass
class RunManifest:
    manifest_id: str = ""
    run_id: str = ""
    trace_id: str = ""
    checkpoint_id: str = ""
    profile_id: str = ""
    config_hash: str = ""
    input_hash: str = ""
    evaluation_verdict_id: str = ""
    status: str = ""
    timestamp: str = ""

    @classmethod
    def create(cls, run_id: str, **kwargs: Any) -> RunManifest:
        return cls(
            manifest_id=f"manifest-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            **kwargs,
        )


# === Evaluation types (merged from evaluation_contracts + seed_scorecard) ===

EVALUATION_SCHEMA_VERSION: str = "1.0"


@dataclass
class EvaluationVerdict:
    schema_version: str = EVALUATION_SCHEMA_VERSION
    verdict_id: str = ""
    score: float = 0.0
    passed: bool = False
    regression_risk: float = 0.0
    safety_risk: float = 0.0
    usefulness_delta: float = 0.0
    generality_delta: float = 0.0
    evidence_refs: list[str] = field(default_factory=list)
    is_noop: bool = False
    is_cosmetic_only: bool = False
    profile_regression: list[str] = field(default_factory=list)
    failure_reason: str = ""
    timestamp: str = ""

    @classmethod
    def create(cls, **kwargs: Any) -> EvaluationVerdict:
        return cls(
            verdict_id=f"ev-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "verdict_id": self.verdict_id,
            "score": self.score,
            "passed": self.passed,
            "regression_risk": self.regression_risk,
            "safety_risk": self.safety_risk,
            "usefulness_delta": self.usefulness_delta,
            "generality_delta": self.generality_delta,
            "evidence_refs": list(self.evidence_refs),
            "is_noop": self.is_noop,
            "is_cosmetic_only": self.is_cosmetic_only,
            "profile_regression": list(self.profile_regression),
            "failure_reason": self.failure_reason,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class EvaluationCriterion:
    name: str
    score: float
    weight: float = 1.0
    details: str = ""


@dataclass(frozen=True)
class EvaluationResult:
    score: float
    criteria: tuple[EvaluationCriterion, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_score(cls, score: float) -> EvaluationResult:
        return cls(score=score, criteria=(EvaluationCriterion(name="overall", score=score),))


# === Scorecard types (moved from seed_scorecard) ===


@dataclass
class ScorecardCategory:
    name: str
    weight: float
    score: float
    max_score: float = 1.0
    details: str = ""


@dataclass
class SeedScorecard:
    version: str = "1.0"
    generated_at: str = ""
    overall_score: float = 0.0
    categories: list[ScorecardCategory] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def compute_overall(self) -> float:
        if not self.categories:
            return 0.0
        total = sum((c.score / c.max_score) * c.weight for c in self.categories)
        weight_sum = sum(c.weight for c in self.categories)
        self.overall_score = total / weight_sum if weight_sum else 0.0
        return self.overall_score


# === Replay types (merged from replay_contract) ===


class ReplayMode(str, Enum):
    EVIDENCE_REPLAY = "evidence_replay"
    DETERMINISTIC_RERUN = "deterministic_rerun"
    REGRESSION_REPLAY = "regression_replay"


class ReplayStatus(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ReplayEvidence:
    turn_id: str = ""
    kernel_version: str = ""
    input_hash: str = ""
    profile_hash: str = ""
    policy_hash: str = ""
    planner_decision_hash: str = ""
    governance_decision_hash: str = ""
    gateway_result_hash: str = ""
    trace_id: str = ""
    checkpoint_id: str = ""
    memory_refs: list[str] = field(default_factory=list)
    final_output_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "kernel_version": self.kernel_version,
            "input_hash": self.input_hash,
            "profile_hash": self.profile_hash,
            "policy_hash": self.policy_hash,
            "planner_decision_hash": self.planner_decision_hash,
            "governance_decision_hash": self.governance_decision_hash,
            "gateway_result_hash": self.gateway_result_hash,
            "trace_id": self.trace_id,
            "checkpoint_id": self.checkpoint_id,
            "memory_refs": list(self.memory_refs),
            "final_output_hash": self.final_output_hash,
        }

    def missing_fields(self) -> list[str]:
        missing = []
        for field_name in self.__dataclass_fields__:
            val = getattr(self, field_name)
            if not val:
                missing.append(field_name)
        return missing

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ReplayEvidence:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def evidence_replay(recorded: ReplayEvidence) -> ReplayStatus:
    missing = recorded.missing_fields()
    if missing:
        return ReplayStatus.FAILED
    return ReplayStatus.MATCH


def deterministic_rerun(recorded: ReplayEvidence, current: ReplayEvidence) -> ReplayStatus:
    if recorded.missing_fields():
        return ReplayStatus.FAILED
    mismatches = []
    for field_name in recorded.__dataclass_fields__:
        rv = getattr(recorded, field_name)
        cv = getattr(current, field_name)
        if rv != cv:
            mismatches.append(field_name)
    if mismatches:
        return ReplayStatus.MISMATCH
    return ReplayStatus.MATCH
