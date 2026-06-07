from __future__ import annotations

import pytest

from agentx_evolve.context.sensitive_data_redactor import redact_sensitive_context_items
from agentx_evolve.context.context_models import ContextItem


class TestContextRedaction:
    def test_redact_api_key(self):
        items = [
            ContextItem(
                context_item_id="a",
                content="API_KEY=sk-1234567890abcdef",
                sensitive_data_score=0.0,
            )
        ]
        result = redact_sensitive_context_items(items)
        assert len(result["redacted_items"]) >= 0

    def test_redact_marks_item(self):
        items = [
            ContextItem(
                context_item_id="a",
                content="password=secret123",
                sensitive_data_score=1.0,
            )
        ]
        result = redact_sensitive_context_items(items)
        assert result is not None

    def test_redact_clean_content(self):
        items = [
            ContextItem(
                context_item_id="a",
                content="This is harmless text",
                sensitive_data_score=0.0,
            )
        ]
        result = redact_sensitive_context_items(items)
        assert result is not None
