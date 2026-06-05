import pytest

from agentx_evolve.mcp.mcp_adapter import (
    build_mcp_tool_manifest,
    handle_mcp_tool_request,
)
from agentx_evolve.tools.tool_registry import load_default_tool_registry


@pytest.fixture
def registry():
    return load_default_tool_registry()


def test_build_mcp_tool_manifest_has_required_keys(registry):
    manifest = build_mcp_tool_manifest(registry)
    assert "schema_version" in manifest
    assert "manifest_id" in manifest
    assert "exposed_tools" in manifest
    assert "blocked_tools" in manifest


def test_build_mcp_tool_manifest_exposed_tools(registry):
    manifest = build_mcp_tool_manifest(registry)
    for t in manifest["exposed_tools"]:
        assert "tool_name" in t
        assert "description" in t
        assert "input_schema" in t


def test_build_mcp_tool_manifest_blocked_not_empty(registry):
    manifest = build_mcp_tool_manifest(registry)
    assert len(manifest["blocked_tools"]) > 0


def test_build_mcp_tool_manifest_has_id(registry):
    manifest = build_mcp_tool_manifest(registry)
    assert manifest["manifest_id"].startswith("mcp_")


def test_handle_mcp_tool_request_unknown_tool(registry):
    result = handle_mcp_tool_request("nonexistent", {}, {"caller_id": "test"}, registry, {})
    assert result["status"] == "INVALID" or result.get("failure_class") is not None


def test_handle_mcp_tool_request_blocked_tool(registry):
    result = handle_mcp_tool_request("git_create_branch", {}, {"caller_id": "test"}, registry, {})
    assert result.get("status") == "BLOCKED" or result.get("failure_class") == "MCP_TOOL_BLOCKED"


def test_handle_mcp_tool_request_allows_read_only(registry):
    result = handle_mcp_tool_request("agentx_scan", {}, {"caller_id": "test", "session_id": "sess_1"}, registry, {})
    assert result["status"] == "ALLOWED"


def test_handle_mcp_tool_request_returns_valid_response(registry):
    result = handle_mcp_tool_request("agentx_scan", {"action": "list"}, {"caller_id": "test"}, registry, {})
    assert "status" in result
    assert "message" in result
    assert "data" in result or "failure_class" in result
