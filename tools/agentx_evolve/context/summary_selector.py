from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import (
    ContextItem,
    SUMMARIZE,
    new_id,
)
from agentx_evolve.context.context_models import stable_hash


def select_summary_items(
    items: list[ContextItem],
    compression_plan: dict,
) -> list[ContextItem]:
    summary_ids = set(compression_plan.get("summary_item_ids", []))
    summaries: list[ContextItem] = []

    for item in items:
        if item.context_item_id not in summary_ids:
            continue

        if item.summarized:
            summaries.append(item)
            continue

        excerpt = _extractive_excerpt(item.content, max_chars=500)
        summary = ContextItem(
            context_item_id=new_id("ci-summary"),
            created_at=item.created_at,
            source_id=item.source_id,
            source_component=item.source_component,
            source_trust_level="SOURCE_TRUST_SUMMARY",
            item_kind="SUMMARY",
            title=f"Summary: {item.title}",
            content=excerpt,
            content_hash=stable_hash(excerpt),
            dedupe_key=f"summary:{item.dedupe_key or item.context_item_id}",
            inclusion_decision=SUMMARIZE,
            summarized=True,
            artifact_refs=item.artifact_refs,
            evidence_refs=item.evidence_refs + [item.context_item_id],
        )
        summaries.append(summary)

    return summaries


def _extractive_excerpt(text: str, max_chars: int = 500) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
