import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifact_writer import runtime_root


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def append_event(repo_root: Path, event_type: str, data: dict[str, Any]) -> None:
    rt = runtime_root(repo_root)
    rt.mkdir(parents=True, exist_ok=True)
    log_path = rt / "final_acceptance_event_history.jsonl"
    entry = {
        "timestamp": _make_timestamp(),
        "event_type": event_type,
        "data": data,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def append_command_record(
    repo_root: Path,
    command_name: str,
    status: str,
    exit_code: int | None,
    summary: str,
) -> None:
    rt = runtime_root(repo_root)
    rt.mkdir(parents=True, exist_ok=True)
    log_path = rt / "final_acceptance_command_history.jsonl"
    entry = {
        "timestamp": _make_timestamp(),
        "command_name": command_name,
        "status": status,
        "exit_code": exit_code,
        "summary": summary,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
