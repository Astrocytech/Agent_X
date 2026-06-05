from __future__ import annotations
from datetime import datetime, timezone

from agentx_evolve.context.context_models import ContextItem


def score_context_recency(
    item: ContextItem,
    reference_time_iso: str | None = None,
) -> ContextItem:
    if reference_time_iso is None:
        reference_time_iso = datetime.now(timezone.utc).isoformat()

    if not item.created_at:
        item.recency_score = 0.5
        return item

    try:
        ref = datetime.fromisoformat(reference_time_iso)
        item_time = datetime.fromisoformat(item.created_at)
        age_seconds = (ref - item_time).total_seconds()
        if age_seconds < 0:
            age_seconds = 0
        max_age_seconds = 86400 * 30
        recency = max(0.0, 1.0 - (age_seconds / max_age_seconds))
        item.recency_score = round(recency, 4)
    except (ValueError, TypeError):
        item.recency_score = 0.5

    return item


def score_recency_batch(
    items: list[ContextItem],
    reference_time_iso: str | None = None,
) -> list[ContextItem]:
    return [score_context_recency(it, reference_time_iso) for it in items]
