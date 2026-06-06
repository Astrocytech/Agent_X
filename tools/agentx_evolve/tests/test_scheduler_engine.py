import pytest
import tempfile
from pathlib import Path

from agentx_evolve.scheduler.scheduler_engine import SchedulerEngine
from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_BLOCKED,
)


@pytest.fixture
def engine():
    with tempfile.TemporaryDirectory() as tmp:
        eng = SchedulerEngine(Path(tmp))
        yield eng


def test_create_session(engine):
    s = engine.create_session("ses1")
    assert s.session_id == "ses1"


def test_get_session(engine):
    engine.create_session("ses1")
    s = engine.get_session("ses1")
    assert s is not None
    assert s.session_id == "ses1"


def test_get_session_nonexistent(engine):
    s = engine.get_session("nonexistent")
    assert s is None


def test_get_active_sessions(engine):
    engine.create_session("ses1")
    engine.create_session("ses2")
    active = engine.get_active_sessions()
    assert len(active) == 2


def test_close_session(engine):
    engine.create_session("ses1")
    result = engine.close_session("ses1")
    assert result["status"] == "SESSION_CLOSED"


def test_heartbeat_session(engine):
    engine.create_session("ses1")
    result = engine.heartbeat_session("ses1")
    assert result["status"] == "HEARTBEAT_RECORDED"


def test_get_task_nonexistent(engine):
    t = engine.get_task("nonexistent")
    assert t is None


def test_claim_next_no_tasks(engine):
    engine.create_session("ses1")
    result = engine.claim_next("ses1")
    assert result is None


def test_claim_next_with_task(engine):
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
    disp = SchedulerDispatcher(str(engine.runtime_root))
    disp.create_task("task1", "ses1", payload_ref="payload1")
    claim = engine.claim_next("ses1")
    assert claim is not None
    assert claim["task_id"] == "task1"


def test_progress_task(engine):
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
    disp = SchedulerDispatcher(str(engine.runtime_root))
    disp.create_task("task1", "ses1")
    claim = engine.claim_next("ses1")
    result = engine.progress_task("task1", "ses1", SCHEDULER_STATUS_RUNNING)
    assert result["status"] == "PROGRESSED"


def test_invalid_transition(engine):
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
    disp = SchedulerDispatcher(str(engine.runtime_root))
    disp.create_task("task1", "ses1")
    result = engine.progress_task("task1", "ses1", SCHEDULER_STATUS_COMPLETED)
    assert result["status"] == "INVALID_TRANSITION"


def test_dependencies_not_satisfied(engine):
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
    disp = SchedulerDispatcher(str(engine.runtime_root))
    disp.create_task("task1", "ses1", dependency_ids=["task0"])
    claim = engine.claim_next("ses1")
    assert claim is None


def test_dependencies_satisfied(engine):
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
    disp = SchedulerDispatcher(str(engine.runtime_root))
    disp.create_task("task0", "ses1")
    engine.progress_task("task0", "ses1", SCHEDULER_STATUS_COMPLETED)
    disp.create_task("task1", "ses1", dependency_ids=["task0"])
    claim = engine.claim_next("ses1")
    assert claim is not None


def test_get_queue_state(engine):
    state = engine.get_queue_state()
    assert "total_tasks" in state
    assert state["total_tasks"] == 0


def test_run_recovery_pass(engine):
    result = engine.run_recovery_pass()
    assert "recovered_sessions" in result
    assert "expired_leases" in result


def test_claim_and_complete_cycle(engine):
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
    disp = SchedulerDispatcher(str(engine.runtime_root))
    disp.create_task("task1", "ses1")
    claim = engine.claim_next("ses1")
    assert claim is not None
    engine.progress_task("task1", "ses1", SCHEDULER_STATUS_RUNNING)
    engine.progress_task("task1", "ses1", SCHEDULER_STATUS_COMPLETED)
    task = engine.get_task("task1")
    assert task.status == SCHEDULER_STATUS_COMPLETED
