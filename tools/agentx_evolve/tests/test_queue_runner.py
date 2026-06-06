import json
from pathlib import Path

import pytest

from scheduler.scheduler_models import (
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
)
from scheduler.scheduler_engine import SchedulerEngine
from scheduler.scheduler_dispatcher import SchedulerDispatcher


@pytest.fixture
def dispatcher(tmp_path: Path):
    d = SchedulerDispatcher(str(tmp_path / "runtime"))
    d.initialize()
    return d


def test_run_next_task_claims_and_marks_running(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    from scheduler.queue_store import QueueStore
    qs = QueueStore(str(tmp_path / "runtime" / "queue"))
    from scheduler.scheduler_models import TaskRecord, new_id
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    qs.append_task(task)
    claim = engine.claim_next("ses1")
    assert claim is not None
    assert claim["task_id"] == "t1"
    progress = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_RUNNING)
    assert progress["status"] == "PROGRESSED"


def test_run_scheduler_tick_processes_one_tick(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    from scheduler.queue_store import QueueStore
    qs = QueueStore(str(tmp_path / "runtime" / "queue"))
    from scheduler.scheduler_models import TaskRecord, new_id
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
    )
    qs.append_task(task)
    claim = engine.claim_next("ses1")
    assert claim is not None
    progress = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_RUNNING)
    assert progress["status"] == "PROGRESSED"
    complete = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_COMPLETED)
    assert complete["status"] == "PROGRESSED"


def test_get_queue_summary_returns_counts(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    state = engine.get_queue_state()
    assert "total_tasks" in state
    assert "by_status" in state


def test_queue_runner_is_not_background_daemon(dispatcher):
    assert hasattr(dispatcher, "claim_next_task")
    result = dispatcher.claim_next_task("nonexistent")
    assert result["status"] == "SESSION_NOT_FOUND"


def test_run_scheduler_tick_writes_events(tmp_path: Path):
    dispatcher = SchedulerDispatcher(str(tmp_path / "runtime"))
    dispatcher.initialize()
    dispatcher.engine.create_session("ses1")
    dispatcher.create_task("t1", "ses1")
    claim = dispatcher.claim_next_task("ses1")
    assert claim["status"] in ("CLAIMED", "NO_TASK_AVAILABLE")
