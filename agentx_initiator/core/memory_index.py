from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.memory_model import MemoryRecord, MemoryIndex


def build_index(records: list[MemoryRecord]) -> MemoryIndex:
    by_category: dict[str, list[str]] = {}
    by_source_component: dict[str, list[str]] = {}
    by_source_artifact: dict[str, list[str]] = {}
    by_status: dict[str, list[str]] = {}
    by_memory_id: dict[str, dict] = {}

    for r in records:
        mid = r.memory_id
        cat = r.category or "UNKNOWN"
        comp = r.source_component or "UNKNOWN"
        art = r.source_artifact or "UNKNOWN"
        st = r.status or "UNKNOWN"

        by_category.setdefault(cat, []).append(mid)
        by_source_component.setdefault(comp, []).append(mid)
        by_source_artifact.setdefault(art, []).append(mid)
        by_status.setdefault(st, []).append(mid)
        by_memory_id[mid] = r.to_dict()

    return MemoryIndex(
        schema_version="1.0",
        index_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        by_category=by_category,
        by_source_component=by_source_component,
        by_source_artifact=by_source_artifact,
        by_status=by_status,
        by_memory_id=by_memory_id,
        record_count=len(records),
    )
