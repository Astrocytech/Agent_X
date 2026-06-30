from __future__ import annotations

import pytest
from agentx_evolve.adapters.tool_adapter import ToolAdapter
from agentx_evolve.adapters.tool_result import ToolCall, ToolResult


class TestToolAdapterInterface:
    def test_interface_has_required_methods(self):
        assert hasattr(ToolAdapter, "describe_capabilities")
        assert hasattr(ToolAdapter, "validate_call")
        assert hasattr(ToolAdapter, "simulate_call")
        assert hasattr(ToolAdapter, "execute_call")
        assert hasattr(ToolAdapter, "normalize_result")

    def test_interface_does_not_implement_execute(self):
        with pytest.raises(TypeError):
            ToolAdapter()

    def test_tool_call_requires_tool_name(self):
        call = ToolCall()
        errors = call.validate()
        assert "tool_name is required" in errors

    def test_tool_call_requires_call_id(self):
        call = ToolCall(tool_name="read")
        errors = call.validate()
        assert "call_id is required" in errors

    def test_tool_call_requires_run_id(self):
        call = ToolCall(tool_name="read", call_id="c1")
        errors = call.validate()
        assert "run_id is required" in errors

    def test_valid_tool_call_passes(self):
        call = ToolCall(tool_name="read", call_id="c1", run_id="r1")
        errors = call.validate()
        assert errors == []

    def test_tool_result_requires_tool_name(self):
        result = ToolResult()
        errors = result.validate()
        assert "tool_name is required" in errors

    def test_tool_result_requires_call_id(self):
        result = ToolResult(tool_name="read")
        errors = result.validate()
        assert "call_id is required" in errors

    def test_tool_result_requires_provenance(self):
        result = ToolResult(tool_name="read", call_id="c1")
        errors = result.validate()
        assert "provenance is required" in errors

    def test_valid_tool_result_passes(self):
        result = ToolResult(tool_name="read", call_id="c1", provenance={"adapter_id": "test"})
        errors = result.validate()
        assert errors == []

    def test_tool_result_auto_hashes(self):
        result = ToolResult(tool_name="read", call_id="c1",
                            output_text="test content", provenance={"adapter_id": "test"})
        assert result.output_hash
