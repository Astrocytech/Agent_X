from __future__ import annotations
from agentx_evolve.failure.failure_models import (
    RecoveryPlaybook, RecoveryAction,
    CAT_PATH_BOUNDARY, CAT_GOVERNANCE_BLOCKED, CAT_VALIDATION_FAILED,
    CAT_SUBPROCESS_BLOCKED, CAT_NETWORK_BLOCKED, CAT_SANDBOX_VIOLATION,
    CAT_POLICY_BLOCKED, CAT_PATCH_APPLY_FAILED, CAT_ROLLBACK_FAILED,
    CAT_INTERNAL_ERROR,
    SEV_LOW, SEV_MEDIUM, SEV_HIGH, SEV_CRITICAL,
    ACTION_RETRY, ACTION_ROLLBACK, ACTION_ESCALATE, ACTION_REPROPOSE,
    ACTION_ADJUST_POLICY, ACTION_SKIP, ACTION_REVIEW,
    new_id, utc_now_iso,
)


def default_playbooks() -> list[RecoveryPlaybook]:
    return [
        RecoveryPlaybook(
            playbook_id="pb-path-boundary",
            failure_category=CAT_PATH_BOUNDARY,
            severity=SEV_MEDIUM,
            description="Path boundary violation — skip the blocked path and continue",
            suggested_actions=[
                RecoveryAction(action_type=ACTION_SKIP, description="Skip the blocked path"),
                RecoveryAction(action_type=ACTION_REVIEW, description="Review path rules if false positive"),
            ],
            auto_recoverable=False,
        ),
        RecoveryPlaybook(
            playbook_id="pb-governance-blocked",
            failure_category=CAT_GOVERNANCE_BLOCKED,
            severity=SEV_MEDIUM,
            description="Governance check failed — repropose with governance session IDs",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_REPROPOSE,
                    description="Re-create the proposal with valid governance decision ID and session ID",
                ),
                RecoveryAction(
                    action_type=ACTION_RETRY,
                    description="Retry with correct governance credentials",
                ),
            ],
            auto_recoverable=True,
        ),
        RecoveryPlaybook(
            playbook_id="pb-validation-failed",
            failure_category=CAT_VALIDATION_FAILED,
            severity=SEV_MEDIUM,
            description="Post-apply validation command failed — review or roll back",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_RETRY,
                    description="Re-run validation commands",
                ),
                RecoveryAction(
                    action_type=ACTION_ROLLBACK,
                    description="Roll back the patch and investigate",
                    requires_approval=True,
                ),
                RecoveryAction(
                    action_type=ACTION_REVIEW,
                    description="Review validation output for required fixes",
                ),
            ],
            auto_recoverable=False,
        ),
        RecoveryPlaybook(
            playbook_id="pb-subprocess-blocked",
            failure_category=CAT_SUBPROCESS_BLOCKED,
            severity=SEV_HIGH,
            description="Subprocess command blocked by sandbox policy",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_ADJUST_POLICY,
                    description="Add command to allowlisted_commands if safe",
                    requires_approval=True,
                ),
                RecoveryAction(
                    action_type=ACTION_REPROPOSE,
                    description="Repropose without blocked command",
                ),
            ],
            auto_recoverable=False,
        ),
        RecoveryPlaybook(
            playbook_id="pb-network-blocked",
            failure_category=CAT_NETWORK_BLOCKED,
            severity=SEV_LOW,
            description="Network request blocked by policy",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_SKIP,
                    description="Skip the network request",
                ),
                RecoveryAction(
                    action_type=ACTION_ADJUST_POLICY,
                    description="Allowlist the network target if safe",
                    requires_approval=True,
                ),
            ],
            auto_recoverable=True,
        ),
        RecoveryPlaybook(
            playbook_id="pb-sandbox-violation",
            failure_category=CAT_SANDBOX_VIOLATION,
            severity=SEV_CRITICAL,
            description="Security sandbox violation — escalate immediately",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_ESCALATE,
                    description="Escalate to human review — possible security issue",
                    requires_approval=True,
                ),
                RecoveryAction(
                    action_type=ACTION_ROLLBACK,
                    description="Roll back any changes made before violation",
                    requires_approval=True,
                ),
            ],
            auto_recoverable=False,
        ),
        RecoveryPlaybook(
            playbook_id="pb-policy-blocked",
            failure_category=CAT_POLICY_BLOCKED,
            severity=SEV_HIGH,
            description="Tool or operation blocked by capability policy",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_ADJUST_POLICY,
                    description="Update capability registry to allow the operation",
                    requires_approval=True,
                ),
                RecoveryAction(
                    action_type=ACTION_REPROPOSE,
                    description="Use an alternative approved tool or operation",
                ),
            ],
            auto_recoverable=False,
        ),
        RecoveryPlaybook(
            playbook_id="pb-patch-apply-failed",
            failure_category=CAT_PATCH_APPLY_FAILED,
            severity=SEV_MEDIUM,
            description="Patch application failed — review error and repropose",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_REPROPOSE,
                    description="Fix old_text/new_text alignment and repropose",
                ),
                RecoveryAction(
                    action_type=ACTION_ROLLBACK,
                    description="Roll back any partial changes",
                    requires_approval=True,
                ),
            ],
            auto_recoverable=False,
        ),
        RecoveryPlaybook(
            playbook_id="pb-rollback-failed",
            failure_category=CAT_ROLLBACK_FAILED,
            severity=SEV_CRITICAL,
            description="Rollback operation failed — manual intervention required",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_ESCALATE,
                    description="Escalate — rollback snapshots may be corrupted",
                    requires_approval=True,
                ),
            ],
            auto_recoverable=False,
        ),
        RecoveryPlaybook(
            playbook_id="pb-internal-error",
            failure_category=CAT_INTERNAL_ERROR,
            severity=SEV_CRITICAL,
            description="Internal error — unexpected condition",
            suggested_actions=[
                RecoveryAction(
                    action_type=ACTION_ESCALATE,
                    description="Escalate to engineering — unexpected error path",
                    requires_approval=True,
                ),
            ],
            auto_recoverable=False,
        ),
    ]


class RecoveryPlaybookManager:
    def __init__(self, playbooks: list[RecoveryPlaybook] | None = None):
        self._playbooks = playbooks or default_playbooks()

    @property
    def playbooks(self) -> list[RecoveryPlaybook]:
        return list(self._playbooks)

    def get_playbook(self, category: str) -> RecoveryPlaybook | None:
        for pb in self._playbooks:
            if pb.failure_category == category:
                return pb
        return None

    def get_suggested_actions(self, category: str) -> list[RecoveryAction]:
        pb = self.get_playbook(category)
        if pb is None:
            return []
        return list(pb.suggested_actions)

    def add_playbook(self, playbook: RecoveryPlaybook) -> RecoveryPlaybook:
        self._playbooks.append(playbook)
        return playbook

    def remove_playbook(self, category: str) -> bool:
        for i, pb in enumerate(self._playbooks):
            if pb.failure_category == category:
                self._playbooks.pop(i)
                return True
        return False

    def is_auto_recoverable(self, category: str) -> bool:
        pb = self.get_playbook(category)
        if pb is None:
            return False
        return pb.auto_recoverable

    def categories(self) -> list[str]:
        return [pb.failure_category for pb in self._playbooks]
