import pytest

from agentx_evolve.mcp.mcp_server import (
    build_server_manifest,
    register_mcp_tools,
    start_server,
)


def test_build_server_manifest_has_required_keys():
    manifest = build_server_manifest()
    assert "schema_version" in manifest
    assert "manifest_id" in manifest
    assert "exposed_tools" in manifest
    assert "blocked_tools" in manifest


def test_build_server_manifest_exposed_tools_list():
    manifest = build_server_manifest()
    assert isinstance(manifest["exposed_tools"], list)
    assert len(manifest["exposed_tools"]) > 0


def test_register_mcp_tools_returns_list():
    tools = register_mcp_tools()
    assert isinstance(tools, list)
    for t in tools:
        assert "tool_name" in t
        assert "description" in t
        assert "input_schema" in t


def test_register_mcp_tools_all_exposed_have_names():
    tools = register_mcp_tools()
    names = [t["tool_name"] for t in tools]
    assert "agentx_scan" in names
    assert all(n for n in names)


def test_start_server_raises():
    with pytest.raises(NotImplementedError, match="not implemented"):
        start_server()
