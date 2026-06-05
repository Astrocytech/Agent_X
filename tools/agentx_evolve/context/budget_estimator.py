from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import ContextItem
from agentx_evolve.context.context_models import estimate_tokens_rough


def estimate_context_item_budget(item: ContextItem) -> dict[str, Any]:
    tokens = estimate_tokens_rough(item.content)
    item.token_estimate = tokens
    return {
        "context_item_id": item.context_item_id,
        "token_estimate": tokens,
        "content_length": len(item.content),
    }


def estimate_context_pack_budget(
    items: list[ContextItem],
    max_context_tokens: int,
    reserved_output_tokens: int,
) -> dict[str, Any]:
    total = sum(estimate_tokens_rough(it.content) for it in items)
    available = max_context_tokens - reserved_output_tokens
    fits = total <= available
    over = max(0, total - available)

    return {
        "max_context_tokens": max_context_tokens,
        "reserved_output_tokens": reserved_output_tokens,
        "available_input_tokens": available,
        "total_estimated_tokens": total,
        "fits": fits,
        "over_budget_tokens": over,
        "item_count": len(items),
        "over_budget": not fits,
    }
