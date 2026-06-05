from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

SPEC_SCHEMA_VERSION = "1.0"
SOURCE_COMPONENT = "MCPAdapter"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}{uuid4().hex}"
    return uuid4().hex


@dataclass
class MCPToolDefinition:
    tool_name: str = ""
    description: str = ""
    input_schema: dict = field(default_factory=dict)


@dataclass
class MCPToolManifest:
    schema_version: str = SPEC_SCHEMA_VERSION
    schema_id: str = "mcp_tool_manifest.schema.json"
    manifest_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    exposed_tools: list[MCPToolDefinition] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class MCPToolRequest:
    tool_name: str = ""
    arguments: dict = field(default_factory=dict)
    caller_context: dict = field(default_factory=dict)


@dataclass
class MCPToolResponse:
    status: str = ""
    message: str = ""
    data: dict = field(default_factory=dict)
    failure_class: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
