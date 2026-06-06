import json
import pytest
import tempfile
from pathlib import Path

from agentx_evolve.scheduler.scheduler_observability import SchedulerObservability
from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_EVENT_QUEUED, SCHEDULER_EVENT_CLAIMED,
    SCHEDULER_EVENT_COMPLETED, SCHEDULER_EVENT_FAILED,
)


@pytest.fixture
def observability():
    with tempfile.TemporaryDirectory() as tmp:
        obs = SchedulerObservability(Path(tmp))
        yield obs


def test_record_event(observability):
    result = observability.record_event(
        event_type=SCHEDULER_EVENT_QUEUED,
        task_id="task1",
        session_id="ses1",
    )
    assert "event_id" in result
    assert result["event_type"] == SCHEDULER_EVENT_QUEUED


def test_record_event_persists(observability):
    observability.record_event(event_type=SCHEDULER_EVENT_QUEUED, task_id="task1")
    log_path = observability._log_path
    assert log_path.exists()
    with open(log_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
    data = json.loads(line)
    assert data["event_type"] == SCHEDULER_EVENT_QUEUED


def test_write_summary(observability):
    result = observability.write_summary({"total_tasks": 5}, 2)
    assert result["status"] == "summary_written"


def test_write_health(observability):
    result = observability.write_health(status="PASS", checks={"queue": "PASS"})
    assert result["status"] == "health_written"
