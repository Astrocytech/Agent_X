from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MCP_DESCRIPTOR_SCHEMA_VERSION = "adapter.mcp_descriptor.v1"

SUPPORTED_TRANSPORTS = {
    "local_mock_transport",
    "stdio",
    "streamable_http",
    "sse",
    "remote_http",
}
SUPPORTED_AUTH_MODES = {"none", "local_mock", "api_key", "oauth"}

REAL_TRANSPORTS = {"stdio", "streamable_http", "sse", "remote_http"}
TRANSPORT_REQUIRES_NETWORK = {"streamable_http", "sse", "remote_http"}


@dataclass
class MCPDescriptor:
    tool_name: str = ""
    server_id: str = ""
    transport: str = ""
    auth_mode: str = "none"
    capabilities: list[str] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    side_effects: list[str] = field(default_factory=list)
    live_required: bool = False
    replay_mode: str = "deterministic"
    allowed_profiles: list[str] = field(default_factory=list)
    schema_version: str = MCP_DESCRIPTOR_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "server_id": self.server_id,
            "transport": self.transport,
            "auth_mode": self.auth_mode,
            "capabilities": self.capabilities,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "side_effects": self.side_effects,
            "live_required": self.live_required,
            "replay_mode": self.replay_mode,
            "allowed_profiles": self.allowed_profiles,
            "schema_version": self.schema_version,
        }

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.tool_name:
            errors.append("tool_name is required")
        if not self.server_id:
            errors.append("server_id is required")
        if self.transport not in SUPPORTED_TRANSPORTS:
            errors.append(f"unsupported transport: {self.transport}")
        if self.auth_mode not in SUPPORTED_AUTH_MODES:
            errors.append(f"unsupported auth_mode: {self.auth_mode}")
        return errors
