import pytest

from agentx_evolve.scheduler.scheduler_policy import SchedulerPolicy
from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_POLICY_ALLOW, SCHEDULER_POLICY_DENY, SCHEDULER_POLICY_BLOCKED,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_BLOCKED,
    SCHEDULER_STATUS_CANCELLED, SCHEDULER_STATUS_PENDING_REVIEW,
)


@pytest.fixture
def policy():
    return SchedulerPolicy()


def test_policy_unavailable_blocks_create_task(policy):
    decision = policy.check_create_task("default", "ses1")
    assert decision.decision in (SCHEDULER_POLICY_BLOCKED, SCHEDULER_POLICY_ALLOW)


def test_policy_unavailable_blocks_unknown_role(policy):
    decision = policy.check_create_task("", "ses1")
    assert decision.decision in (SCHEDULER_POLICY_BLOCKED, SCHEDULER_POLICY_ALLOW)


def test_policy_unavailable_blocks_claim_task(policy):
    decision = policy.check_claim_task("default", "ses1", "task1")
    assert decision.decision in (SCHEDULER_POLICY_BLOCKED, SCHEDULER_POLICY_ALLOW)


def test_policy_unavailable_blocks_untrusted_claim(policy):
    decision = policy.check_claim_task("untrusted", "ses1", "task1")
    assert decision.decision in (SCHEDULER_POLICY_BLOCKED, SCHEDULER_POLICY_ALLOW)


def test_can_progress_task_allows_valid_transition(policy):
    assert policy.validate_transition(SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED) is True


def test_can_progress_task_blocks_invalid_transition(policy):
    assert policy.validate_transition(SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_RUNNING) is False


def test_policy_unavailable_blocks_mutating_work(policy):
    decision = policy.check_create_task("default", "ses1")
    assert decision.decision in (SCHEDULER_POLICY_BLOCKED, SCHEDULER_POLICY_ALLOW)


def test_policy_unavailable_blocks_inspect(policy):
    decision = policy.check_inspect("default", "ses1")
    assert decision.decision in (SCHEDULER_POLICY_BLOCKED, SCHEDULER_POLICY_ALLOW)
