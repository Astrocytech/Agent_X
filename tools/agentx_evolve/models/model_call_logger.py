from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelRetryRecord,
    to_dict,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
)

ARTIFACT_ROOT = ".agentx-init/model_calls"


def _ensure_dir(repo_root: Path) -> Path:
    p = repo_root / ARTIFACT_ROOT
    p.mkdir(parents=True, exist_ok=True)
    return p


def _redact_secrets(text: str) -> str:
    if not text:
        return text
    markers = ["sk-", "api_key", "api-key", "API_KEY", "secret_", "AKIA", "ghp_", "gho_"]
    for m in markers:
        if m in text:
            text = text.replace(m, "***REDACTED***")
    return text


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_jsonl(path: Path, data: dict):
    with open(path, "a") as f:
        f.write(json.dumps(data) + "\n")


def _write_atomic_json(path: Path, data: dict):
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tmp", dir=path.parent)
    try:
        json.dump(data, tmp)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp.close()
        os.replace(tmp.name, path)
    except Exception:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        raise


def append_model_request(request: ModelRequest, repo_root: Path) -> dict:
    d = to_dict(request)
    d["prompt"] = _redact_secrets(d["prompt"])
    d["system_prompt"] = _redact_secrets(d.get("system_prompt", ""))
    d["prompt_hash"] = _sha256(request.prompt)
    d["system_prompt_hash"] = _sha256(request.system_prompt or "")
    evidence_dir = _ensure_dir(repo_root)
    history_path = evidence_dir / "model_request_history.jsonl"
    _write_jsonl(history_path, d)
    return {"path": str(history_path), "written": True}


def append_model_response(response: ModelResponse, repo_root: Path) -> dict:
    d = to_dict(response)
    d["raw_output"] = _redact_secrets(d["raw_output"])
    d["output_hash"] = _sha256(response.raw_output)
    evidence_dir = _ensure_dir(repo_root)
    history_path = evidence_dir / "model_response_history.jsonl"
    _write_jsonl(history_path, d)
    return {"path": str(history_path), "written": True}


def append_model_retry(record: ModelRetryRecord, repo_root: Path) -> dict:
    d = to_dict(record)
    evidence_dir = _ensure_dir(repo_root)
    history_path = evidence_dir / "model_retry_history.jsonl"
    _write_jsonl(history_path, d)
    return {"path": str(history_path), "written": True}


def append_blocked_model(request: ModelRequest, response: ModelResponse, repo_root: Path) -> dict:
    d = {
        "request": {"model_id": request.model_id, "task_type": request.task_type, "caller_role": request.caller_role},
        "response": {"status": response.status, "message": response.message, "failure_class": response.failure_class},
        "timestamp": utc_now_iso(),
    }
    evidence_dir = _ensure_dir(repo_root)
    history_path = evidence_dir / "blocked_model_history.jsonl"
    _write_jsonl(history_path, d)
    return {"path": str(history_path), "written": True}


def append_invalid_model(request: ModelRequest | None, response: ModelResponse, repo_root: Path) -> dict:
    d = {
        "request": to_dict(request) if request else None,
        "response": to_dict(response),
        "timestamp": utc_now_iso(),
    }
    evidence_dir = _ensure_dir(repo_root)
    history_path = evidence_dir / "invalid_model_history.jsonl"
    _write_jsonl(history_path, d)
    return {"path": str(history_path), "written": True}


def write_latest_model_request(request: ModelRequest, repo_root: Path) -> dict:
    d = to_dict(request)
    d["prompt"] = _redact_secrets(d["prompt"])
    d["system_prompt"] = _redact_secrets(d.get("system_prompt", ""))
    d["prompt_hash"] = _sha256(request.prompt)
    d["system_prompt_hash"] = _sha256(request.system_prompt or "")
    evidence_dir = _ensure_dir(repo_root)
    latest_path = evidence_dir / "latest_model_request.json"
    _write_atomic_json(latest_path, d)
    return {"path": str(latest_path), "written": True}


def write_latest_model_response(response: ModelResponse, repo_root: Path) -> dict:
    d = to_dict(response)
    d["raw_output"] = _redact_secrets(d["raw_output"])
    d["output_hash"] = _sha256(response.raw_output)
    evidence_dir = _ensure_dir(repo_root)
    latest_path = evidence_dir / "latest_model_response.json"
    _write_atomic_json(latest_path, d)
    return {"path": str(latest_path), "written": True}


def write_model_call_evidence(request: ModelRequest, response: ModelResponse, repo_root: Path) -> dict:
    results = {}
    results["request"] = append_model_request(request, repo_root)
    results["response"] = append_model_response(response, repo_root)
    if response.status in ("BLOCKED",):
        results["blocked"] = append_blocked_model(request, response, repo_root)
    if response.status in ("INVALID",):
        results["invalid"] = append_invalid_model(request, response, repo_root)
    results["latest_request"] = write_latest_model_request(request, repo_root)
    results["latest_response"] = write_latest_model_response(response, repo_root)
    return results
