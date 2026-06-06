from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_events import (
    canonical_json,
    sha256_dict,
)


def sha256_file(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def append_jsonl(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")
    return path


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    import json
    return json.loads(path.read_text())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def redact_payload(payload: dict, keys_to_redact: set[str] | None = None) -> dict:
    if keys_to_redact is None:
        keys_to_redact = {"secret", "password", "token", "api_key", "private_key"}
    result: dict = {}
    for k, v in payload.items():
        if k.lower() in keys_to_redact:
            result[k] = "***REDACTED***"
        elif isinstance(v, dict):
            result[k] = redact_payload(v, keys_to_redact)
        elif isinstance(v, list):
            result[k] = [
                redact_payload(item, keys_to_redact) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            result[k] = v
    return result
