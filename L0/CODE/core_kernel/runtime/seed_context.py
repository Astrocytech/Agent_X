from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SeedRuntimeContext:
    run_id: str
    session_id: str
    profile_id: str
    policy_id: str | None = None
    policy_decision_id: str | None = None
    planner_decision_id: str | None = None
    governance_decision_id: str | None = None
    execution_status: str = "not_attempted"
    memory_refs: list = field(default_factory=list)
    evaluation_verdict_id: str | None = None
    evaluation_score: float | None = None
    trace_id: str | None = None
    checkpoint_id: str | None = None
    blocked_actions: list = field(default_factory=list)
    pending_approvals: list = field(default_factory=list)
