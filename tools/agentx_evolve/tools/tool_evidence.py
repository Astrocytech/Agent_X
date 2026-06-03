from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_tool_evidence(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def validate_tool_evidence(evidence: dict[str, Any], session_id: str) -> list[str]:
    errors: list[str] = []
    if not evidence:
        errors.append("Tool evidence is empty")
        return errors
    if evidence.get("session_id") != session_id:
        errors.append(f"session_id mismatch: expected {session_id}, got {evidence.get('session_id')}")
    return errors
