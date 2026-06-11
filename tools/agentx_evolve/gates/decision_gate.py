from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

GateResult = Literal["ALLOW", "DENY", "REQUIRE_MORE_CHECKS", "ESCALATE", "ROLLBACK"]

DENY_CONDITIONS: list[str] = [
    "policy_denied",
    "capability_missing",
    "protected_target",
    "validation_failed",
    "rollback_plan_missing",
    "self_validator_modification",
    "self_promotion_attempt",
]


@dataclass
class GateOutput:
    decision: GateResult = "DENY"
    reason: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"decision": self.decision, "reason": self.reason, "details": self.details}


class MvpDecisionGate:
    def __init__(self) -> None:
        self._policy_engine: Any = None
        self._capability_graph: Any = None
        self._invariant_engine: Any = None
        self._simulation_engine: Any = None

    def bind_policy_engine(self, engine: Any) -> None:
        self._policy_engine = engine

    def bind_capability_graph(self, graph: Any) -> None:
        self._capability_graph = graph

    def bind_invariant_engine(self, engine: Any) -> None:
        self._invariant_engine = engine

    def bind_simulation_engine(self, engine: Any) -> None:
        self._simulation_engine = engine

    def evaluate(self, action: Any, context: dict[str, Any]) -> GateOutput:
        details: dict[str, Any] = {}

        if self._policy_engine:
            pol_decision, pol_reason = self._policy_engine.evaluate(
                context.get("scope", "action"), context
            )
            details["policy"] = {"decision": pol_decision, "reason": pol_reason}
            if pol_decision == "DENY":
                return GateOutput(decision="DENY", reason=f"Policy denied: {pol_reason}", details=details)
            if pol_decision == "ESCALATE":
                return GateOutput(decision="ESCALATE", reason=f"Policy escalated: {pol_reason}", details=details)

        if self._capability_graph and context.get("agent_id"):
            agent_id = context.get("agent_id", "")
            capability = context.get("capability", "execute")
            target = context.get("target", "")
            ok, reason = self._capability_graph.can(agent_id, capability, target)
            details["capability"] = {"allowed": ok, "reason": reason}
            if not ok:
                if reason == "self_modifying":
                    return GateOutput(decision="DENY", reason="Self-modifying capability denied", details=details)
                return GateOutput(decision="DENY", reason=f"Capability missing: {reason}", details=details)

        if self._invariant_engine:
            inv_results = self._invariant_engine.check_all(action, context)
            details["invariants"] = inv_results
            for inv in inv_results:
                if not inv.get("passed", True):
                    return GateOutput(decision="DENY", reason=f"Invariant failed: {inv.get('name', 'unknown')}", details=details)

        if context.get("risk_level") in ("high", "critical"):
            return GateOutput(decision="ESCALATE", reason="Risk level requires escalation", details=details)

        if context.get("requires_rollback_plan") and not context.get("has_rollback_plan"):
            return GateOutput(decision="DENY", reason="Rollback plan required", details=details)

        return GateOutput(decision="ALLOW", reason="All checks passed", details=details)
