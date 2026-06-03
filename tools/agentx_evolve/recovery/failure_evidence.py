from __future__ import annotations

import json
from pathlib import Path

from agentx_evolve.recovery.failure_models import (
    FailureRecord,
    RecoveryAction,
    RecoveryDecision,
    SafeModeTrigger,
    to_dict,
    utc_now_iso,
    new_id,
)

RECOVERY_DIR = ".agentx-init/recovery"
FAILURE_RECORDS_FILE = "failure_records.jsonl"
RECOVERY_DECISIONS_FILE = "recovery_decisions.jsonl"
SAFE_MODE_TRIGGERS_FILE = "safe_mode_triggers.jsonl"
LATEST_FAILURE_FILE = "latest_failure_record.json"
LATEST_RECOVERY_DECISION_FILE = "latest_recovery_decision.json"
LATEST_SAFE_MODE_TRIGGER_FILE = "latest_safe_mode_trigger.json"
RECOVERY_SUMMARY_FILE = "recovery_summary.json"
COMPLETION_RECORD_FILE = "failure_recovery_completion_record.json"


def _ensure_dir(repo_root: Path) -> Path:
    d = repo_root / RECOVERY_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _atomic_write_json(data: dict, path: Path) -> dict:
    try:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        tmp.rename(path)
        return {"status": "SUCCESS", "path": str(path), "artifact_id": data.get("failure_id") or data.get("recovery_decision_id") or data.get("safe_mode_trigger_id"), "message": "Write completed", "warnings": [], "errors": []}
    except OSError as e:
        return {"status": "FAILED", "path": str(path), "artifact_id": None, "message": str(e), "warnings": [], "errors": [str(e)]}


def _append_jsonl(data: dict, path: Path) -> dict:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, default=str) + "\n")
        return {"status": "SUCCESS", "path": str(path), "artifact_id": data.get("failure_id") or data.get("recovery_decision_id") or data.get("safe_mode_trigger_id"), "message": "Append completed", "warnings": [], "errors": []}
    except OSError as e:
        return {"status": "FAILED", "path": str(path), "artifact_id": None, "message": str(e), "warnings": [], "errors": [str(e)]}


def append_failure_record(failure: FailureRecord, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = to_dict(failure)
    return _append_jsonl(d, base / FAILURE_RECORDS_FILE)


def append_recovery_decision(decision: RecoveryDecision, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = to_dict(decision)
    return _append_jsonl(d, base / RECOVERY_DECISIONS_FILE)


def append_safe_mode_trigger(trigger: SafeModeTrigger, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = to_dict(trigger)
    return _append_jsonl(d, base / SAFE_MODE_TRIGGERS_FILE)


def write_latest_failure_record(failure: FailureRecord, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = to_dict(failure)
    return _atomic_write_json(d, base / LATEST_FAILURE_FILE)


def write_latest_recovery_decision(decision: RecoveryDecision, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = to_dict(decision)
    return _atomic_write_json(d, base / LATEST_RECOVERY_DECISION_FILE)


def write_latest_safe_mode_trigger(trigger: SafeModeTrigger, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = to_dict(trigger)
    return _atomic_write_json(d, base / LATEST_SAFE_MODE_TRIGGER_FILE)


def write_recovery_summary(summary: dict, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    return _atomic_write_json(summary, base / RECOVERY_SUMMARY_FILE)


def write_failure_recovery_completion_record(completion: dict, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    return _atomic_write_json(completion, base / COMPLETION_RECORD_FILE)
