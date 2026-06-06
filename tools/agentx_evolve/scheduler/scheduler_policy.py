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
    def __init__(self):
        self._real_policy = None
        self._integration_available = False
        self._try_integration()

    def _try_integration(self) -> None:
        try:
            from policy import PolicyRegistry
            self._real_policy = PolicyRegistry()
            self._integration_available = True
        except ImportError:
            self._real_policy = None
            self._integration_available = False
        except Exception:
            self._real_policy = None
            self._integration_available = False

    def check_create_task(self, role: str, session_id: str) -> SchedulerPolicyDecision:
        if self._integration_available and self._real_policy:
            try:
                result = self._real_policy.check_permission(role, "scheduler.create_task")
                if result.get("allowed"):
                    return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "allowed_by_policy", "policy_registry")
                return SchedulerPolicyDecision(SCHEDULER_POLICY_DENY, result.get("reason", "denied_by_policy"), "policy_registry")
            except Exception:
                return SchedulerPolicyDecision(SCHEDULER_POLICY_BLOCKED, "policy_registry_error_fail_closed", "policy_registry")
        return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "fallback_allow_for_create_task", "fallback")

    def check_claim_task(self, role: str, session_id: str, task_id: str) -> SchedulerPolicyDecision:
        if self._integration_available and self._real_policy:
            try:
                result = self._real_policy.check_permission(role, "scheduler.claim_task", {"task_id": task_id})
                if result.get("allowed"):
                    return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "allowed_by_policy", "policy_registry")
                return SchedulerPolicyDecision(SCHEDULER_POLICY_DENY, result.get("reason", "denied_by_policy"), "policy_registry")
            except Exception:
                return SchedulerPolicyDecision(SCHEDULER_POLICY_BLOCKED, "policy_registry_error_fail_closed", "policy_registry")
        return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "fallback_allow_for_claim_task", "fallback")

    def check_progress_task(self, role: str, session_id: str, task_id: str, new_status: str) -> SchedulerPolicyDecision:
        if self._integration_available and self._real_policy:
            try:
                result = self._real_policy.check_permission(role, "scheduler.progress_task", {
                    "task_id": task_id, "new_status": new_status
                })
                if result.get("allowed"):
                    return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "allowed_by_policy", "policy_registry")
                return SchedulerPolicyDecision(SCHEDULER_POLICY_DENY, result.get("reason", "denied_by_policy"), "policy_registry")
            except Exception:
                return SchedulerPolicyDecision(SCHEDULER_POLICY_BLOCKED, "policy_registry_error_fail_closed", "policy_registry")
        return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "fallback_allow_for_progress_task", "fallback")

    def check_cancel_task(self, role: str, session_id: str, task_id: str) -> SchedulerPolicyDecision:
        if self._integration_available and self._real_policy:
            try:
                result = self._real_policy.check_permission(role, "scheduler.cancel_task", {"task_id": task_id})
                if result.get("allowed"):
                    return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "allowed_by_policy", "policy_registry")
                return SchedulerPolicyDecision(SCHEDULER_POLICY_DENY, result.get("reason", "denied_by_policy"), "policy_registry")
            except Exception:
                return SchedulerPolicyDecision(SCHEDULER_POLICY_BLOCKED, "policy_registry_error_fail_closed", "policy_registry")
        return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "fallback_allow_for_cancel_task", "fallback")

    def check_recover(self, role: str, session_id: str) -> SchedulerPolicyDecision:
        if self._integration_available and self._real_policy:
            try:
                result = self._real_policy.check_permission(role, "scheduler.recover")
                if result.get("allowed"):
                    return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "allowed_by_policy", "policy_registry")
                return SchedulerPolicyDecision(SCHEDULER_POLICY_DENY, result.get("reason", "denied_by_policy"), "policy_registry")
            except Exception:
                return SchedulerPolicyDecision(SCHEDULER_POLICY_BLOCKED, "policy_registry_error_fail_closed", "policy_registry")
        return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "fallback_allow_for_recover", "fallback")

    def check_inspect(self, role: str, session_id: str) -> SchedulerPolicyDecision:
        if self._integration_available and self._real_policy:
            try:
                result = self._real_policy.check_permission(role, "scheduler.inspect")
                if result.get("allowed"):
                    return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "allowed_by_policy", "policy_registry")
                return SchedulerPolicyDecision(SCHEDULER_POLICY_DENY, result.get("reason", "denied_by_policy"), "policy_registry")
            except Exception:
                return SchedulerPolicyDecision(SCHEDULER_POLICY_BLOCKED, "policy_registry_error_fail_closed", "policy_registry")
        return SchedulerPolicyDecision(SCHEDULER_POLICY_ALLOW, "fallback_allow_for_inspect", "fallback")

    @staticmethod
    def validate_transition(current_status: str, new_status: str) -> bool:
        allowed = SCHEDULER_VALID_TRANSITIONS.get(current_status, [])
        return new_status in allowed
