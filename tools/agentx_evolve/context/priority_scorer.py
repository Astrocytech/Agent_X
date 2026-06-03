from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import (
    ContextItem, TaskInput,
    SOURCE_TRUST_SYSTEM, SOURCE_TRUST_AGENTX_CONTRACT,
    SOURCE_TRUST_VALIDATED_ARTIFACT, SOURCE_TRUST_BLOCKED,
    EXCLUDE_LOW_PRIORITY, EXCLUDE_POLICY_BLOCKED,
)


TRUST_ORDER = {
    SOURCE_TRUST_SYSTEM: 0,
    SOURCE_TRUST_AGENTX_CONTRACT: 1,
    SOURCE_TRUST_VALIDATED_ARTIFACT: 2,
}

SOURCE_TRUST_USER_INPUT_ORDER = 3
SOURCE_TRUST_TOOL_OUTPUT_ORDER = 4
SOURCE_TRUST_UNTRUSTED_TEXT_ORDER = 5
SOURCE_TRUST_BLOCKED_SCORE = -1.0


def score_context_priority(
    item: ContextItem,
    task_input: TaskInput,
    scoring_context: dict | None = None,
) -> ContextItem:
    score = 0.0

    if item.source_trust_level == SOURCE_TRUST_BLOCKED:
        item.priority_score = 0.0
        item.inclusion_decision = EXCLUDE_POLICY_BLOCKED
        return item

    trust_rank = TRUST_ORDER.get(item.source_trust_level, 5)
    trust_score = max(0.1, 1.0 - (trust_rank * 0.15))
    score += trust_score * 0.4

    if task_input.task_title and item.title:
        if task_input.task_title.lower() in item.content.lower():
            score += 0.3

    if item.item_kind in ("CONSTRAINT", "REQUIREMENT", "SYSTEM_CONSTRAINT"):
        score += 0.2

    if task_input.target_files:
        if any(tf in item.content for tf in task_input.target_files):
            score += 0.1

    score = min(score, 1.0)
    item.priority_score = round(score, 4)
    return item


def score_priority_batch(
    items: list[ContextItem],
    task_input: TaskInput,
    scoring_context: dict | None = None,
) -> list[ContextItem]:
    scored = [score_context_priority(it, task_input, scoring_context) for it in items]
    scored.sort(key=lambda i: i.priority_score, reverse=True)
    return scored
