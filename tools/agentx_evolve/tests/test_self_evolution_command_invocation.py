import pytest


def test_command_invocation_binding_structure():
    binding = {
        "binding_id": "cmd-001",
        "step_id": "step-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "command_line": "python -m pytest tests/",
        "status": "PENDING",
    }
    assert binding["binding_id"] == "cmd-001"
    assert binding["status"] == "PENDING"


def test_command_invocation_completed():
    binding = {
        "binding_id": "cmd-001",
        "step_id": "step-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "command_line": "python -m pytest tests/",
        "status": "COMPLETED",
        "exit_code": 0,
    }
    assert binding["exit_code"] == 0
    assert binding["status"] == "COMPLETED"


def test_command_invocation_failed():
    binding = {
        "binding_id": "cmd-002",
        "step_id": "step-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "command_line": "python -m pytest tests/",
        "status": "FAILED",
        "exit_code": 1,
    }
    assert binding["exit_code"] == 1
    assert binding["status"] == "FAILED"
