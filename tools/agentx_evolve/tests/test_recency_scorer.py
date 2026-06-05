import pytest
from agentx_evolve.context.recency_scorer import score_context_recency, score_recency_batch
from agentx_evolve.context.context_models import ContextItem


class TestScoreContextRecency:
    def test_recent_above_old(self):
        recent = ContextItem(context_item_id="recent", created_at="2026-06-05T00:00:00")
        old = ContextItem(context_item_id="old", created_at="2026-01-01T00:00:00")
        ref = "2026-06-05T12:00:00"
        recent_scored = score_context_recency(recent, ref)
        old_scored = score_context_recency(old, ref)
        assert recent_scored.recency_score > old_scored.recency_score

    def test_undated_neutral(self):
        item = ContextItem(context_item_id="undated")
        scored = score_context_recency(item, "2026-06-05T00:00:00")
        assert scored.recency_score == 0.5

    def test_recent_scores_high(self):
        item = ContextItem(context_item_id="fresh", created_at="2026-06-04T00:00:00")
        scored = score_context_recency(item, "2026-06-05T00:00:00")
        assert scored.recency_score > 0.8
