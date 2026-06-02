from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Optional
from agentx_initiator.core.memory_model import (
    MemoryRecord, MemoryQuery, MemoryQueryResult,
    MemorySnapshot, MemoryManifest, MemoryWriteResult,
    MEMORY_CATEGORIES, MEMORY_STATUSES,
)
from agentx_initiator.core.memory_index import build_index
from agentx_initiator.core.jsonl_store import append_jsonl, read_jsonl
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.schema_validation import validate_schema_object


def _compute_content_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_record(record: MemoryRecord) -> Optional[str]:
    if not record.memory_id:
        return "memory_id is required"
    if not record.timestamp:
        return "timestamp is required"
    if record.category not in MEMORY_CATEGORIES:
        return f"Invalid category: {record.category}"
    if record.status not in MEMORY_STATUSES:
        return f"Invalid status: {record.status}"
    if not record.content_hash:
        expected = _compute_content_hash(record.payload)
        if record.content_hash != expected:
            return "content_hash mismatch"
    return None


def store_memory(record: MemoryRecord) -> MemoryWriteResult:
    validation_error = _validate_record(record)
    if validation_error:
        return MemoryWriteResult(status="FAILED", error=validation_error)

    record.content_hash = record.content_hash or _compute_content_hash(record.payload)

    path = get_path("memory_dir") / "memory_records.jsonl"
    result = append_jsonl(path, record.to_dict())
    if result.status != "SUCCESS":
        return MemoryWriteResult(status="FAILED", error=result.error)

    return MemoryWriteResult(
        status="SUCCESS",
        memory_id=record.memory_id,
        content_hash=record.content_hash,
    )


def load_memory(memory_id: str) -> Optional[MemoryRecord]:
    path = get_path("memory_dir") / "memory_records.jsonl"
    records = read_jsonl(path)
    for r in records:
        if r.get("memory_id") == memory_id:
            return MemoryRecord.from_dict(r) if hasattr(MemoryRecord, "from_dict") else MemoryRecord(**r)
    return None


def query_memory(query: MemoryQuery) -> MemoryQueryResult:
    path = get_path("memory_dir") / "memory_records.jsonl"
    raw = read_jsonl(path)

    matched: list[dict] = []
    for r in raw:
        if query.memory_id and r.get("memory_id") != query.memory_id:
            continue
        if query.category and r.get("category") != query.category:
            continue
        if query.source_component and r.get("source_component") != query.source_component:
            continue
        if query.source_artifact and r.get("source_artifact") != query.source_artifact:
            continue
        if query.status and r.get("status") != query.status:
            continue
        matched.append(r)

    matched.sort(key=lambda x: (x.get("timestamp", ""), x.get("memory_id", "")))

    return MemoryQueryResult(
        schema_version="1.0",
        query_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        query=query.to_dict(),
        result_count=len(matched),
        records=matched,
    )


def create_snapshot(records: list[MemoryRecord] | None = None) -> MemorySnapshot:
    if records is None:
        path = get_path("memory_dir") / "memory_records.jsonl"
        raw = read_jsonl(path)
        records = [MemoryRecord(**r) for r in raw]

    index = build_index(records)

    return MemorySnapshot(
        schema_version="1.0",
        snapshot_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        record_count=len(records),
        index_ref=index.index_id,
        records=[r.to_dict() for r in records],
    )


def build_manifest(records: list[MemoryRecord] | None = None,
                   index: Optional[object] = None) -> MemoryManifest:
    if records is None:
        path = get_path("memory_dir") / "memory_records.jsonl"
        raw = read_jsonl(path)
        records = [MemoryRecord(**r) for r in raw]
    if index is None:
        index = build_index(records)

    categories = list(dict.fromkeys(r.category for r in records if r.category))
    schema_versions = list(dict.fromkeys(r.schema_version for r in records if r.schema_version))

    return MemoryManifest(
        schema_version="1.0",
        manifest_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        record_count=len(records),
        latest_snapshot=index.index_id,
        latest_index=index.index_id,
        categories=categories,
        schema_versions=schema_versions,
    )
