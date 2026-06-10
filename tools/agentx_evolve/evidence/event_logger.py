"""Append-only event logger for umbrella agent milestone runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def log_event(
    event: dict[str, Any],
    log_path: Path,
) -> dict[str, Any]:
    """Append a single event to the JSONL event log."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")
    return {"status": "logged", "path": str(log_path), "event_id": event.get("event_id")}


def read_event_log(log_path: Path) -> list[dict[str, Any]]:
    """Read all events from a JSONL event log."""
    if not log_path.exists():
        return []
    events = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def validate_event_log(events: list[dict[str, Any]]) -> list[str]:
    """Validate event log ordering and required fields."""
    errors = []
    if not events:
        errors.append("Event log is empty")
        return errors
    stage_order = [
        "proposal", "risk", "context", "prompt",
        "patch_candidate", "patch_validation", "patch_execution",
        "test", "evidence", "review", "promotion", "acceptance",
    ]
    seen_stages = set()
    for i, ev in enumerate(events):
        stage = ev.get("stage")
        if stage:
            seen_stages.add(stage)
        if not ev.get("event_id"):
            errors.append(f"Event {i}: missing event_id")
        if not ev.get("timestamp"):
            errors.append(f"Event {i}: missing timestamp")
    for stage in stage_order:
        if stage not in seen_stages:
            errors.append(f"Required stage '{stage}' not found in event log")
    return errors
