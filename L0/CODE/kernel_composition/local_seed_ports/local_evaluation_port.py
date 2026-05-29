"""LocalEvaluationPort — L0 seed evaluation port with failure-aware scoring."""

from __future__ import annotations

from core_kernel.contracts.trace_contracts import EvaluationVerdict
from core_kernel.models.kernel_results import SeedTurnResult
from core_kernel.models.enums.seed_failure_reason import SeedFailureReason
from typing import Any

from core_kernel.models.kernel_atoms import Goal

_FAILURE_OUTPUTS = frozenset(
    {
        SeedFailureReason.NO_ACTION.value,
        SeedFailureReason.NO_OUTPUT.value,
        SeedFailureReason.NO_DECISION.value,
        SeedFailureReason.TOOL_FAILED.value,
        SeedFailureReason.GOVERNANCE_DENIED.value,
        SeedFailureReason.PLANNER_ERROR.value,
        SeedFailureReason.GATEWAY_ERROR.value,
    }
)


class LocalEvaluationPort:
    runtime_safety_class = "production_seed_port"

    def evaluate(self, goal: Goal, output: str, **kwargs: Any) -> EvaluationVerdict:
        return self._score(goal, output, kwargs.get("ctx", {}))

    def evaluate_turn(self, turn: SeedTurnResult) -> EvaluationVerdict:
        goal = Goal(text=turn.goal_text)
        ctx = {
            "run_id": turn.run_id,
            "trace_id": turn.trace_id,
            "checkpoint_id": turn.checkpoint_id,
            "blocked": bool(turn.blocked_actions),
            "pending_approval": bool(turn.pending_approvals),
            "memory_refs": turn.memory_refs,
        }
        return self._score(goal, turn.tool_output, ctx)

    def _score(self, goal: Goal, output: str, context: dict[str, Any]) -> EvaluationVerdict:
        score = 0.0

        if not goal or not goal.text:
            score += 0.0
        else:
            score += 0.15

        if not output:
            score += 0.0
        else:
            score += 0.20

        if (
            output
            and output not in _FAILURE_OUTPUTS
            and not output.startswith(("blocked:", "failed:"))
        ):
            score += 0.25

        if output and len(output.strip()) >= 20:
            score += 0.10
        elif output:
            score += 0.03

        if goal and goal.text and output:
            goal_words = set(goal.text.lower().split()[:8])
            output_lower = output.lower()
            overlap = sum(1 for w in goal_words if w in output_lower and len(w) > 3)
            if overlap >= 2:
                score += 0.10
            elif overlap >= 1:
                score += 0.05

        has_content = output and output not in _FAILURE_OUTPUTS and len(output.strip()) > 5
        if has_content:
            score += 0.10

        if not context.get("blocked"):
            score += 0.05

        if not context.get("pending_approval"):
            score += 0.05

        if context.get("tool_name"):
            score += 0.05

        if context.get("trace_id"):
            score += 0.05

        if context.get("checkpoint_id"):
            score += 0.05

        if context.get("memory_refs"):
            score += 0.05

        evidence_refs = context.get("evidence_refs") or []
        if isinstance(evidence_refs, (list, tuple)):
            final_evidence = list(evidence_refs)
        else:
            final_evidence = []
        memory_refs = context.get("memory_refs") or []
        if isinstance(memory_refs, (list, tuple)):
            final_evidence.extend(m for m in memory_refs if m not in final_evidence)

        score = round(min(score, 1.0), 4)
        passed = score >= 0.9 and not context.get("blocked") and not context.get("pending_approval")
        return EvaluationVerdict.create(
            score=score,
            passed=passed,
            regression_risk=0.0,
            safety_risk=0.0,
            usefulness_delta=0.0,
            generality_delta=0.0,
            evidence_refs=final_evidence,
            is_noop=not bool(output),
            is_cosmetic_only=False,
            profile_regression=[],
            failure_reason="" if passed else "low_score",
        )
