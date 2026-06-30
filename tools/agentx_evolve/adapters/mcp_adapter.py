from __future__ import annotations

from typing import Any

from agentx_evolve.adapters.mcp_contract import MCPDescriptor, SUPPORTED_TRANSPORTS
from agentx_evolve.adapters.tool_result import ToolResult

MCP_ADAPTER_ID = "mcp_shell"


class MCPAdapterShell:
    def __init__(self) -> None:
        self._descriptors: dict[str, MCPDescriptor] = {}

    def register_descriptor(self, descriptor: MCPDescriptor) -> None:
        errors = descriptor.validate()
        if errors:
            raise ValueError(f"invalid MCP descriptor: {'; '.join(errors)}")
        self._descriptors[descriptor.tool_name] = descriptor

    def get_descriptor(self, tool_name: str) -> MCPDescriptor | None:
        return self._descriptors.get(tool_name)

    def validate_call(self, server_id: str, tool_name: str, transport: str) -> dict[str, Any]:
        errors: list[str] = []
        desc = self._descriptors.get(tool_name)
        if not desc:
            errors.append(f"unknown MCP tool: {tool_name}")
            return {"valid": False, "errors": errors}
        if desc.server_id != server_id:
            errors.append(f"unknown MCP server: {server_id}")
        if transport not in SUPPORTED_TRANSPORTS:
            errors.append(f"unsupported transport: {transport}")
        if desc.live_required:
            errors.append("live MCP disabled by default")
        return {"valid": len(errors) == 0, "errors": errors}

    def normalize_result(self, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "tool_name": result.get("tool_name", ""),
            "server_id": result.get("server_id", ""),
            "output": result.get("output", {}),
            "output_hash": result.get("output_hash", ""),
            "status": result.get("status", "DENIED"),
        }

    def list_registered_tools(self) -> list[str]:
        return sorted(self._descriptors.keys())
