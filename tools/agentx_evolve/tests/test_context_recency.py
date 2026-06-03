from __future__ import annotations

import pytest

from agentx_evolve.context.recency_scorer import score_recency_batch
from agentx_evolve.context.context_models import ContextItem


class TestContextRecency:
    def test_score_all_items(self):
        items = [
            ContextItem(context_item_id="a", recency_score=0.0),
            ContextItem(context_item_id="b", recency_score=0.0),
        ]
        result = score_recency_batch(items)
        assert len(result) == 2

    def test_score_sets_positive_value(self):
        items = [ContextItem(context_item_id="a", recency_score=0.0)]
        result = score_recency_batch(items)
        assert result[0].recency_score >= 0.0

    def test_score_empty_list(self):
        result = score_recency_batch([])
        assert result == []
