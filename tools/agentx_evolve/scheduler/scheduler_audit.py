import json
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, to_dict,
    SchedulerAudit,
)


AUDIT_DIR = ".agentx-init/scheduler/audit"
AUDIT_HISTORY_FILE = "audit_history.jsonl"
LATEST_AUDIT_STATE_FILE = "latest_audit_state.json"


def _audit_dir(repo_root: str | Path) -> Path:
    path = Path(repo_root) / AUDIT_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _history_path(repo_root: str | Path) -> Path:
    return _audit_dir(repo_root) / AUDIT_HISTORY_FILE


def _latest_state_path(repo_root: str | Path) -> Path:
    return _audit_dir(repo_root) / LATEST_AUDIT_STATE_FILE


def append_audit_event(event: SchedulerAudit, repo_root: str | Path) -> dict:
    path = _history_path(repo_root)
    data = to_dict(event)
    line = json.dumps(data, sort_keys=True, default=str) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
    return {"audit_id": event.audit_id, "action": event.action, "status": "appended"}


def load_audit_history(repo_root: str | Path) -> list[SchedulerAudit]:
    path = _history_path(repo_root)
    if not path.exists():
        return []
    audits = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            audit = _dict_to_audit(data)
            if audit is not None:
                audits.append(audit)
    return audits


def write_latest_audit_state(repo_root: str | Path) -> dict:
    audits = load_audit_history(repo_root)
    state = {
        "total_audit_events": len(audits),
        "latest_timestamp": audits[-1].timestamp if audits else utc_now_iso(),
        "latest_action": audits[-1].action if audits else "",
        "by_action": _count_by_action(audits),
        "by_outcome": _count_by_outcome(audits),
        "snapshot_at": utc_now_iso(),
    }
    path = _latest_state_path(repo_root)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)
    tmp.replace(path)
    return {"path": str(path), "status": "written", "total_events": len(audits)}


def _count_by_action(audits: list[SchedulerAudit]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in audits:
        counts[a.action] = counts.get(a.action, 0) + 1
    return counts


def _count_by_outcome(audits: list[SchedulerAudit]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in audits:
        counts[a.outcome] = counts.get(a.outcome, 0) + 1
    return counts


def _dict_to_audit(data: dict) -> SchedulerAudit | None:
    try:
        return SchedulerAudit(
            audit_id=data.get("audit_id", ""),
            action=data.get("action", ""),
            performed_by=data.get("performed_by", ""),
            outcome=data.get("outcome", ""),
            task_id=data.get("task_id"),
            session_id=data.get("session_id"),
            details=data.get("details"),
            warnings=data.get("warnings", []),
            errors=data.get("errors", []),
            timestamp=data.get("timestamp"),
        )
    except (KeyError, TypeError):
        return None
