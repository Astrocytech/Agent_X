import pytest
from agentx_evolve.context.deduplication_engine import deduplicate_context_items
from agentx_evolve.context.context_models import (
    ContextItem,
    SOURCE_TRUST_SYSTEM,
    SOURCE_TRUST_UNTRUSTED_TEXT,
    EXCLUDE_DUPLICATE,
)


class TestDeduplicateContextItems:
    def test_exact_duplicate_removed(self):
        items = [
            ContextItem(context_item_id="a", content_hash="hash1", title="same"),
            ContextItem(context_item_id="b", content_hash="hash1", title="same"),
        ]
        result = deduplicate_context_items(items)
        assert result["total_unique"] == 1
        assert result["total_duplicates"] == 1

    def test_higher_trust_duplicate_retained(self):
        items = [
            ContextItem(context_item_id="low", source_trust_level=SOURCE_TRUST_UNTRUSTED_TEXT, content_hash="h1"),
            ContextItem(context_item_id="high", source_trust_level=SOURCE_TRUST_SYSTEM, content_hash="h1"),
        ]
        result = deduplicate_context_items(items)
        assert result["total_unique"] == 1
        assert result["unique_items"][0].context_item_id == "high"

    def test_deduplication_records_excluded_ids(self):
        items = [
            ContextItem(context_item_id="a", content_hash="h1"),
            ContextItem(context_item_id="b", content_hash="h1"),
        ]
        result = deduplicate_context_items(items)
        assert len(result["records"]) == 1
        assert "a" in result["records"][0]["primary_item_id"] or "b" in result["records"][0]["primary_item_id"]

    def test_no_duplicates_returns_all(self):
        items = [
            ContextItem(context_item_id="a", content_hash="h1"),
            ContextItem(context_item_id="b", content_hash="h2"),
        ]
        result = deduplicate_context_items(items)
        assert result["total_unique"] == 2
        assert result["total_duplicates"] == 0
