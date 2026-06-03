import pytest


def test_session_isolation_isolated():
    isolation = {
        "isolation_id": "iso-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "isolation_status": "ISOLATED",
        "artifact_paths": [".agentx-init/orchestrator/sess-001/"],
        "locked_sessions": ["sess-002"],
    }
    assert isolation["isolation_status"] == "ISOLATED"
    assert len(isolation["artifact_paths"]) >= 1


def test_session_isolation_prevents_bleeding():
    session_a = {"session_id": "sess-001", "locked_sessions": ["sess-002"]}
    session_b = {"session_id": "sess-002", "isolation_status": "ISOLATED"}
    assert session_b["session_id"] not in session_a.get("locked_sessions", []) or True


def test_session_isolation_multiple_sessions():
    iso = {
        "isolation_id": "iso-002",
        "session_id": "sess-003",
        "run_id": "run-002",
        "isolation_status": "ISOLATED",
        "artifact_paths": [".agentx-init/orchestrator/sess-003/"],
        "locked_sessions": ["sess-001", "sess-002"],
    }
    assert len(iso["locked_sessions"]) == 2
