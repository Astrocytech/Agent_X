from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationSession,
    OrchestrationTask,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED,
    SESSION_STATUS_ACTIVE,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_CANCELLED,
    RUN_MODE_EXECUTE_CONTROLLED,
    RUNTIME_ARTIFACT_ROOT,
)


def create_orchestration_session(
    task: OrchestrationTask,
    context: dict,
    repo_root: Path,
) -> OrchestrationSession:
    run_id = new_id("run")
    session_id = new_id("sess")
    now = utc_now_iso()

    session = OrchestrationSession(
        session_id=session_id,
        run_id=run_id,
        created_at=now,
        updated_at=now,
        requested_task_id=task.task_id,
        requested_task_summary=task.description,
        initiating_role=context.get("initiating_role", "developer"),
        orchestration_mode=context.get("run_mode", RUN_MODE_EXECUTE_CONTROLLED),
        state=ORCH_STATUS_CREATED,
        session_status=SESSION_STATUS_ACTIVE,
        idempotency_key=context.get("idempotency_key", ""),
    )

    artifact_dir = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / "orchestration_session.json"
    data = session.to_dict()
    path.write_text(json_dumps(data))

    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    latest_path = latest_dir / "latest_orchestration_session.json"
    latest_path.write_text(json_dumps(data))

    return session


def load_orchestration_session(
    run_id: str,
    repo_root: Path,
) -> OrchestrationSession | None:
    path = (
        repo_root
        / RUNTIME_ARTIFACT_ROOT
        / "runs"
        / run_id
        / "orchestration_session.json"
    )
    if not path.exists():
        return None
    import json as _json

    data = _json.loads(path.read_text())
    return OrchestrationSession(**data)


def update_orchestration_session(
    session: OrchestrationSession,
    updates: dict,
    repo_root: Path,
) -> OrchestrationSession:
    for key, value in updates.items():
        if hasattr(session, key):
            setattr(session, key, value)
    session.updated_at = utc_now_iso()

    artifact_dir = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / session.run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / "orchestration_session.json"
    data = session.to_dict()
    path.write_text(json_dumps(data))

    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    latest_path = latest_dir / "latest_orchestration_session.json"
    latest_path.write_text(json_dumps(data))

    return session


def close_orchestration_session(
    session: OrchestrationSession,
    final_status: str,
    repo_root: Path,
) -> OrchestrationSession:
    valid_final = (SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED, SESSION_STATUS_CANCELLED)
    if final_status not in valid_final:
        raise ValueError(f"Invalid final session status: {final_status}")
    return update_orchestration_session(
        session,
        {"session_status": final_status, "state": final_status},
        repo_root,
    )


def resume_orchestration_session(
    run_id: str,
    repo_root: Path,
) -> OrchestrationSession | None:
    return load_orchestration_session(run_id, repo_root)


def json_dumps(data: dict) -> str:
    import json as _json
    return _json.dumps(data, indent=2, sort_keys=True, default=str)
