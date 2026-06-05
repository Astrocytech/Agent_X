from __future__ import annotations

import json
from pathlib import Path

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    InvalidToolRecord,
    to_dict,
)

TOOL_CALLS_DIR = ".agentx-init/tool_calls"

CALL_HISTORY_FILE = "tool_call_history.jsonl"
RESULT_HISTORY_FILE = "tool_result_history.jsonl"
BLOCKED_HISTORY_FILE = "blocked_tool_history.jsonl"
INVALID_HISTORY_FILE = "invalid_tool_history.jsonl"
LATEST_CALL_FILE = "latest_tool_call.json"
LATEST_RESULT_FILE = "latest_tool_result.json"


def _ensure_dir(repo_root: Path) -> Path:
    d = repo_root / TOOL_CALLS_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _atomic_write_json(data: dict, path: Path) -> dict:
    try:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        tmp.rename(path)
        return {"status": "SUCCESS", "path": str(path), "artifact_id": data.get("tool_call_id") or data.get("tool_result_id"), "message": "Write completed", "warnings": [], "errors": []}
    except OSError as e:
        return {"status": "FAILED", "path": str(path), "artifact_id": None, "message": str(e), "warnings": [], "errors": [str(e)]}


def _append_jsonl(data: dict, path: Path) -> dict:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, default=str) + "\n")
        return {"status": "SUCCESS", "path": str(path), "artifact_id": data.get("tool_call_id") or data.get("tool_result_id") or data.get("record_id"), "message": "Append completed", "warnings": [], "errors": []}
    except OSError as e:
        return {"status": "FAILED", "path": str(path), "artifact_id": None, "message": str(e), "warnings": [], "errors": [str(e)]}


def _redact(data: dict) -> dict:
    redacted = {}
    for k, v in data.items():
        if isinstance(v, str) and _looks_like_secret(k, v):
            redacted[k] = "<REDACTED>"
        elif isinstance(v, dict):
            redacted[k] = _redact(v)
        elif isinstance(v, list):
            redacted[k] = [_redact(item) if isinstance(item, dict) else item for item in v]
        else:
            redacted[k] = v
    return redacted


def _looks_like_secret(key: str, value: str) -> bool:
    key_lower = key.lower()
    if any(k in key_lower for k in ("secret", "password", "token", "key", "credential", "auth")):
        return True
    if len(value) > 100:
        return True
    return False


def append_tool_call(tool_call: ToolCall, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = _redact(to_dict(tool_call))
    return _append_jsonl(d, base / CALL_HISTORY_FILE)


def append_tool_result(result: ToolResult, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = _redact(to_dict(result))
    return _append_jsonl(d, base / RESULT_HISTORY_FILE)


def append_blocked_tool(tool_call: ToolCall, result: ToolResult, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    entry = {
        "tool_call": _redact(to_dict(tool_call)),
        "tool_result": _redact(to_dict(result)),
        "timestamp": result.timestamp,
    }
    return _append_jsonl(entry, base / BLOCKED_HISTORY_FILE)


def append_invalid_tool(record: InvalidToolRecord, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = _redact(to_dict(record))
    return _append_jsonl(d, base / INVALID_HISTORY_FILE)


def write_latest_tool_call(tool_call: ToolCall, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = _redact(to_dict(tool_call))
    return _atomic_write_json(d, base / LATEST_CALL_FILE)


def write_latest_tool_result(result: ToolResult, repo_root: Path) -> dict:
    base = _ensure_dir(repo_root)
    d = _redact(to_dict(result))
    return _atomic_write_json(d, base / LATEST_RESULT_FILE)


def write_tool_call_evidence(tool_call: ToolCall, result: ToolResult, repo_root: Path) -> dict:
    call_result = append_tool_call(tool_call, repo_root)
    result_result = append_tool_result(result, repo_root)
    latest_call_result = write_latest_tool_call(tool_call, repo_root)
    latest_result_result = write_latest_tool_result(result, repo_root)
    return {
        "status": "SUCCESS",
        "call_history": call_result,
        "result_history": result_result,
        "latest_call": latest_call_result,
        "latest_result": latest_result_result,
    }
