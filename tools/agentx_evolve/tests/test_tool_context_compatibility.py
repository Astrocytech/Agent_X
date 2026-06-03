import pytest
from agentx_evolve.context.tool_context_compatibility import check_tool_context_compatibility
from agentx_evolve.context.context_models import TaskInput, ContextPack


class TestToolContextCompatibility:
    def test_read_only_tool_allowed(self):
        ti = TaskInput(task_input_id="ti-001", task_title="test", requested_tools=["read_file"])
        cp = ContextPack(context_pack_id="cp-001", task_input_id="ti-001", max_context_tokens=4096)
        registry = {"read_file": {"tool_type": "READ_ONLY"}}
        result = check_tool_context_compatibility(ti, cp, registry)
        assert "read_file" in result["allowed_tools"]
        assert len(result["blocked_tools"]) == 0

    def test_unknown_tool_blocked(self):
        ti = TaskInput(task_input_id="ti-002", task_title="test", requested_tools=["unknown_tool"])
        cp = ContextPack(context_pack_id="cp-002", task_input_id="ti-002", max_context_tokens=4096)
        result = check_tool_context_compatibility(ti, cp, {})
        assert "unknown_tool" in result["blocked_tools"]

    def test_mutating_tool_without_governance_blocked(self):
        ti = TaskInput(task_input_id="ti-003", task_title="test", requested_tools=["write_file"])
        cp = ContextPack(context_pack_id="cp-003", task_input_id="ti-003", max_context_tokens=4096)
        registry = {"write_file": {"tool_type": "MUTATING", "governance_approved": False}}
        result = check_tool_context_compatibility(ti, cp, registry)
        assert "write_file" in result["blocked_tools"]

    def test_mutating_tool_with_governance_allowed(self):
        ti = TaskInput(task_input_id="ti-004", task_title="test", requested_tools=["write_file"])
        cp = ContextPack(context_pack_id="cp-004", task_input_id="ti-004", max_context_tokens=4096)
        registry = {"write_file": {"tool_type": "MUTATING", "governance_approved": True}}
        result = check_tool_context_compatibility(ti, cp, registry)
        assert "write_file" in result["allowed_tools"]

    def test_mixed_tools(self):
        ti = TaskInput(task_input_id="ti-005", task_title="test", requested_tools=["read_file", "write_file", "ghost"])
        cp = ContextPack(context_pack_id="cp-005", task_input_id="ti-005", max_context_tokens=4096)
        registry = {
            "read_file": {"tool_type": "READ_ONLY"},
            "write_file": {"tool_type": "MUTATING", "governance_approved": False},
        }
        result = check_tool_context_compatibility(ti, cp, registry)
        assert "read_file" in result["allowed_tools"]
        assert "write_file" in result["blocked_tools"]
        assert "ghost" in result["blocked_tools"]
