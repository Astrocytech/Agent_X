import json
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, to_dict,
)
from .task_queue import _queue_store, get_queue_state
from .session_store import SessionStore
from .lease_manager import LeaseManager


S_CREATED = "CREATED"
S_RUNNING = "RUNNING"
S_COMPLETED = "COMPLETED"

_SCHEDULER_STATE_TRANSITIONS = {
    S_CREATED: [S_RUNNING],
    S_RUNNING: [S_COMPLETED],
    S_COMPLETED: [],
}


class SchedulerState:
    def __init__(self, state: str = S_CREATED):
        self.state = state

    def transition_to(self, new_state: str) -> "SchedulerState":
        if new_state not in _SCHEDULER_STATE_TRANSITIONS.get(self.state, []):
            raise ValueError(f"Cannot transition from {self.state} to {new_state}")
        self.state = new_state
        return self


def migrate_state(current: str, target: str) -> str:
    allowed = _SCHEDULER_STATE_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise ValueError(f"Cannot migrate from {current} to {target}")
    return target


STATE_FILE = "scheduler_state.json"


def _state_path(repo_root: str | Path) -> Path:
    path = Path(repo_root) / ".agentx-init/scheduler"
    path.mkdir(parents=True, exist_ok=True)
    return path / STATE_FILE


def load_scheduler_state(repo_root: str | Path) -> dict | None:
    path = _state_path(repo_root)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_scheduler_state(state: dict, repo_root: str | Path) -> dict:
    path = _state_path(repo_root)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)
    tmp.replace(path)
    return {"path": str(path), "status": "written"}


def build_scheduler_state(repo_root: str | Path) -> dict:
    queue_state = get_queue_state(repo_root)
    session_dir = Path(repo_root) / ".agentx-init/scheduler/sessions"
    session_store = SessionStore(session_dir)
    effective_sessions = session_store.get_effective_sessions()
    lease_dir = Path(repo_root) / ".agentx-init/scheduler/leases"
    lease_mgr = LeaseManager(lease_dir)
    active_leases = lease_mgr._get_active_leases()

    state = {
        "queue_state": to_dict(queue_state),
        "sessions": {
            sid: to_dict(s) for sid, s in effective_sessions.items()
        },
        "active_leases": {
            tid: l for tid, l in active_leases.items()
        },
        "built_at": utc_now_iso(),
    }
    write_scheduler_state(state, repo_root)
    return state


def reset_scheduler_state(repo_root: str | Path) -> dict:
    path = _state_path(repo_root)
    if path.exists():
        path.unlink()
    state = {
        "queue_state": {},
        "sessions": {},
        "active_leases": {},
        "reset_at": utc_now_iso(),
    }
    write_scheduler_state(state, repo_root)
    return {"status": "reset", "path": str(path)}
