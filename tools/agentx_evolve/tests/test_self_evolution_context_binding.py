import pytest


def test_context_binding_created():
    binding = {
        "binding_id": "cb-001",
        "step_id": "step-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "context_package_id": "ctx-001",
        "context_package_version": "1.0",
    }
    assert binding["context_package_id"] == "ctx-001"
    assert binding["context_package_version"] == "1.0"
