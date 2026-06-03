import json
from typing import Any

from .scheduler_models import (
    SCHEDULER_STATUS_VALUES,
    SCHEDULER_SESSION_STATUS_VALUES,
    SCHEDULER_CLAIM_STATUS_VALUES,
    SCHEDULER_LEASE_STATUS_VALUES,
    SCHEDULER_LOCK_STATUS_VALUES,
    SCHEDULER_VALID_TRANSITIONS,
    TASK_PRIORITY_LOW, TASK_PRIORITY_MEDIUM, TASK_PRIORITY_HIGH,
    TASK_PRIORITY_CRITICAL,
    TaskRecord, SessionRecord, SchedulerEvent,
)


def validate_task_record(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        errors.append("task_record must be a dict")
        return errors
    required = ["record_id", "task_id", "session_id", "status", "priority"]
    for field in required:
        if field not in data:
            errors.append(f"missing required field: {field}")
    if "status" in data and data["status"] not in SCHEDULER_STATUS_VALUES:
        errors.append(f"invalid status: {data.get('status')}")
    if "priority" in data and not isinstance(data["priority"], int):
        errors.append("priority must be an integer")
    if "record_id" in data and not isinstance(data["record_id"], str):
        errors.append("record_id must be a string")
    return errors


def validate_session_record(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        errors.append("session_record must be a dict")
        return errors
    required = ["record_id", "session_id", "status"]
    for field in required:
        if field not in data:
            errors.append(f"missing required field: {field}")
    if "status" in data and data["status"] not in SCHEDULER_SESSION_STATUS_VALUES:
        errors.append(f"invalid session status: {data.get('status')}")
    return errors


def validate_scheduler_event(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        errors.append("scheduler_event must be a dict")
        return errors
    required = ["event_id", "event_type", "timestamp"]
    for field in required:
        if field not in data:
            errors.append(f"missing required field: {field}")
    return errors


def validate_scheduler_config(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        errors.append("scheduler_config must be a dict")
        return errors
    if "lease_duration_seconds" in data:
        if not isinstance(data["lease_duration_seconds"], (int, float)):
            errors.append("lease_duration_seconds must be numeric")
        elif data["lease_duration_seconds"] <= 0:
            errors.append("lease_duration_seconds must be positive")
    if "max_retries_default" in data:
        if not isinstance(data["max_retries_default"], int):
            errors.append("max_retries_default must be an integer")
        elif data["max_retries_default"] < 0:
            errors.append("max_retries_default must be non-negative")
    return errors


def validate_status_transition(current: str, requested: str) -> list[str]:
    errors = []
    if current not in SCHEDULER_STATUS_VALUES:
        errors.append(f"invalid current status: {current}")
        return errors
    if requested not in SCHEDULER_STATUS_VALUES:
        errors.append(f"invalid requested status: {requested}")
        return errors
    allowed = SCHEDULER_VALID_TRANSITIONS.get(current, [])
    if requested not in allowed:
        errors.append(f"transition from {current} to {requested} not allowed")
    return errors
