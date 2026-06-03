from agentx_evolve.policy.role_matrix import is_valid_role

from .scheduler_models import (
    SCHEDULER_POLICY_ALLOW, SCHEDULER_POLICY_DENY, SCHEDULER_POLICY_BLOCKED,
    SCHEDULER_POLICY_NOT_APPLICABLE,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED, SCHEDULER_STATUS_RUNNING,
    SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_BLOCKED, SCHEDULER_STATUS_PENDING_REVIEW,
    SCHEDULER_VALID_TRANSITIONS,
    SchedulerPolicyDecision,
)


class SchedulerPolicy:
    def _check(self, role: str, action: str) -> SchedulerPolicyDecision:
        if is_valid_role(role):
            return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, f"allowed_by_policy:{action}", "policy_registry")
        return SchedulerPolicyDecision(SCHEDULER_POLICY_DENY, f"denied_by_policy:{action}", "policy_registry")

    def check_create_task(self, role: str, session_id: str) -> SchedulerPolicyDecision:
        return self._check(role, "scheduler.create_task")

    def check_claim_task(self, role: str, session_id: str, task_id: str) -> SchedulerPolicyDecision:
        return self._check(role, "scheduler.claim_task")

    def check_progress_task(self, role: str, session_id: str, task_id: str, new_status: str) -> SchedulerPolicyDecision:
        return self._check(role, "scheduler.progress_task")

    def check_cancel_task(self, role: str, session_id: str, task_id: str) -> SchedulerPolicyDecision:
        return self._check(role, "scheduler.cancel_task")

    def check_recover(self, role: str, session_id: str) -> SchedulerPolicyDecision:
        return self._check(role, "scheduler.recover")

    def check_inspect(self, role: str, session_id: str) -> SchedulerPolicyDecision:
        return self._check(role, "scheduler.inspect")

    @staticmethod
    def validate_transition(current_status: str, new_status: str) -> bool:
        allowed = SCHEDULER_VALID_TRANSITIONS.get(current_status, [])
        return new_status in allowed
