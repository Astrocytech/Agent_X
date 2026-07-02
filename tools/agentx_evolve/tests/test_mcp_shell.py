from __future__ import annotations

import pytest
from agentx_evolve.adapters.mcp_contract import MCPDescriptor, MCP_DESCRIPTOR_SCHEMA_VERSION
from agentx_evolve.adapters.mcp_adapter import MCPAdapterShell, MCP_ADAPTER_ID


class TestMCPAdapter:
    def setup_method(self):
        self.adapter = MCPAdapterShell()
        self.desc = MCPDescriptor(
            tool_name="test_tool",
            server_id="test_server",
            transport="local_mock_transport",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )

    def test_register_descriptor(self):
        self.adapter.register_descriptor(self.desc)
        retrieved = self.adapter.get_descriptor("test_tool")
        assert retrieved is not None
        assert retrieved.tool_name == "test_tool"

    def test_get_descriptor_returns_none_for_unknown(self):
        assert self.adapter.get_descriptor("nonexistent") is None

    def test_validate_call_accepts_valid(self):
        self.adapter.register_descriptor(self.desc)
        result = self.adapter.validate_call("test_server", "test_tool", "local_mock_transport")
        assert result["valid"] is True

    def test_validate_call_rejects_unknown_tool(self):
        result = self.adapter.validate_call("srv", "nonexistent", "local_mock_transport")
        assert result["valid"] is False

    def test_validate_call_rejects_unknown_server(self):
        self.adapter.register_descriptor(self.desc)
        result = self.adapter.validate_call("wrong_server", "test_tool", "local_mock_transport")
        assert result["valid"] is False

    def test_list_registered_tools(self):
        self.adapter.register_descriptor(self.desc)
        tools = self.adapter.list_registered_tools()
        assert "test_tool" in tools

    def test_normalize_result_adds_status_default(self):
        raw = {"tool_name": "test_tool", "server_id": "srv", "output": {"result": "ok"}, "output_hash": "abc"}
        normalized = self.adapter.normalize_result(raw)
        assert normalized["tool_name"] == "test_tool"
        assert normalized["status"] == "DENIED"

    def test_normalize_result_overwrites_status(self):
        raw = {"tool_name": "test_tool", "server_id": "srv", "output": {}, "output_hash": "abc", "status": "SUCCESS"}
        normalized = self.adapter.normalize_result(raw)
        assert normalized["status"] == "SUCCESS"

    def test_mcp_descriptor_requires_tool_name(self):
        desc = MCPDescriptor()
        errors = desc.validate()
        assert "tool_name is required" in errors

    def test_mcp_descriptor_requires_server_id(self):
        desc = MCPDescriptor(tool_name="t")
        errors = desc.validate()
        assert "server_id is required" in errors

    def test_mcp_descriptor_requires_valid_transport(self):
        desc = MCPDescriptor(tool_name="t", server_id="s", transport="bad")
        errors = desc.validate()
        assert any("transport" in e for e in errors)

    def test_mcp_descriptor_to_dict(self):
        d = self.desc.to_dict()
        assert d["tool_name"] == "test_tool"
        assert d["server_id"] == "test_server"

    def test_real_transport_stdio_supported(self):
        from agentx_evolve.adapters.mcp_contract import SUPPORTED_TRANSPORTS
        assert "stdio" in SUPPORTED_TRANSPORTS

    def test_real_transport_streamable_http_supported(self):
        from agentx_evolve.adapters.mcp_contract import SUPPORTED_TRANSPORTS
        assert "streamable_http" in SUPPORTED_TRANSPORTS

    def test_real_transport_sse_supported(self):
        from agentx_evolve.adapters.mcp_contract import SUPPORTED_TRANSPORTS
        assert "sse" in SUPPORTED_TRANSPORTS

    def test_real_transport_remote_http_supported(self):
        from agentx_evolve.adapters.mcp_contract import SUPPORTED_TRANSPORTS
        assert "remote_http" in SUPPORTED_TRANSPORTS

    def test_transport_runner_mock_execute(self):
        from agentx_evolve.adapters.mcp_adapter import MCPTransportRunner
        runner = MCPTransportRunner()
        result = runner.execute("test_tool", "test_server", "local_mock_transport", {"key": "val"})
        assert result["status"] == "SUCCESS"
        assert result["output"]["mock"] is True

    def test_transport_runner_stdio_not_found(self):
        from agentx_evolve.adapters.mcp_adapter import MCPTransportRunner
        runner = MCPTransportRunner()
        result = runner.execute("tool", "nonexistent_mcp_server_binary", "stdio", {})
        assert result["status"] == "EXECUTION_ERROR"

    def test_transport_runner_network_transports_blocked(self):
        from agentx_evolve.adapters.mcp_adapter import MCPTransportRunner
        runner = MCPTransportRunner()
        for transport in ("streamable_http", "sse", "remote_http"):
            result = runner.execute("tool", "server", transport, {})
            assert result["status"] == "BLOCKED", f"{transport} should be BLOCKED"

    def test_execute_tool_with_real_transport(self):
        self.adapter.register_descriptor(self.desc)
        result = self.adapter.execute_tool("test_tool", "test_server", "local_mock_transport", {"a": 1})
        assert result["status"] == "SUCCESS"

    def test_execute_tool_blocked_on_validation_failure(self):
        result = self.adapter.execute_tool("nonexistent", "srv", "local_mock_transport", {})
        assert result["status"] == "BLOCKED"
