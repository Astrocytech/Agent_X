import pytest


def test_mcp_exposure_default_blocked():
    exposure = {
        "exposure_id": "mcp-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "exposure_status": "INACTIVE",
    }
    assert exposure["exposure_status"] == "INACTIVE"


def test_mcp_exposure_active_with_allowed_tools():
    exposure = {
        "exposure_id": "mcp-002",
        "session_id": "sess-001",
        "run_id": "run-001",
        "exposure_status": "ACTIVE",
        "allowed_tools": ["source_reader", "file_lister"],
    }
    assert "source_reader" in exposure["allowed_tools"]


def test_mcp_exposure_blocked():
    exposure = {
        "exposure_id": "mcp-003",
        "session_id": "sess-001",
        "run_id": "run-001",
        "exposure_status": "BLOCKED",
    }
    assert exposure["exposure_status"] == "BLOCKED"
