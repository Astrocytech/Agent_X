import pytest

from agentx_evolve.scheduler.scheduler_policy import SchedulerPolicy
from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_POLICY_ALLOW, SCHEDULER_POLICY_DENY, SCHEDULER_POLICY_BLOCKED,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_BLOCKED,
    SCHEDULER_STATUS_CANCELLED, SCHEDULER_STATUS_PENDING_REVIEW,
)
from agentx_evolve.policy.policy_models import ROLE_ORCHESTRATOR


@pytest.fixture
def policy():
    return SchedulerPolicy()


def test_unknown_role_denies_create_task(policy):
    decision = policy.check_create_task("default", "ses1")
    assert decision.decision == SCHEDULER_POLICY_DENY


def test_empty_role_denies_create_task(policy):
    decision = policy.check_create_task("", "ses1")
    assert decision.decision == SCHEDULER_POLICY_DENY


def test_valid_role_allows_create_task(policy):
    decision = policy.check_create_task(ROLE_ORCHESTRATOR, "ses1")
    assert decision.decision == SCHEDULER_POLICY_ALLOW


def test_unknown_role_denies_claim_task(policy):
    decision = policy.check_claim_task("default", "ses1", "task1")
    assert decision.decision == SCHEDULER_POLICY_DENY


def test_unknown_role_denies_untrusted_claim(policy):
    decision = policy.check_claim_task("untrusted", "ses1", "task1")
    assert decision.decision == SCHEDULER_POLICY_DENY


def test_valid_role_allows_claim_task(policy):
    decision = policy.check_claim_task(ROLE_ORCHESTRATOR, "ses1", "task1")
    assert decision.decision == SCHEDULER_POLICY_ALLOW


def test_can_progress_task_allows_valid_transition(policy):
    assert policy.validate_transition(SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED) is True


def test_can_progress_task_blocks_invalid_transition(policy):
    assert policy.validate_transition(SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_RUNNING) is False


def test_unknown_role_denies_mutating_work(policy):
    decision = policy.check_create_task("default", "ses1")
    assert decision.decision == SCHEDULER_POLICY_DENY


def test_unknown_role_denies_inspect(policy):
    decision = policy.check_inspect("default", "ses1")
    assert decision.decision == SCHEDULER_POLICY_DENY


def test_valid_role_allows_inspect(policy):
    decision = policy.check_inspect(ROLE_ORCHESTRATOR, "ses1")
    assert decision.decision == SCHEDULER_POLICY_ALLOW


def test_all_checks_use_role_validation():
    policy = SchedulerPolicy()
    valid_role = ROLE_ORCHESTRATOR
    assert policy.check_create_task(valid_role, "s1").decision == SCHEDULER_POLICY_ALLOW
    assert policy.check_claim_task(valid_role, "s1", "t1").decision == SCHEDULER_POLICY_ALLOW
    assert policy.check_progress_task(valid_role, "s1", "t1", "RUNNING").decision == SCHEDULER_POLICY_ALLOW
    assert policy.check_cancel_task(valid_role, "s1", "t1").decision == SCHEDULER_POLICY_ALLOW
    assert policy.check_recover(valid_role, "s1").decision == SCHEDULER_POLICY_ALLOW
    assert policy.check_inspect(valid_role, "s1").decision == SCHEDULER_POLICY_ALLOW
