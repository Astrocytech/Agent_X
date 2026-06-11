"""Append-only event logger with hash-chain enforcement.

Item 13.1: Monotonic sequence IDs, hash-chain, duplicate/out-of-order rejection.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _event_hash(event: dict) -> str:
    return hashlib.sha256(_canonical_json(event).encode()).hexdigest()


def _last_event_info(log_path: Path) -> tuple[int, str]:
    if not log_path.exists() or log_path.stat().st_size == 0:
        return 0, ""
    last_hash = ""
    last_seq = 0
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            seq = ev.get("sequence_id", 0)
            if isinstance(seq, int) and seq > last_seq:
                last_seq = seq
                last_hash = _event_hash(ev)
    return last_seq, last_hash


KNOWN_TYPES = frozenset({
    "proposal_created", "risk_classified", "context_packet_created",
    "prompt_contract_selected", "worker_output_created",
    "patch_candidate_created", "patch_candidate_validated",
    "patch_applied", "validation_started", "validation_completed",
    "rollback_started", "rollback_completed", "review_requested",
    "review_completed", "promotion_requested", "promotion_completed",
    "candidate_rejected", "negative_knowledge_recorded",
    "final_acceptance_evaluated",
    # Also accept bare stage names for backward compatibility
    "proposal", "risk", "context", "prompt",
    "patch_candidate", "patch_validation", "patch_execution",
    "test", "evidence", "review", "promotion", "acceptance",
})


def log_event(
    event: dict[str, Any],
    log_path: Path,
) -> dict[str, Any]:
    """Append a single event with hash-chain enforcement.

    - Assigns monotonic ``sequence_id`` if not present.
    - Computes and stores ``previous_hash`` (SHA-256 of previous event).
    - Rejects duplicate ``event_id`` and out-of-order ``sequence_id``.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    last_seq, last_hash = _last_event_info(log_path)

    new_seq = last_seq + 1
    if "sequence_id" in event:
        req_seq = event["sequence_id"]
        if not isinstance(req_seq, int) or req_seq < 1:
            return {"status": "rejected", "reason": f"invalid sequence_id: {req_seq}"}
        if req_seq <= last_seq:
            return {"status": "rejected", "reason": f"sequence_id {req_seq} <= last {last_seq}"}
        if req_seq != last_seq + 1:
            return {"status": "rejected", "reason": f"sequence_id {req_seq} != expected {last_seq + 1} (gap)"}
        new_seq = req_seq

    event["sequence_id"] = new_seq
    event["previous_hash"] = last_hash
    if "event_type" not in event:
        event["event_type"] = event.get("stage", "unknown")
    if "event_id" not in event:
        event["event_id"] = f"evt-{new_seq:06d}"

    # Duplicate event_id check (all existing events)
    existing_ids = set()
    if log_path.exists():
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    existing_ids.add(json.loads(line).get("event_id", ""))
                except json.JSONDecodeError:
                    pass
    if event["event_id"] in existing_ids:
        return {"status": "rejected", "reason": f"duplicate event_id: {event['event_id']}"}

    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")

    return {"status": "logged", "path": str(log_path), "event_id": event["event_id"],
            "sequence_id": new_seq, "hash": _event_hash(event)}


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
    """Validate event log ordering, hash-chain, and required fields."""
    errors = []
    if not events:
        errors.append("Event log is empty")
        return errors

    stage_order = [
        "proposal", "risk", "context", "prompt",
        "patch_candidate", "patch_validation", "patch_execution",
        "test", "evidence", "review", "promotion", "acceptance",
    ]
    seen_stages: set[str] = set()
    expected_seq = 1
    prev_hash = ""

    for i, ev in enumerate(events):
        stage = ev.get("stage")
        if stage:
            seen_stages.add(stage)

        if not ev.get("event_id"):
            errors.append(f"Event {i}: missing event_id")

        seq = ev.get("sequence_id")
        if not isinstance(seq, int) or seq < 1:
            errors.append(f"Event {i}: missing or invalid sequence_id")
        elif seq != expected_seq:
            errors.append(f"Event {i}: sequence_id {seq} != expected {expected_seq}")
        expected_seq = seq + 1 if isinstance(seq, int) else expected_seq + 1

        actual_prev = ev.get("previous_hash", "")
        if actual_prev != prev_hash:
            errors.append(f"Event {i}: previous_hash mismatch (got {actual_prev[:16]}..., expected {prev_hash[:16]}...)")

        prev_hash = _event_hash(ev)

        if ev.get("event_type") and ev["event_type"] not in KNOWN_TYPES:
            errors.append(f"Event {i}: unknown event_type '{ev['event_type']}'")

        if not ev.get("timestamp"):
            errors.append(f"Event {i}: missing timestamp")

    for stage in stage_order:
        if stage not in seen_stages:
            errors.append(f"Required stage '{stage}' not found in event log")

    return errors
