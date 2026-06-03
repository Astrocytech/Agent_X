import pytest
from agentx_evolve.context.sensitive_data_redactor import (
    redact_sensitive_context_item,
    redact_sensitive_context_items,
)
from agentx_evolve.context.context_models import ContextItem


class TestRedactSensitiveContextItem:
    def test_api_key_redacted(self):
        item = ContextItem(
            context_item_id="ci-001",
            content="The api_key=sk-1234abcd5678efgh9012ijkl must be secret.",
        )
        redact_sensitive_context_item(item)
        assert item.redacted is True
        assert "[REDACTED_API_KEY]" in item.content

    def test_private_key_redacted(self):
        item = ContextItem(
            context_item_id="ci-002",
            content="-----BEGIN PRIVATE KEY-----\nABCDEF\n-----END PRIVATE KEY-----",
        )
        redact_sensitive_context_item(item)
        assert item.redacted is True

    def test_non_secret_technical_text_preserved(self):
        item = ContextItem(
            context_item_id="ci-003",
            content="def calculate(x): return x * 2",
        )
        redact_sensitive_context_item(item)
        assert item.redacted is False
        assert "calculate" in item.content


class TestRedactSensitiveContextItems:
    def test_multiple_items(self):
        items = [
            ContextItem(context_item_id="a", content="api_key=sk-1234567890abcdef12345678"),
            ContextItem(context_item_id="b", content="safe text"),
        ]
        result = redact_sensitive_context_items(items)
        assert result["total_redacted"] == 1
        assert result["total_scanned"] == 2

    def test_no_secrets(self):
        items = [
            ContextItem(context_item_id="c", content="just normal code"),
        ]
        result = redact_sensitive_context_items(items)
        assert result["total_redacted"] == 0
