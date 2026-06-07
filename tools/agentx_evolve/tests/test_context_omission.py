from __future__ import annotations

import pytest

from agentx_evolve.context.context_models import (
    ContextItem,
    INCLUDE,
    EXCLUDE_DUPLICATE,
    EXCLUDE_LOW_PRIORITY,
    EXCLUDE_OVER_BUDGET,
    EXCLUDE_POLICY_BLOCKED,
    EXCLUDE_INJECTION_RISK,
    EXCLUDE_SENSITIVE,
    SUMMARIZE,
    REDACT_AND_INCLUDE,
)

ALL_EXCLUSIONS = [
    EXCLUDE_DUPLICATE,
    EXCLUDE_LOW_PRIORITY,
    EXCLUDE_OVER_BUDGET,
    EXCLUDE_POLICY_BLOCKED,
    EXCLUDE_INJECTION_RISK,
    EXCLUDE_SENSITIVE,
]


class TestContextOmission:
    def test_inclusion_default_is_include(self):
        item = ContextItem(context_item_id="a")
        assert item.inclusion_decision == INCLUDE

    def test_exclusion_constants_defined(self):
        for ex in ALL_EXCLUSIONS:
            assert isinstance(ex, str)

    def test_summarize_is_valid_decision(self):
        item = ContextItem(context_item_id="b", inclusion_decision=SUMMARIZE)
        assert item.inclusion_decision == SUMMARIZE

    def test_redact_is_valid_decision(self):
        item = ContextItem(context_item_id="c", inclusion_decision=REDACT_AND_INCLUDE)
        assert item.inclusion_decision == REDACT_AND_INCLUDE

    def test_items_with_exclusions(self):
        items = [
            ContextItem(context_item_id="d", inclusion_decision=INCLUDE),
            ContextItem(context_item_id="e", inclusion_decision=EXCLUDE_LOW_PRIORITY),
            ContextItem(context_item_id="f", inclusion_decision=EXCLUDE_POLICY_BLOCKED),
        ]
        excluded = [i for i in items if i.inclusion_decision != INCLUDE]
        assert len(excluded) == 2
