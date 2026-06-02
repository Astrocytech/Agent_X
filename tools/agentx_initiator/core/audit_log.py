from __future__ import annotations
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4
from agentx_initiator.core.audit_model import AuditEvent, AuditAppendResult
from agentx_initiator.core.path_registry import get_path


def _compute_event_hash(event: AuditEvent) -> str:
    to_hash = event.to_dict().copy()
    to_hash.pop("event_hash", None)
    canonical = json.dumps(to_hash, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _read_last_hash(log_path: Path) -> Optional[str]:
    if not log_path.exists():
        return None
    last_hash: Optional[str] = None
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    record = json.loads(line)
                    h = record.get("event_hash")
                    if h:
                        last_hash = h
                except json.JSONDecodeError:
                    continue
    return last_hash


def append_event(event: dict | AuditEvent) -> AuditAppendResult:
    log_path = get_path("audit_events_file")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(event, dict):
        ae = AuditEvent.from_dict(event)
    else:
        ae = event

    if not ae.event_id:
        ae.event_id = str(uuid4())
    if not ae.timestamp:
        ae.timestamp = datetime.now(timezone.utc).isoformat()
    if not ae.component:
        ae.component = "agentx-init"

    ae.previous_event_hash = _read_last_hash(log_path)
    ae.event_hash = _compute_event_hash(ae)

    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(ae.to_dict(), separators=(",", ":")) + "\n")
    except OSError as e:
        return AuditAppendResult(
            status="FAILED", event_id=ae.event_id, warning=str(e)
        )

    return AuditAppendResult(
        status="SUCCESS", event_id=ae.event_id, event_hash=ae.event_hash
    )


def read_events(limit: int = 100) -> list[dict]:
    log_path = get_path("audit_events_file")
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
                    continue
    return events[-limit:]
