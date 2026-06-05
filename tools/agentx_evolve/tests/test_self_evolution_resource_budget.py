import pytest


def test_resource_budget_defaults():
    budget = {
        "budget_id": "budget-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "max_steps": 100,
        "max_retries_total": 10,
        "max_retries_per_step": 3,
        "max_tool_calls": 50,
        "max_model_calls": 20,
        "max_run_seconds": 3600,
        "steps_used": 0,
        "retries_used": 0,
        "tool_calls_used": 0,
        "model_calls_used": 0,
        "time_elapsed_seconds": 0.0,
        "status": "ACTIVE",
    }
    assert budget["status"] == "ACTIVE"
    assert budget["max_steps"] == 100


def test_resource_budget_exceeded():
    budget = {
        "budget_id": "budget-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "max_steps": 10,
        "max_retries_total": 10,
        "max_retries_per_step": 3,
        "max_tool_calls": 50,
        "max_model_calls": 20,
        "max_run_seconds": 3600,
        "steps_used": 10,
        "retries_used": 5,
        "tool_calls_used": 50,
        "model_calls_used": 20,
        "time_elapsed_seconds": 100.0,
        "status": "EXCEEDED",
    }
    assert budget["steps_used"] <= budget["max_steps"] or budget["status"] == "EXCEEDED"


def test_resource_budget_exceed_status():
    budget = {
        "budget_id": "budget-002",
        "session_id": "sess-001",
        "run_id": "run-001",
        "max_steps": 10,
        "steps_used": 11,
        "status": "EXCEEDED",
    }
    assert budget["steps_used"] > budget["max_steps"]
    assert budget["status"] == "EXCEEDED"
