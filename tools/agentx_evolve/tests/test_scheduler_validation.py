import pytest

from agentx_evolve.scheduler.scheduler_validation import (
    validate_task_record,
    validate_session_record,
    validate_scheduler_event,
    validate_scheduler_config,
    validate_status_transition,
)
from agentx_evolve.scheduler.scheduler_models import (
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_RUNNING,
    SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_BLOCKED,
    SCHEDULER_STATUS_CLAIMED,
)


def test_validate_task_record_valid():
    data = {
        "record_id": "r1",
        "task_id": "t1",
        "session_id": "s1",
        "status": "QUEUED",
        "priority": 50,
    }
    errors = validate_task_record(data)
    assert errors == []


def test_validate_task_record_invalid_status():
    data = {
        "record_id": "r1",
        "task_id": "t1",
        "session_id": "s1",
        "status": "INVALID_STATUS",
        "priority": 50,
    }
    errors = validate_task_record(data)
    assert len(errors) > 0


def test_validate_task_record_missing_field():
    data = {"task_id": "t1"}
    errors = validate_task_record(data)
    assert len(errors) > 0


def test_validate_session_record_valid():
    data = {"record_id": "sr1", "session_id": "ses1", "status": "ACTIVE"}
    errors = validate_session_record(data)
    assert errors == []


def test_validate_session_record_invalid_status():
    data = {"record_id": "sr1", "session_id": "ses1", "status": "INVALID"}
    errors = validate_session_record(data)
    assert len(errors) > 0


def test_validate_scheduler_event_valid():
    data = {"event_id": "e1", "event_type": "TASK_QUEUED", "timestamp": "2024-01-01T00:00:00.000000Z"}
    errors = validate_scheduler_event(data)
    assert errors == []


def test_validate_scheduler_event_missing():
    data = {}
    errors = validate_scheduler_event(data)
    assert len(errors) > 0


def test_validate_scheduler_config_valid():
    data = {"lease_duration_seconds": 300, "max_retries_default": 3}
    errors = validate_scheduler_config(data)
    assert errors == []


def test_validate_scheduler_config_invalid():
    data = {"lease_duration_seconds": -1}
    errors = validate_scheduler_config(data)
    assert len(errors) > 0


def test_validate_status_transition_valid():
    errors = validate_status_transition(SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED)
    assert errors == []


def test_validate_status_transition_invalid():
    errors = validate_status_transition(SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_RUNNING)
    assert len(errors) > 0


def test_validate_status_transition_blocked_to_queued():
    errors = validate_status_transition(SCHEDULER_STATUS_BLOCKED, SCHEDULER_STATUS_QUEUED)
    assert errors == []
