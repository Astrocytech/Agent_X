import pytest

from agentx_evolve.mcp.mcp_models import (
    SPEC_SCHEMA_VERSION, SOURCE_COMPONENT,
    utc_now_iso, new_id,
    MCPToolDefinition, MCPToolManifest,
    MCPToolRequest, MCPToolResponse,
)


def test_constants():
    assert SPEC_SCHEMA_VERSION == "1.0"
    assert SOURCE_COMPONENT == "MCPAdapter"


def test_utc_now_iso():
    now = utc_now_iso()
    assert "T" in now
    assert now.endswith("Z") or "+" in now


def test_new_id_with_prefix():
    nid = new_id("test")
    assert nid.startswith("test")
    assert len(nid) > len("test")


def test_new_id_without_prefix():
    nid = new_id()
    assert isinstance(nid, str)
    assert len(nid) > 0


def test_mcp_tool_definition_defaults():
    d = MCPToolDefinition()
    assert d.tool_name == ""
    assert d.description == ""
    assert d.input_schema == {}


def test_mcp_tool_definition_custom():
    d = MCPToolDefinition(
        tool_name="read_file",
        description="Read a file from disk",
        input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
    )
    assert d.tool_name == "read_file"
    assert d.input_schema["type"] == "object"


def test_mcp_tool_manifest_defaults():
    m = MCPToolManifest()
    assert m.schema_version == SPEC_SCHEMA_VERSION
    assert m.schema_id == "mcp_tool_manifest.schema.json"
    assert m.manifest_id == ""
    assert m.source_component == SOURCE_COMPONENT
    assert m.exposed_tools == []
    assert m.blocked_tools == []


def test_mcp_tool_manifest_with_tools():
    tool = MCPToolDefinition(tool_name="write_file")
    m = MCPToolManifest(
        manifest_id="m-1",
        exposed_tools=[tool],
        blocked_tools=["delete_file"],
    )
    assert m.manifest_id == "m-1"
    assert len(m.exposed_tools) == 1
    assert m.exposed_tools[0].tool_name == "write_file"
    assert "delete_file" in m.blocked_tools


def test_mcp_tool_request_defaults():
    r = MCPToolRequest()
    assert r.tool_name == ""
    assert r.arguments == {}
    assert r.caller_context == {}


def test_mcp_tool_request_custom():
    r = MCPToolRequest(
        tool_name="search_code",
        arguments={"query": "foo"},
        caller_context={"session_id": "s-1"},
    )
    assert r.tool_name == "search_code"
    assert r.arguments["query"] == "foo"


def test_mcp_tool_response_defaults():
    r = MCPToolResponse()
    assert r.status == ""
    assert r.message == ""
    assert r.data == {}
    assert r.failure_class is None
    assert r.warnings == []
    assert r.errors == []


def test_mcp_tool_response_custom():
    r = MCPToolResponse(
        status="SUCCESS",
        message="Tool completed",
        data={"result": "ok"},
        failure_class=None,
        warnings=["deprecated"],
        errors=[],
    )
    assert r.status == "SUCCESS"
    assert r.data["result"] == "ok"
    assert r.warnings == ["deprecated"]
