from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.promotion.gate_decision import (
    create_gate_decision,
    validate_gate_decision,
    is_promotion_approved,
)
from agentx_evolve.promotion.gate_policy import (
    collect_promotion_blockers,
    classify_blocker,
    has_non_overridable_blocker,
)
from agentx_evolve.promotion.gate_recorder import (
    write_gate_decision,
    write_latest_gate_decision,
    append_gate_decision_history,
)
from agentx_evolve.promotion.promotion_models import (
    PromotionGateDecision,
    ALL_PROMOTION_STATUSES,
    ALL_PROMOTION_DECISIONS,
)
from agentx_evolve.promotion.promotion_dispatcher import run_promotion_gate

__all__ = [
    "create_gate_decision",
    "validate_gate_decision",
    "is_promotion_approved",
    "collect_promotion_blockers",
    "classify_blocker",
    "has_non_overridable_blocker",
    "write_gate_decision",
    "write_latest_gate_decision",
    "append_gate_decision_history",
    "PromotionGateDecision",
    "ALL_PROMOTION_STATUSES",
    "ALL_PROMOTION_DECISIONS",
    "run_promotion_gate",
    "MvpPromotionGate",
    "MvpPromotionDecision",
]


@dataclass
class MvpPromotionDecision:
    action_id: str = ""
    run_id: str = ""
    promoted: bool = False
    reason: str = ""
    review_ref: str = ""
    evidence_refs: list[dict] = field(default_factory=list)
    observation_ref: str = ""
    gate_result_ref: str = ""
    invariant_pass: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "run_id": self.run_id,
            "promoted": self.promoted,
            "reason": self.reason,
            "review_ref": self.review_ref,
            "evidence_refs": self.evidence_refs,
            "observation_ref": self.observation_ref,
            "gate_result_ref": self.gate_result_ref,
            "invariant_pass": self.invariant_pass,
            "errors": list(self.errors),
        }


class MvpPromotionGate:
    def __init__(self) -> None:
        self._decisions: list[MvpPromotionDecision] = []

    @property
    def decisions(self) -> list[MvpPromotionDecision]:
        return list(self._decisions)

    def evaluate(self, action: Any, context: dict[str, Any]) -> MvpPromotionDecision:
        action_id = getattr(action, "action_id", "") if action else context.get("action_id", "")
        run_id = context.get("run_id", "")
        errors = []

        agent_id = context.get("agent_id", "")
        target_agent = context.get("target_agent", "")
        if agent_id and target_agent and agent_id == target_agent:
            decision = MvpPromotionDecision(
                action_id=action_id, run_id=run_id, promoted=False,
                reason="Self-promotion denied",
                errors=["Self-promotion: agent attempted to promote own action"],
            )
            self._decisions.append(decision)
            return decision

        review_ref = context.get("review_ref", "")
        if not review_ref:
            errors.append("Missing review reference")

        evidence_refs = context.get("evidence_refs", [])
        if not evidence_refs:
            errors.append("Missing evidence references")

        observation_ref = context.get("observation_ref", "")
        if not observation_ref:
            errors.append("Missing observation reference")

        gate_result = context.get("gate_result", "")
        if gate_result != "ALLOW":
            errors.append(f"Gate result is not ALLOW: {gate_result}")

        invariant_pass = context.get("invariant_pass", False)
        if not invariant_pass:
            errors.append("Invariant check failed")

        if errors:
            decision = MvpPromotionDecision(
                action_id=action_id, run_id=run_id, promoted=False,
                reason="; ".join(errors), errors=errors,
                review_ref=review_ref, evidence_refs=evidence_refs,
                observation_ref=observation_ref, gate_result_ref=gate_result,
                invariant_pass=invariant_pass,
            )
        else:
            decision = MvpPromotionDecision(
                action_id=action_id, run_id=run_id, promoted=True,
                reason="All checks passed", review_ref=review_ref,
                evidence_refs=evidence_refs, observation_ref=observation_ref,
                gate_result_ref=gate_result, invariant_pass=invariant_pass,
            )
        self._decisions.append(decision)
        return decision
