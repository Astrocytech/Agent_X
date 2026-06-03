from __future__ import annotations
import json
from typing import Any
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, TS_SUCCESS,
    new_id, utc_now_iso,
)
from agentx_evolve.tool.tool_registry import ToolRegistry


class MCPServer:
    def __init__(self, registry: ToolRegistry, name: str = "agentx-mcp"):
        self._registry = registry
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def list_tools(self) -> list[dict]:
        return [d.to_dict() for d in self._registry.list_tools()]

    def call_tool(self, tool_name: str, arguments: dict[str, Any], session_id: str = "") -> dict:
        result = self._registry.call_tool(tool_name, arguments, session_id)
        return result.to_simple_dict()

    def handle_json_request(self, request: dict) -> dict:
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id", new_id("req"))
        if method == "list_tools":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.list_tools()},
            }
        if method == "call_tool":
            tool_name = params.get("tool_name", "")
            arguments = params.get("arguments", {})
            session_id = params.get("session_id", "")
            result = self.call_tool(tool_name, arguments, session_id)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            }
        if method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"status": "pong", "server": self._name},
            }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
