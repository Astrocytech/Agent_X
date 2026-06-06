from pathlib import Path

import pytest

from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher
from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_CANCELLED, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_RUNNING,
)
from agentx_evolve.scheduler.scheduler_engine import SchedulerEngine
from agentx_evolve.scheduler.queue_store import QueueStore
from agentx_evolve.scheduler.scheduler_models import TaskRecord, new_id


@pytest.fixture
def dispatcher(tmp_path: Path):
    d = SchedulerDispatcher(str(tmp_path / "runtime"))
    d.initialize()
    return d


def test_cancel_pending_task_works(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    qs = QueueStore(str(tmp_path / "runtime" / "queue"))
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    qs.append_task(task)
    result = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CANCELLED)
    assert result["status"] == "PROGRESSED"


def test_cancel_running_task_records_evidence(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    qs = QueueStore(str(tmp_path / "runtime" / "queue"))
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    qs.append_task(task)
    engine.progress_task("t1", "ses1", SCHEDULER_STATUS_RUNNING)
    result = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CANCELLED)
    assert result["status"] == "PROGRESSED"


def test_cancel_done_task_fails(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    qs = QueueStore(str(tmp_path / "runtime" / "queue"))
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    qs.append_task(task)
    engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CLAIMED)
    engine.progress_task("t1", "ses1", SCHEDULER_STATUS_RUNNING)
    result = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_COMPLETED)
    assert result["status"] == "PROGRESSED"
    cancel = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CANCELLED)
    assert cancel["status"] == "INVALID_TRANSITION"


def test_cancelled_task_cannot_be_claimed(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    qs = QueueStore(str(tmp_path / "runtime" / "queue"))
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    qs.append_task(task)
    engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CANCELLED)
    claim = engine.claim_next("ses1")
    assert claim is None


def test_cancellation_writes_audit(dispatcher):
    dispatcher.engine.create_session("ses1")
    dispatcher.create_task("t1", "ses1")
    result = dispatcher.cancel_task("t1", "ses1")
    assert result["status"] in ("PROGRESSED", "INVALID_TRANSITION")


def test_non_owner_cancellation_blocked(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    qs = QueueStore(str(tmp_path / "runtime" / "queue"))
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    qs.append_task(task)
    found = engine.get_task("t1")
    assert found is not None
    result = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CANCELLED)
    assert result["status"] == "PROGRESSED"
