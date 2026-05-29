"""Deprecated — use KernelTurnResponseV1 from kernel_turn_response_v1 instead."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FinalOutputContract:
    """Deprecated: use KernelTurnResponseV1 from kernel_turn_response_v1."""
    run_id: str = ""
    task_id: str = ""
    profile_id: str = ""
    final_response: str = ""
    trace_id: str = ""
    evaluation_id: str = ""
    policy_decision_id: str = ""
    status: str = ""
    created_at: str = ""

    @staticmethod
    def build(
        run_id: str,
        task_id: str,
        profile_id: str,
        final_response: str,
        trace_id: str,
        evaluation_id: str,
        policy_decision_id: str,
        status: str,
        created_at: str,
    ) -> FinalOutputContract:
        violations: list[str] = []
        if not trace_id:
            violations.append("missing_trace_id")
        if not evaluation_id:
            violations.append("missing_evaluation_id")
        if not policy_decision_id:
            violations.append("missing_policy_decision_id")
        if not task_id:
            violations.append("missing_task_id")
        if not run_id:
            violations.append("missing_run_id")
        if not profile_id:
            violations.append("missing_profile_id")
        if violations:
            msg = "; ".join(violations)
            raise ValueError(f"FinalOutputContract validation failed: {msg}")
        return FinalOutputContract(
            run_id=run_id,
            task_id=task_id,
            profile_id=profile_id,
            final_response=final_response,
            trace_id=trace_id,
            evaluation_id=evaluation_id,
            policy_decision_id=policy_decision_id,
            status=status,
            created_at=created_at,
        )

    def validate(self) -> list[str]:
        violations: list[str] = []
        if not self.trace_id:
            violations.append("missing_trace_id")
        if not self.evaluation_id:
            violations.append("missing_evaluation_id")
        if not self.policy_decision_id:
            violations.append("missing_policy_decision_id")
        if not self.task_id:
            violations.append("missing_task_id")
        if not self.run_id:
            violations.append("missing_run_id")
        if not self.profile_id:
            violations.append("missing_profile_id")
        return violations
