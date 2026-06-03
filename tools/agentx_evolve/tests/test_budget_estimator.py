import pytest
from agentx_evolve.context.budget_estimator import (
    estimate_context_item_budget,
    estimate_context_pack_budget,
)
from agentx_evolve.context.context_models import ContextItem


class TestBudgetEstimator:
    def test_short_vs_long(self):
        short = ContextItem(context_item_id="short", content="hi")
        long_ = ContextItem(context_item_id="long", content="a " * 1000)
        short_b = estimate_context_item_budget(short)
        long_b = estimate_context_item_budget(long_)
        assert short_b["token_estimate"] < long_b["token_estimate"]

    def test_reserved_output_reduces_available(self):
        items = [ContextItem(context_item_id="a", content="hello")]
        budget = estimate_context_pack_budget(items, max_context_tokens=1000, reserved_output_tokens=200)
        assert budget["available_input_tokens"] == 800

    def test_over_budget_pack_flagged(self):
        items = [ContextItem(context_item_id="a", content="x " * 10000)]
        budget = estimate_context_pack_budget(items, max_context_tokens=100, reserved_output_tokens=0)
        assert budget["over_budget"] is True

    def test_deterministic(self):
        items = [ContextItem(context_item_id="a", content="hello world")]
        b1 = estimate_context_pack_budget(items, 8192, 1024)
        b2 = estimate_context_pack_budget(items, 8192, 1024)
        assert b1["total_estimated_tokens"] == b2["total_estimated_tokens"]

    def test_within_budget(self):
        items = [ContextItem(context_item_id="a", content="small")]
        budget = estimate_context_pack_budget(items, 1000, 100)
        assert budget["fits"] is True
