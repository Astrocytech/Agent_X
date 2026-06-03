import pytest
from agentx_evolve.context.summary_selector import select_summary_items
from agentx_evolve.context.context_models import ContextItem


class TestSummarySelector:
    def test_existing_summary_selected(self):
        existing = ContextItem(
            context_item_id="existing-summary",
            item_kind="SUMMARY",
            title="Existing summary",
            content="already summarized",
            summarized=True,
        )
        items = [existing]
        plan = {"summary_item_ids": ["existing-summary"]}
        result = select_summary_items(items, plan)
        assert len(result) == 1
        assert result[0].summarized is True

    def test_extractive_summary_deterministic(self):
        item = ContextItem(
            context_item_id="long-item",
            title="Long document",
            content="A " * 500,
        )
        items = [item]
        plan = {"summary_item_ids": ["long-item"]}
        r1 = select_summary_items(items, plan)
        r2 = select_summary_items(items, plan)
        assert len(r1) == 1
        assert r1[0].content == r2[0].content

    def test_summary_keeps_original_evidence_refs(self):
        item = ContextItem(
            context_item_id="orig",
            title="Original",
            content="Some content here",
            evidence_refs=["ev-001"],
        )
        items = [item]
        plan = {"summary_item_ids": ["orig"]}
        result = select_summary_items(items, plan)
        assert "ev-001" in result[0].evidence_refs

    def test_summary_does_not_replace_safety_critical(self):
        items = [ContextItem(context_item_id="safe", title="Safety", content="safety")]
        plan = {"summary_item_ids": []}
        result = select_summary_items(items, plan)
        assert len(result) == 0
