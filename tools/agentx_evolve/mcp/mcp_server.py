from __future__ import annotations

from agentx_evolve.tools.tool_registry import (
    load_default_tool_registry,
    list_mcp_exposable_tools,
)
from agentx_evolve.mcp.mcp_adapter import build_mcp_tool_manifest


def build_server_manifest() -> dict:
    registry = load_default_tool_registry()
    return build_mcp_tool_manifest(registry)


def register_mcp_tools() -> list[dict]:
    registry = load_default_tool_registry()
    exposed = list_mcp_exposable_tools(registry)
    return [
        {
            "tool_name": t.tool_name,
            "description": t.description,
            "input_schema": {"type": "object"},
        }
        for t in exposed
    ]

