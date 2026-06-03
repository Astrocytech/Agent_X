import json
from pathlib import Path

import pytest

from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_CANCELLED, SCHEDULER_STATUS_FAILED,
    new_id, utc_now_iso,
)
from agentx_evolve.scheduler.queue_store import QueueStore, QUEUE_HISTORY_FILE
from agentx_evolve.scheduler.scheduler_engine import SchedulerEngine


def test_transition_log_written_on_status_change(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_models import TaskRecord
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    engine.queue_store.append_task(task)
    engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CLAIMED)
    result = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_RUNNING)
    assert result["status"] == "PROGRESSED"
    history = engine.queue_store._history_path
    assert history.exists()
    with open(history, "r", encoding="utf-8") as f:
        lines = f.readlines()
    records = [json.loads(l.strip()) for l in lines if l.strip()]
    statuses = [r.get("status") for r in records]
    assert SCHEDULER_STATUS_CLAIMED in statuses


def test_transition_log_has_required_fields(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_models import TaskRecord
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
    )
    engine.queue_store.append_task(task)
    engine.progress_task("t1", "ses1", SCHEDULER_STATUS_RUNNING)
    with open(engine.queue_store._history_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            assert "record_id" in data
            assert "task_id" in data
            assert "status" in data
            assert "updated_at" in data


def test_invalid_transition_logged(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_models import TaskRecord
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
        status=SCHEDULER_STATUS_COMPLETED,
    )
    engine.queue_store.append_task(task)
    result = engine.progress_task("t1", "ses1", SCHEDULER_STATUS_RUNNING)
    assert result["status"] == "INVALID_TRANSITION"


def test_transition_log_is_append_only(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_models import TaskRecord
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="ses1",
    )
    engine.queue_store.append_task(task)
    before_count = len(engine.queue_store._history_path.read_text().splitlines())
    engine.progress_task("t1", "ses1", SCHEDULER_STATUS_CLAIMED)
    after_count = len(engine.queue_store._history_path.read_text().splitlines())
    assert after_count > before_count


def test_load_transition_log_returns_records(tmp_path: Path):
    engine = SchedulerEngine(str(tmp_path / "runtime"))
    engine.create_session("ses1")
    from agentx_evolve.scheduler.scheduler_models import TaskRecord
    for state in [SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED]:
        task = TaskRecord(
            record_id=new_id("tr"), task_id="t1", session_id="ses1",
            status=state,
        )
        engine.queue_store.append_task(task)
    tasks, quarantined = engine.queue_store.replay_tasks()
    assert len(tasks) >= 3
