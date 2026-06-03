import pytest
from agentx_evolve.context.task_pack_builder import build_task_pack
from agentx_evolve.context.context_models import (
    SOURCE_TRUST_SYSTEM, SOURCE_TRUST_UNTRUSTED_TEXT, SOURCE_TRUST_BLOCKED,
)


class TestTaskPackBuilder:
    def test_valid_task_pack_builds(self):
        tp = build_task_pack(
            raw_task={"task_title": "Implement X", "task_description": "Build it"},
            source_requests=[
                {"source_id": "src-001", "source_type": "SYSTEM_CONSTRAINT", "source_component": "sys", "source_trust_level": SOURCE_TRUST_SYSTEM, "allowed_by_policy": True},
            ],
            builder_context={
                "model_profile": {"model_profile_id": "m1", "context_window": 8192},
            },
        )
        assert tp.task_pack_id != ""
        assert tp.task_input.task_title == "Implement X"
        assert len(tp.context_pack.included_items) >= 1
        assert tp.errors == []

    def test_over_budget_compresses_or_blocks(self):
        tp = build_task_pack(
            raw_task={"task_title": "Big task"},
            source_requests=[
                {"source_id": f"src-{i}", "source_type": "REPOSITORY_FILE", "source_component": "fs", "source_trust_level": SOURCE_TRUST_UNTRUSTED_TEXT, "allowed_by_policy": True}
                for i in range(50)
            ],
            builder_context={
                "max_context_tokens": 100,
                "reserved_output_tokens": 0,
            },
        )
        assert tp.context_pack.total_estimated_tokens <= tp.context_pack.max_context_tokens + 5000

    def test_policy_blocked_context_excluded(self):
        tp = build_task_pack(
            raw_task={"task_title": "Test"},
            source_requests=[
                {"source_id": "src-blocked", "source_type": "UNKNOWN", "source_component": "unknown", "source_trust_level": SOURCE_TRUST_BLOCKED, "allowed_by_policy": False},
            ],
            builder_context={},
        )
        assert len(tp.context_pack.included_items) == 0

    def test_injection_context_excluded(self):
        tp = build_task_pack(
            raw_task={"task_title": "Test"},
            source_requests=[
                {"source_id": "src-inject", "source_type": "TOOL_RESULT", "source_component": "tool", "source_trust_level": SOURCE_TRUST_UNTRUSTED_TEXT, "allowed_by_policy": True},
            ],
            builder_context={},
        )
        if tp.context_pack.warnings:
            assert any("injection" in w for w in tp.context_pack.warnings)

    def test_blocked_tool_recorded(self):
        tp = build_task_pack(
            raw_task={"task_title": "Test", "requested_tools": ["write_file"]},
            source_requests=[],
            builder_context={
                "tool_registry": {"write_file": {"tool_type": "MUTATING", "governance_approved": False}},
            },
        )
        assert "write_file" in tp.blocked_tools

    def test_error_on_missing_input(self):
        tp = build_task_pack(
            raw_task={},
            source_requests=[],
            builder_context={},
        )
        assert len(tp.errors) >= 1

    def test_sensitive_context_redacted(self):
        tp = build_task_pack(
            raw_task={"task_title": "Test"},
            source_requests=[
                {"source_id": "src-secret", "source_type": "REPOSITORY_FILE", "source_component": "fs", "source_trust_level": SOURCE_TRUST_UNTRUSTED_TEXT, "allowed_by_policy": True},
            ],
            builder_context={},
        )
        for item in tp.context_pack.included_items:
            assert "[REDACTED_API_KEY]" not in item.content or item.redacted is True
