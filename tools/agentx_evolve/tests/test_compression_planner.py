import pytest
from agentx_evolve.context.compression_planner import plan_context_compression
from agentx_evolve.context.context_models import ContextItem


class TestCompressionPlanner:
    def test_over_budget_plan_created(self):
        items = [
            ContextItem(context_item_id="keep", item_kind="CONSTRAINT", source_trust_level="SOURCE_TRUST_SYSTEM", content="must keep", priority_score=0.9),
            ContextItem(context_item_id="compress", item_kind="FILE_SNIPPET", source_trust_level="SOURCE_TRUST_UNTRUSTED_TEXT", content="x " * 1000, priority_score=0.1),
        ]
        budget = {"fits": False, "over_budget_tokens": 500}
        plan = plan_context_compression(items, budget)
        assert plan["needs_compression"] is True
        assert "keep" in plan["must_keep_verbatim_ids"]
        assert "compress" in plan["compressible_item_ids"]

    def test_safety_constraint_verbatim(self):
        items = [
            ContextItem(context_item_id="safety", item_kind="CONSTRAINT", source_trust_level="SOURCE_TRUST_SYSTEM", content="safety first", priority_score=0.9),
        ]
        budget = {"fits": True}
        plan = plan_context_compression(items, budget)
        assert plan["needs_compression"] is False

    def test_no_compression_needed(self):
        items = [ContextItem(context_item_id="a", priority_score=0.5)]
        budget = {"fits": True}
        plan = plan_context_compression(items, budget)
        assert plan["needs_compression"] is False
