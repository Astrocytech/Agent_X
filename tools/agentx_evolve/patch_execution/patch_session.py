from __future__ import annotations

import json
from pathlib import Path

from agentx_evolve.patch_execution.patch_evidence import (
    append_implementation_history,
    write_latest_artifact,
)
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    new_id,
    to_dict,
    utc_now_iso,
)

from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat


_IMPLEMENTATION_SUBDIR = ".agentx-init/implementation"
_SESSIONS_SUBDIR = "sessions"
_LATEST_FILE = "latest_implementation_session.json"
_HISTORY_FILE = "implementation_history.jsonl"


def _lifecycle_state_from_status(status: str) -> str:
    mapping = {
        "SESSION_INITIALIZED": "PENDING_INIT",
        "DRY_RUNNING": "DRY_RUN",
        "DRY_RUN_READY": "DRY_RUN_READY",
        "LIVE_APPROVED": "LIVE_APPROVED",
        "PATCH_RUNNING": "PATCH_APPLYING",
        "PATCH_APPLIED": "PATCH_APPLIED",
        "ROLLBACK_RUNNING": "ROLLBACK_RUNNING",
        "ROLLED_BACK": "ROLLED_BACK",
        "VALIDATION_RUNNING": "VALIDATION_RUNNING",
        "VALIDATION_PASSED": "VALIDATION_PASSED",
        "VALIDATION_FAILED": "VALIDATION_FAILED",
        "ACCEPTED": "ACCEPTED",
        "FINALIZED": "FINALIZED",
        "FAILED": "FAILED",
        "BLOCKED": "BLOCKED",
    }
    return mapping.get(status, "UNKNOWN")


def _ensure_implementation_dirs(repo_root: Path) -> Path:
    base = repo_root / _IMPLEMENTATION_SUBDIR
    sessions = base / _SESSIONS_SUBDIR
    base.mkdir(parents=True, exist_ok=True)
    sessions.mkdir(parents=True, exist_ok=True)
    return base


def _atomic_write_json(data: dict, path: Path) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    tmp.rename(path)


def _append_jsonl(data: dict, path: Path) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, default=str) + "\n")


def _write_session_files(
    session: ImplementationSession,
    repo_root: Path,
) -> None:
    base = _ensure_implementation_dirs(repo_root)
    d = to_dict(session)
    session_path = base / _SESSIONS_SUBDIR / f"{session.session_id}.json"
    latest_path = base / _LATEST_FILE
    history_path = base / _HISTORY_FILE
    _atomic_write_json(d, session_path)
    _atomic_write_json(d, latest_path)
    _append_jsonl(d, history_path)
    write_latest_artifact("implementation_session", d, repo_root)
    append_implementation_history(session, repo_root)


def create_implementation_session(
    repo_root: Path,
    target_paths: list[str],
    proposal_id: str | None = None,
    governance_decision_id: str | None = None,
    policy_decision_id: str | None = None,
    compat: InitiatorPatchCompat | None = None,
) -> ImplementationSession:
    if not target_paths:
        raise ValueError("target_paths must not be empty")

    session = ImplementationSession(
        session_id=new_id("IMP"),
        proposal_id=proposal_id,
        governance_decision_id=governance_decision_id,
        policy_decision_id=policy_decision_id,
        target_paths=target_paths,
        lifecycle_state="PENDING_INIT",
        timestamp="",
    )

    return update_implementation_session(
        session=session,
        repo_root=repo_root,
        status="SESSION_INITIALIZED",
    )


def update_implementation_session(
    session: ImplementationSession,
    repo_root: Path,
    status: str,
    final_decision: str | None = None,
    changed_paths: list[str] | None = None,
    rollback_snapshot_id: str | None = None,
    patch_application_id: str | None = None,
    source_change_guard_id: str | None = None,
    validation_result_id: str | None = None,
    rollback_record_id: str | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    compat: InitiatorPatchCompat | None = None,
) -> ImplementationSession:
    session.status = status
    session.timestamp = utc_now_iso()
    session.lifecycle_state = _lifecycle_state_from_status(status)

    if final_decision is not None:
        session.final_decision = final_decision
    if changed_paths is not None:
        session.changed_paths = changed_paths
    if rollback_snapshot_id is not None:
        session.rollback_snapshot_id = rollback_snapshot_id
    if patch_application_id is not None:
        session.patch_application_id = patch_application_id
    if source_change_guard_id is not None:
        session.source_change_guard_id = source_change_guard_id
    if validation_result_id is not None:
        session.validation_result_id = validation_result_id
    if rollback_record_id is not None:
        session.rollback_record_id = rollback_record_id
    if warnings is not None:
        session.warnings = warnings
    if errors is not None:
        session.errors = errors

    _write_session_files(session, repo_root)
    return session
