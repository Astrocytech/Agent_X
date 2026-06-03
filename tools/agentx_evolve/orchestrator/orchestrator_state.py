from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationState,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED,
    ORCH_TRANSITIONS,
    ORCH_TERMINAL_STATUSES,
    RUNTIME_ARTIFACT_ROOT,
)
from agentx_evolve.orchestrator.orchestrator_errors import (
    ORCH_INVALID_STATE_TRANSITION,
    ORCH_TERMINAL_STATE_IMMUTABLE,
)


def can_transition(current_state: str, target_state: str) -> bool:
    allowed = ORCH_TRANSITIONS.get(current_state, [])
    return target_state in allowed


def is_terminal(state: str) -> bool:
    return state in ORCH_TERMINAL_STATUSES


def transition_state(
    current: OrchestrationState,
    target_state: str,
    reason: str = "",
) -> OrchestrationState:
    if is_terminal(current.current_state):
        raise ValueError(
            f"Cannot transition from terminal state {current.current_state}: {ORCH_TERMINAL_STATE_IMMUTABLE}"
        )
    if not can_transition(current.current_state, target_state):
        raise ValueError(
            f"Invalid transition from {current.current_state} to {target_state}: {ORCH_INVALID_STATE_TRANSITION}"
        )

    old_state = current.current_state
    current.previous_state = old_state
    current.current_state = target_state
    current.terminal = is_terminal(target_state)
    current.reason = reason
    current.state_version = current.state_version + 1
    current.updated_at = utc_now_iso()
    return current


def create_initial_state(
    session_id: str,
    run_id: str,
) -> OrchestrationState:
    return OrchestrationState(
        state_id=new_id("st"),
        session_id=session_id,
        run_id=run_id,
        created_at=utc_now_iso(),
        updated_at=utc_now_iso(),
        previous_state="",
        current_state=ORCH_STATUS_CREATED,
        terminal=False,
        reason="Session created",
        state_version=1,
    )


def write_state_snapshot(
    state: OrchestrationState,
    repo_root: Path,
) -> dict:
    artifact_dir = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / state.run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / "orchestration_state.json"
    data = state.to_dict()
    path.write_text(json_dumps(data))
    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    latest_path = latest_dir / "latest_orchestration_state.json"
    latest_path.write_text(json_dumps(data))
    return {"path": str(path), "sha256": sha256_dict(data)}


def load_state_snapshot(
    run_id: str,
    repo_root: Path,
) -> OrchestrationState | None:
    path = (
        repo_root
        / RUNTIME_ARTIFACT_ROOT
        / "runs"
        / run_id
        / "orchestration_state.json"
    )
    if not path.exists():
        return None
    import json as _json

    data = _json.loads(path.read_text())
    return OrchestrationState(**data)


def json_dumps(data: dict) -> str:
    import json as _json

    return _json.dumps(data, indent=2, sort_keys=True, default=str)
