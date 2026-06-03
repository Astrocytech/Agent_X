import pytest
from agentx_evolve.context.context_source_loader import (
    load_context_sources,
)
from agentx_evolve.context.context_models import (
    SOURCE_TRUST_SYSTEM,
    SOURCE_TRUST_BLOCKED,
    SOURCE_TRUST_TOOL_OUTPUT,
    SOURCE_TRUST_UNTRUSTED_TEXT,
)


class TestLoadContextSources:
    def test_approved_source_loads(self):
        requests = [
            {
                "source_id": "src-001",
                "source_type": "IMPLEMENTATION_SPEC",
                "source_component": "ContextBuilderTaskPacker",
                "source_trust_level": SOURCE_TRUST_SYSTEM,
                "allowed_by_policy": True,
            }
        ]
        sources = load_context_sources(requests)
        assert len(sources) == 1
        assert sources[0].source_id == "src-001"
        assert sources[0].allowed_by_policy is True

    def test_blocked_source_excluded(self):
        requests = [
            {
                "source_id": "src-blocked",
                "source_type": "UNKNOWN",
                "source_component": "unknown",
                "source_trust_level": SOURCE_TRUST_BLOCKED,
                "allowed_by_policy": False,
            }
        ]
        sources = load_context_sources(requests)
        assert len(sources) == 1
        assert sources[0].source_trust_level == SOURCE_TRUST_BLOCKED
        assert sources[0].allowed_by_policy is False

    def test_missing_policy_blocks_high_risk_source(self):
        requests = [
            {
                "source_id": "src-tool",
                "source_type": "TOOL_RESULT",
                "source_component": "ToolAdapter",
                "source_trust_level": SOURCE_TRUST_TOOL_OUTPUT,
                "allowed_by_policy": True,
            }
        ]
        sources = load_context_sources(requests, policy_context={"policy_registry_available": False})
        assert len(sources) == 1
        assert sources[0].source_trust_level == SOURCE_TRUST_BLOCKED

    def test_unknown_source_type_warns(self):
        requests = [
            {
                "source_id": "src-unknown",
                "source_type": "ALIEN_TYPE",
                "source_component": "unknown",
                "source_trust_level": SOURCE_TRUST_UNTRUSTED_TEXT,
                "allowed_by_policy": False,
            }
        ]
        sources = load_context_sources(requests)
        assert len(sources) == 1
        assert any("unknown source type" in w for w in sources[0].warnings)

    def test_multiple_sources(self):
        requests = [
            {"source_id": "a", "source_type": "SYSTEM_CONSTRAINT", "source_component": "sys", "source_trust_level": SOURCE_TRUST_SYSTEM, "allowed_by_policy": True},
            {"source_id": "b", "source_type": "TOOL_RESULT", "source_component": "tool", "source_trust_level": SOURCE_TRUST_TOOL_OUTPUT, "allowed_by_policy": True},
        ]
        sources = load_context_sources(requests)
        assert len(sources) == 2

    def test_empty_requests(self):
        sources = load_context_sources([])
        assert sources == []
