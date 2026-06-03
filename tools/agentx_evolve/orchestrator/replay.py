from __future__ import annotations

import json as _json
from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_models import (
    ExecutionStep,
    TaskPlan,
    OrchestrationState,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT
from agentx_evolve.orchestrator.orchestrator_logger import append_evidence_event
from agentx_evolve.orchestrator.session_manager import load_orchestration_session
from agentx_evolve.orchestrator.orchestrator_state import load_state_snapshot
from agentx_evolve.orchestrator.execution_planner import build_execution_steps, order_execution_steps
from agentx_evolve.orchestrator.run_ledger import load_run_ledger


def replay_plan(run_id: str, repo_root: Path) -> dict:
    session = load_orchestration_session(run_id, repo_root)
    if session is None:
        return {"status": "NOT_FOUND", "message": f"No session for run_id: {run_id}"}

    state = load_state_snapshot(run_id, repo_root)
    ledger = load_run_ledger(run_id, repo_root)

    replay = {
        "replay_id": new_id("replay"),
        "created_at": utc_now_iso(),
        "run_id": run_id,
        "session_status": session.session_status if session else "unknown",
        "final_state": state.current_state if state else "unknown",
        "ledger_decision": ledger.final_decision if ledger else "unknown",
        "ledger_summary": {
            "steps_total": ledger.steps_total if ledger else 0,
            "steps_completed": ledger.steps_completed if ledger else 0,
            "steps_failed": ledger.steps_failed if ledger else 0,
            "steps_blocked": ledger.steps_blocked if ledger else 0,
        } if ledger else {},
        "replay_source": "state_snapshot",
    }
    return replay


def replay_dry_run(
    run_id: str,
    plan: TaskPlan,
    repo_root: Path,
) -> dict:
    steps = build_execution_steps(plan)
    steps = order_execution_steps(steps)

    replay_steps: list[dict] = []
    for step in steps:
        replay_steps.append({
            "step_index": step.step_index,
            "step_name": step.step_name,
            "step_type": step.step_type,
            "assigned_role": step.assigned_role,
            "simulated_status": "SIMULATED",
            "deterministic": True,
        })

    result = {
        "replay_id": new_id("replay"),
        "created_at": utc_now_iso(),
        "run_id": run_id,
        "replay_type": "dry_run",
        "plan_id": plan.plan_id,
        "plan_hash": plan.plan_hash,
        "steps_simulated": len(replay_steps),
        "steps": replay_steps,
    }
    return result


def compare_replay(
    run_id: str,
    original_result: dict,
    replay_result: dict,
) -> dict:
    original_status = original_result.get("status", "")
    replay_status = replay_result.get("status", "SIMULATED")
    original_steps = original_result.get("steps_total", 0)
    replay_steps = replay_result.get("steps_simulated", 0)

    mismatches: list[str] = []
    if original_status != "DONE":
        mismatches.append(f"Original run was not DONE ({original_status})")
    if original_steps != replay_steps:
        mismatches.append(
            f"Step count mismatch: original={original_steps}, replay={replay_steps}"
        )

    comparison_id = new_id("cmp")
    comparison = {
        "comparison_id": comparison_id,
        "created_at": utc_now_iso(),
        "run_id": run_id,
        "original_status": original_status,
        "replay_status": replay_status,
        "original_steps_total": original_steps,
        "replay_steps_simulated": replay_steps,
        "mismatches": mismatches,
        "match": len(mismatches) == 0,
    }
    return comparison
