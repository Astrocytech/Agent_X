import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.mcp.mcp_adapter import (
    handle_mcp_tool_request, build_mcp_tool_manifest,
)
from agentx_evolve.tools.tool_registry import load_default_tool_registry
from agentx_evolve.tools.tool_models import (
    ToolRegistry, ToolDefinition, TRUST_TIER_0_READ_ONLY, EFFECT_READ,
)
from agentx_evolve.mcp.mcp_models import MCPToolResponse


class TestToolMcpPolicyFlow:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.registry = load_default_tool_registry()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_allowed_read_only_tool_succeeds(self):
        caller_ctx = {"caller_id": "mcp-test", "session_id": "sess-1"}
        result = handle_mcp_tool_request(
            "agentx_status", {}, caller_ctx, self.registry, {},
        )
        assert isinstance(result, dict)
        assert result.get("status") in ("ALLOWED", "BLOCKED")

    def test_unknown_tool_fails_closed(self):
        caller_ctx = {"caller_id": "mcp-test", "session_id": "sess-1"}
        result = handle_mcp_tool_request(
            "non_existent_tool", {}, caller_ctx, self.registry, {},
        )
        assert result.get("status") in ("BLOCKED", "INVALID")

    def test_denied_tool_fails_closed(self):
        caller_ctx = {"caller_id": "mcp-test", "session_id": "sess-1"}
        result = handle_mcp_tool_request(
            "patch_apply_guarded", {}, caller_ctx, self.registry, {},
        )
        assert result.get("status") == "BLOCKED"

    def test_tool_audit_artifact_is_schema_valid(self):
        manifest = build_mcp_tool_manifest(self.registry)
        assert "manifest_id" in manifest
        assert "created_at" in manifest
        assert "exposed_tools" in manifest
        assert "blocked_tools" in manifest
        for tool in manifest["exposed_tools"]:
            assert "tool_name" in tool
            assert "description" in tool
