from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import (
    ContextItem,
    EXCLUDE_DUPLICATE,
)
from agentx_evolve.context.context_models import SOURCE_TRUST_SYSTEM, SOURCE_TRUST_BLOCKED


TRUST_ORDER = [
    SOURCE_TRUST_SYSTEM,
    "SOURCE_TRUST_AGENTX_CONTRACT",
    "SOURCE_TRUST_VALIDATED_ARTIFACT",
]


def deduplicate_context_items(items: list[ContextItem]) -> dict[str, Any]:
    seen_dedupe: dict[str, ContextItem] = {}
    duplicates: list[ContextItem] = []
    unique: list[ContextItem] = []
    records: list[dict] = []

    for item in items:
        key = item.dedupe_key or item.content_hash or item.title
        if not key:
            unique.append(item)
            continue

        if key in seen_dedupe:
            existing = seen_dedupe[key]
            keep = _resolve_duplicate(existing, item)
            if keep == item:
                seen_dedupe[key] = item
                duplicates.append(existing)
                existing.inclusion_decision = EXCLUDE_DUPLICATE
            else:
                duplicates.append(item)
                item.inclusion_decision = EXCLUDE_DUPLICATE
            records.append({
                "primary_item_id": seen_dedupe[key].context_item_id,
                "duplicate_item_ids": [item.context_item_id],
                "decision": "KEEP_PRIMARY",
                "reason": f"duplicate key: {key}",
            })
        else:
            seen_dedupe[key] = item

    unique = list(seen_dedupe.values())

    unique.sort(key=lambda i: i.priority_score, reverse=True)

    return {
        "unique_items": unique,
        "duplicates": duplicates,
        "records": records,
        "total_input": len(items),
        "total_unique": len(unique),
        "total_duplicates": len(duplicates),
    }


def _resolve_duplicate(a: ContextItem, b: ContextItem) -> ContextItem:
    a_trust_idx = _trust_index(a.source_trust_level)
    b_trust_idx = _trust_index(b.source_trust_level)
    if a_trust_idx < b_trust_idx:
        return a
    elif b_trust_idx < a_trust_idx:
        return b
    if a.priority_score >= b.priority_score:
        return a
    return b


def _trust_index(level: str) -> int:
    try:
        return TRUST_ORDER.index(level)
    except ValueError:
        return len(TRUST_ORDER)
