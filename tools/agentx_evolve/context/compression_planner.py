from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import ContextItem


COMPRESSION_SAFE_KINDS = {"FILE_SNIPPET", "TOOL_RESULT", "TEST_RESULT", "SUMMARY", "EVIDENCE_REF"}
MUST_KEEP_KINDS = {"CONSTRAINT", "REQUIREMENT", "POLICY_DECISION", "SCHEMA"}


def plan_context_compression(
    items: list[ContextItem],
    budget_estimate: dict,
    compression_context: dict | None = None,
) -> dict[str, Any]:
    if budget_estimate.get("fits", True):
        return {
            "plan_id": f"plan-no-compression",
            "needs_compression": False,
            "compressible_item_ids": [],
            "must_keep_verbatim_ids": [it.context_item_id for it in items],
            "summary_item_ids": [],
            "tokens_saved_estimate": 0,
            "warnings": [],
            "errors": [],
        }

    over = budget_estimate.get("over_budget_tokens", 0)
    must_keep: list[str] = []
    compressible: list[str] = []

    for item in sorted(items, key=lambda i: i.priority_score):
        if item.item_kind in MUST_KEEP_KINDS or item.source_trust_level in (
            "SOURCE_TRUST_SYSTEM", "SOURCE_TRUST_AGENTX_CONTRACT",
        ):
            must_keep.append(item.context_item_id)
        elif item.item_kind in COMPRESSION_SAFE_KINDS:
            compressible.append(item.context_item_id)
        else:
            compressible.append(item.context_item_id)

    summary_ids = compressible[:max(1, len(compressible) // 2)]
    savings = sum(
        it.token_estimate
        for it in items
        if it.context_item_id in summary_ids
    )

    return {
        "plan_id": f"plan-compress-{over}",
        "needs_compression": True,
        "compressible_item_ids": compressible,
        "must_keep_verbatim_ids": must_keep,
        "summary_item_ids": summary_ids,
        "tokens_saved_estimate": savings,
        "warnings": [] if savings >= over else ["compression may not save enough tokens"],
        "errors": [],
    }
