"""LocalMemoryPort — L0 seed memory port backed by hash-chained JSONL."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).resolve().parents[3] / ".local" / "runtime" / "memory"
_CURRENT_SCHEMA_VERSION = "2"


def _hash_event(event: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(event, sort_keys=True, default=str).encode()).hexdigest()


class LocalMemoryPort:
    runtime_safety_class = "production_seed_port"

    def __init__(self) -> None:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)

    def write(self, observation: str, ctx: dict) -> list[str]:
        scope_id = ctx.get("scope_id", "default")
        run_id = ctx.get("run_id", "")
        task_id = ctx.get("task_id", "")
        profile_id = ctx.get("profile_id", "")
        policy_id = ctx.get("policy_id", "")
        trace_id = ctx.get("trace_id", "")
        source_phase = ctx.get("source_phase", "")
        source_tool = ctx.get("source_tool", "")
        requester_id = ctx.get("requester_id", "kernel")
        event_id = f"mem-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        previous_events = sorted(_DATA_DIR.glob("*.json"))
        previous_hash = ""
        if previous_events:
            try:
                last = json.loads(previous_events[-1].read_text())
                previous_hash = last.get("event_hash", "")
            except (json.JSONDecodeError, OSError):
                previous_hash = ""

        value = {"observation": observation, "ctx": ctx}
        payload_hash = hashlib.sha256(
            json.dumps(value, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

        record = {
            "event_id": event_id,
            "run_id": run_id,
            "task_id": task_id,
            "profile_id": profile_id,
            "scope_id": scope_id,
            "policy_id": policy_id,
            "trace_id": trace_id,
            "source_phase": source_phase,
            "source_tool": source_tool,
            "requester_id": requester_id,
            "schema_version": _CURRENT_SCHEMA_VERSION,
            "created_at": now,
            "value": value,
            "payload_hash": payload_hash,
            "previous_event_hash": previous_hash,
        }
        record["event_hash"] = _hash_event(record)

        (_DATA_DIR / f"{event_id}.json").write_text(json.dumps(record, default=str))
        return [event_id]

    def replay(self) -> list[dict]:
        """Verify hash chain integrity. Returns list of broken links."""
        broken = []
        files = sorted(_DATA_DIR.glob("*.json"))
        previous = ""
        for i, fpath in enumerate(files):
            try:
                event = json.loads(fpath.read_text())
            except (json.JSONDecodeError, OSError):
                broken.append({"index": i, "file": fpath.name, "reason": "unreadable"})
                continue
            expected_hash = _hash_event({k: v for k, v in event.items() if k != "event_hash"})
            if event.get("event_hash", "") != expected_hash:
                broken.append(
                    {"index": i, "event_id": event.get("event_id"), "reason": "hash_mismatch"}
                )
            if i > 0 and event.get("previous_event_hash", "") != previous:
                broken.append(
                    {"index": i, "event_id": event.get("event_id"), "reason": "chain_break"}
                )
            previous = event.get("event_hash", "")
        return broken


