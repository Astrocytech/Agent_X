import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.replay import (
    replay_plan,
    replay_dry_run,
    compare_replay,
)
from agentx_evolve.orchestrator.orchestrator_models import TaskPlan, ExecutionStep
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def test_replay_plan_not_found():
    result = replay_plan("no-such-run", Path("/tmp"))
    assert result["status"] == "NOT_FOUND"
    assert "No session" in result["message"]


def test_replay_plan_with_session(tmp_path):
    import json
    run_id = "run-replay-1"
    runs_dir = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / run_id
    runs_dir.mkdir(parents=True, exist_ok=True)
    session = {
        "session_id": "s-1",
        "run_id": run_id,
        "session_status": "COMPLETED",
        "state": "COMPLETED",
    }
    (runs_dir / "orchestration_session.json").write_text(json.dumps(session))
    state = {
        "state_id": "st-1",
        "run_id": run_id,
        "current_state": "COMPLETED",
    }
    (runs_dir / "orchestration_state.json").write_text(json.dumps(state))
    ledger = {
        "ledger_id": "l-1",
        "run_id": run_id,
        "final_decision": "COMPLETE",
        "steps_total": 3,
        "steps_completed": 3,
        "steps_failed": 0,
        "steps_blocked": 0,
    }
    (runs_dir / "run_ledger.json").write_text(json.dumps(ledger))

    result = replay_plan(run_id, tmp_path)
    assert result.get("status") != "NOT_FOUND"
    assert result["run_id"] == run_id
    assert result["replay_id"].startswith("replay-")
    assert result["replay_source"] == "state_snapshot"


def test_replay_dry_run():
    plan = TaskPlan(
        plan_id="p-1",
        run_id="r-1",
        plan_hash="abc123",
        steps=[
            {"step_index": 0, "step_name": "validate", "step_type": "POLICY",
             "assigned_role": "orchestrator", "idempotency_key": "k1", "description": "d1"},
            {"step_index": 1, "step_name": "tool_call", "step_type": "TOOL",
             "assigned_role": "tool_agent", "idempotency_key": "k2", "description": "d2"},
        ],
    )
    result = replay_dry_run("r-1", plan, Path("/tmp"))
    assert result["replay_id"].startswith("replay-")
    assert result["replay_type"] == "dry_run"
    assert result["plan_id"] == "p-1"
    assert result["steps_simulated"] == 2
    assert len(result["steps"]) == 2


def test_replay_dry_run_simulated_status():
    plan = TaskPlan(
        plan_id="p-1",
        steps=[{"step_index": 0, "step_name": "test", "step_type": "POLICY",
                "assigned_role": "orchestrator", "idempotency_key": "k", "description": "d"}],
    )
    result = replay_dry_run("r-1", plan, Path("/tmp"))
    assert result["steps"][0]["simulated_status"] == "SIMULATED"
    assert result["steps"][0]["deterministic"] is True


def test_compare_replay_match():
    original = {"status": "DONE", "steps_total": 3}
    replay_result = {"status": "SIMULATED", "steps_simulated": 3}
    comparison = compare_replay("r-1", original, replay_result)
    assert comparison["match"] is True
    assert comparison["mismatches"] == []


def test_compare_replay_status_mismatch():
    original = {"status": "FAILED", "steps_total": 3}
    replay_result = {"status": "SIMULATED", "steps_simulated": 3}
    comparison = compare_replay("r-1", original, replay_result)
    assert comparison["match"] is False
    assert len(comparison["mismatches"]) >= 1
    assert "not DONE" in comparison["mismatches"][0]


def test_compare_replay_step_count_mismatch():
    original = {"status": "DONE", "steps_total": 5}
    replay_result = {"status": "SIMULATED", "steps_simulated": 3}
    comparison = compare_replay("r-1", original, replay_result)
    assert comparison["match"] is False
    assert any("Step count mismatch" in m for m in comparison["mismatches"])


def test_compare_replay_returns_comparison_id():
    comparison = compare_replay("r-1", {"status": "DONE", "steps_total": 1},
                                {"status": "SIMULATED", "steps_simulated": 1})
    assert comparison["comparison_id"].startswith("cmp-")
    assert comparison["run_id"] == "r-1"
