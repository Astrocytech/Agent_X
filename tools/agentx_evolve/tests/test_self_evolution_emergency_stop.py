import pytest


def test_emergency_stop_record():
    stop_event = {
        "event_id": "stop-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "stop_type": "EMERGENCY_STOP",
        "triggered_by": "human_operator",
        "reason": "Unsafe mutation detected",
    }
    assert stop_event["stop_type"] == "EMERGENCY_STOP"
    assert stop_event["triggered_by"] == "human_operator"


def test_cancel_event():
    stop_event = {
        "event_id": "stop-002",
        "session_id": "sess-001",
        "run_id": "run-001",
        "stop_type": "CANCEL",
        "triggered_by": "governance_gate",
        "reason": "Policy violation",
    }
    assert stop_event["stop_type"] == "CANCEL"


def test_pause_event():
    stop_event = {
        "event_id": "stop-003",
        "session_id": "sess-001",
        "run_id": "run-001",
        "stop_type": "PAUSE",
        "triggered_by": "human_review",
        "reason": "Needs manual review",
    }
    assert stop_event["stop_type"] == "PAUSE"
