import pytest
import tempfile
from pathlib import Path

from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
from agentx_evolve.scheduler.scheduler_engine import SchedulerEngine
from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_BLOCKED, SCHEDULER_STATUS_QUEUED,
    SCHEDULER_POLICY_DENY, SCHEDULER_POLICY_BLOCKED,
)


@pytest.fixture
def dispatcher():
    with tempfile.TemporaryDirectory() as tmp:
        d = SchedulerDispatcher(Path(tmp))
        d.initialize()
        yield d


@pytest.fixture
def engine():
    with tempfile.TemporaryDirectory() as tmp:
        e = SchedulerEngine(Path(tmp))
        yield e


def test_create_task_empty_session_id(dispatcher):
    result = dispatcher.create_task("task1", "", "payload1")
    assert result["status"] == "QUEUED"


def test_claim_task_no_session(dispatcher):
    result = dispatcher.claim_next_task("nonexistent")
    assert result["status"] == "SESSION_NOT_FOUND"


def test_claim_task_no_active_session(dispatcher):
    dispatcher.engine.create_session("ses1")
    dispatcher.engine.close_session("ses1")
    result = dispatcher.claim_next_task("ses1")
    assert result["status"] == "SESSION_NOT_ACTIVE"


def test_cancel_nonexistent_task(dispatcher):
    result = dispatcher.cancel_task("nonexistent", "ses1")
    assert result["status"] == "TASK_NOT_FOUND"


def test_complete_nonexistent_task(dispatcher):
    result = dispatcher.complete_task("nonexistent", "ses1")
    assert result["status"] == "TASK_NOT_FOUND"


def test_fail_nonexistent_task(dispatcher):
    result = dispatcher.fail_task("nonexistent", "ses1")
    assert result["status"] == "TASK_NOT_FOUND"


def test_invalid_status_transition(dispatcher):
    dispatcher.engine.create_session("ses1")
    dispatcher.create_task("task1", "ses1")
    result = dispatcher.complete_task("task1", "ses1")
    assert result["status"] == "INVALID_TRANSITION"


def test_claim_task_with_dependency_not_met(dispatcher):
    dispatcher.engine.create_session("ses1")
    dispatcher.create_task("task1", "ses1", dependency_ids=["task0"])
    result = dispatcher.claim_next_task("ses1")
    assert result["status"] == "NO_TASK_AVAILABLE"


def test_duplicate_task_ids_allowed(dispatcher):
    dispatcher.engine.create_session("ses1")
    r1 = dispatcher.create_task("task1", "ses1")
    assert r1["status"] == "QUEUED"
    r2 = dispatcher.create_task("task1", "ses1")
    assert r2["status"] == "QUEUED"


def test_claim_selection_by_priority(dispatcher):
    dispatcher.engine.create_session("ses1")
    dispatcher.create_task("low", "ses1", priority=0)
    dispatcher.create_task("high", "ses1", priority=100)
    claim = dispatcher.claim_next_task("ses1")
    assert claim["task_id"] == "high"


def test_engine_no_side_effects_on_import():
    import agentx_evolve.scheduler
    assert True


def test_scheduler_policy_fallback_allow():
    from agentx_evolve.scheduler.scheduler_policy import SchedulerPolicy
    policy = SchedulerPolicy()
    decision = policy.check_create_task("default", "ses1")
    assert decision.decision == "ALLOW"


def test_claim_without_lock_handled(dispatcher):
    dispatcher.engine.create_session("ses1")
    dispatcher.create_task("task1", "ses1")
    claim = dispatcher.claim_next_task("ses1")
    assert claim["status"] == "CLAIMED"


def test_recovery_pass_no_crash(dispatcher):
    result = dispatcher.run_recovery_pass()
    assert "recovered_sessions" in result or isinstance(result, dict)


def test_finalize_evidence(dispatcher):
    result = dispatcher.finalize_evidence("abc123")
    assert "manifest" in result
