from __future__ import annotations

import pytest

from agentx_evolve.context.context_models import (
    ContextSource,
    SOURCE_TRUST_SYSTEM,
    SOURCE_TRUST_UNTRUSTED_TEXT,
    SOURCE_TRUST_BLOCKED,
    to_dict,
)


class TestContextSourceSchema:
    def test_source_defaults(self):
        s = ContextSource()
        assert s.schema_version == "1.0"
        assert s.schema_id == "context_source.schema.json"
        assert s.source_trust_level == SOURCE_TRUST_UNTRUSTED_TEXT

    def test_source_with_trust_level(self):
        s = ContextSource(source_trust_level=SOURCE_TRUST_SYSTEM)
        assert s.source_trust_level == SOURCE_TRUST_SYSTEM

    def test_source_serializes(self):
        s = ContextSource(
            source_id="src_001",
            source_type="file",
            source_path="/tmp/file.txt",
            source_component="TestComponent",
            source_trust_level=SOURCE_TRUST_SYSTEM,
        )
        d = to_dict(s)
        assert d["source_id"] == "src_001"
        assert d["source_type"] == "file"

    def test_source_blocked_trust(self):
        s = ContextSource(source_trust_level=SOURCE_TRUST_BLOCKED)
        assert s.source_trust_level == SOURCE_TRUST_BLOCKED
        assert s.allowed_by_policy is False
