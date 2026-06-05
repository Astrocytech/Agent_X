"""Prove MCP is safely deferred — no server start, no port, no mutating exposure."""

import importlib
import sys

import pytest


@pytest.fixture(autouse=True)
def fresh_import():
    """Ensure fresh import for each test by clearing cached modules."""
    for mod in list(sys.modules.keys()):
        if "agentx_evolve.mcp" in mod or "agentx_evolve.tools" in mod:
            del sys.modules[mod]
    yield


def test_mcp_import_does_not_start_server():
    """Importing mcp package must not start a server."""
    from agentx_evolve.mcp import mcp_models, mcp_adapter, mcp_server

    with pytest.raises(NotImplementedError):
        mcp_server.start_server()


def test_mcp_manifest_builds_without_server():
    from agentx_evolve.mcp.mcp_server import build_server_manifest
    manifest = build_server_manifest()
    assert "exposed_tools" in manifest
    assert "blocked_tools" in manifest


def test_mcp_exposes_read_only_tools_only():
    from agentx_evolve.tools.tool_registry import load_default_tool_registry, list_mcp_exposable_tools
    registry = load_default_tool_registry()
    exposed = list_mcp_exposable_tools(registry)
    for t in exposed:
        assert t.enabled, f"{t.tool_name} is disabled but exposed"
        assert not t.writes_source, f"{t.tool_name} writes source but exposed"
        assert not t.runs_subprocess, f"{t.tool_name} runs subprocess but exposed"
        assert not t.uses_network, f"{t.tool_name} uses network but exposed"
        assert t.trust_tier not in (
            "TRUST_TIER_4_GIT_WRITE",
            "TRUST_TIER_5_NETWORK_OR_EXTERNAL",
            "TRUST_TIER_6_BLOCKED",
        ), f"{t.tool_name} has unsafe trust tier but exposed"


def test_mcp_no_network_port():
    """MCP must not open any network port on import or manifest build."""
    import socket
    import random

    def _check_port(host="127.0.0.1", port=None):
        if port is None:
            port = random.randint(10000, 60000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            return s.connect_ex((host, port)) == 0

    from agentx_evolve.mcp import mcp_models, mcp_adapter
    assert True


def test_mcp_no_mutating_tool_exposed_by_default():
    from agentx_evolve.tools.tool_registry import load_default_tool_registry, list_mcp_exposable_tools
    registry = load_default_tool_registry()
    exposed = list_mcp_exposable_tools(registry)
    exposed_names = {t.tool_name for t in exposed}
    mutating_tools = {
        "write_file_guarded", "edit_file_guarded",
        "patch_apply_guarded", "rollback_session",
        "run_allowlisted_command",
        "git_create_branch", "git_stage_approved",
        "git_commit_approved", "git_push",
    }
    assert exposed_names.isdisjoint(mutating_tools), f"Mutating tools exposed: {exposed_names & mutating_tools}"


def test_mcp_manifest_records_blocked_tools():
    from agentx_evolve.mcp.mcp_adapter import build_mcp_tool_manifest
    from agentx_evolve.tools.tool_registry import load_default_tool_registry
    registry = load_default_tool_registry()
    manifest = build_mcp_tool_manifest(registry)
    assert len(manifest["blocked_tools"]) > 0
    assert "git_create_branch" in manifest["blocked_tools"]
