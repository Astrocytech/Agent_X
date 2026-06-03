from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolRegistry,
    ROLE_MCP_CLIENT,
    EFFECT_READ,
    utc_now_iso,
    new_id,
)
from agentx_evolve.tools.tool_registry import (
    get_tool_definition,
    list_mcp_exposable_tools,
)
from agentx_evolve.tools.tool_policy import check_tool_permission
from agentx_evolve.tools.invalid_tool import handle_invalid_tool
from agentx_evolve.mcp.mcp_models import (
    MCPToolManifest,
    MCPToolDefinition,
    MCPToolResponse,
    utc_now_iso as mcp_now,
    new_id as mcp_id,
)


def build_mcp_tool_manifest(registry: ToolRegistry) -> dict:
    exposed = list_mcp_exposable_tools(registry)
    manifest = MCPToolManifest(
        manifest_id=mcp_id("mcp_"),
        created_at=mcp_now(),
        exposed_tools=[
            MCPToolDefinition(
                tool_name=t.tool_name,
                description=t.description,
                input_schema={"type": "object"},
            )
            for t in exposed
        ],
        blocked_tools=[
            t.tool_name
            for t in registry.tools
            if not t.enabled
            or t.writes_source
            or t.runs_subprocess
            or t.uses_network
            or t.trust_tier in ("TRUST_TIER_4_GIT_WRITE", "TRUST_TIER_5_NETWORK_OR_EXTERNAL", "TRUST_TIER_6_BLOCKED")
        ],
    )
    return {
        "schema_version": manifest.schema_version,
        "schema_id": manifest.schema_id,
        "manifest_id": manifest.manifest_id,
        "created_at": manifest.created_at,
        "source_component": manifest.source_component,
        "exposed_tools": [
            {"tool_name": t.tool_name, "description": t.description, "input_schema": t.input_schema}
            for t in manifest.exposed_tools
        ],
        "blocked_tools": manifest.blocked_tools,
    }


def handle_mcp_tool_request(
    tool_name: str,
    arguments: dict,
    caller_context: dict,
    registry: ToolRegistry,
    policy_context: dict,
) -> dict:
    tool_def = get_tool_definition(registry, tool_name)
    if tool_def is None:
        result = handle_invalid_tool({"tool_name": tool_name, "caller_role": ROLE_MCP_CLIENT})
        return _to_mcp_response(result)

    if tool_def.writes_source or tool_def.runs_subprocess or tool_def.uses_network:
        return MCPToolResponse(
            status="BLOCKED",
            message=f"MCP client cannot call {tool_name}: blocked by MCP exposure rules",
            failure_class="MCP_TOOL_BLOCKED",
        ).__dict__

    tool_call = ToolCall(
        tool_call_id=new_id("call_"),
        timestamp=utc_now_iso(),
        source_component="MCPAdapter",
        caller_role=ROLE_MCP_CLIENT,
        caller_id=caller_context.get("caller_id"),
        session_id=caller_context.get("session_id"),
        tool_name=tool_name,
        arguments=arguments,
        requested_effect=EFFECT_READ,
    )

    permission = check_tool_permission(tool_call, tool_def, policy_context)
    if permission.decision != "ALLOW":
        return MCPToolResponse(
            status="BLOCKED",
            message=permission.reason,
            failure_class="MCP_TOOL_BLOCKED",
            warnings=permission.warnings,
            errors=permission.errors,
        ).__dict__

    return MCPToolResponse(
        status="ALLOWED",
        message=f"MCP request for {tool_name} has passed policy checks",
        data={"tool_name": tool_name, "arguments": arguments},
    ).__dict__


def _to_mcp_response(result) -> dict:
    return MCPToolResponse(
        status=result.status if hasattr(result, "status") else "INVALID",
        message=result.message if hasattr(result, "message") else "Invalid tool call",
        data=result.data if hasattr(result, "data") else {},
        failure_class=result.failure_class if hasattr(result, "failure_class") else "MCP_REQUEST_INVALID",
        warnings=getattr(result, "warnings", []),
        errors=getattr(result, "errors", []),
    ).__dict__
