import pytest
from pathlib import Path
from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher, dispatch_task


def test_dispatcher_routes_tasks(tmp_path):
    dispatcher = SchedulerDispatcher(str(tmp_path))
    dispatcher.initialize()
    result = dispatcher.create_task("task-1", "session-1", payload_ref="payload-1")
    assert result["status"] in ("QUEUED", "BLOCKED")
    if result["status"] == "QUEUED":
        assert result["task_id"] == "task-1"


def test_dispatch_task_function(tmp_path):
    dispatcher = SchedulerDispatcher(str(tmp_path))
    dispatcher.initialize()
    result = dispatch_task(dispatcher, "task-2", "session-1")
    assert result["status"] in ("QUEUED", "BLOCKED")
    if result["status"] == "QUEUED":
        assert result["task_id"] == "task-2"


def test_dispatcher_get_queue_state(tmp_path):
    dispatcher = SchedulerDispatcher(str(tmp_path))
    dispatcher.initialize()
    state = dispatcher.get_queue_state()
    assert "total_tasks" in state


def test_dispatcher_initialize(tmp_path):
    dispatcher = SchedulerDispatcher(str(tmp_path))
    result = dispatcher.initialize()
    assert result["status"] == "initialized"


def test_dispatcher_claim_no_task(tmp_path):
    dispatcher = SchedulerDispatcher(str(tmp_path))
    dispatcher.initialize()
    result = dispatcher.claim_next_task("nonexistent")
    assert result["status"] == "SESSION_NOT_FOUND"
