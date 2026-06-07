"""Negative test pack — prove forbidden actions fail closed."""

import pytest

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    ToolPermissionDecision,
    STATUS_BLOCKED,
    STATUS_INVALID,
    DECISION_BLOCK,
    ROLE_UNKNOWN_CALLER,
    TRUST_TIER_6_BLOCKED,
)
from agentx_evolve.tools.invalid_tool import handle_invalid_tool
from agentx_evolve.tools.tool_policy import check_tool_permission
from agentx_evolve.tools.tool_registry import load_default_tool_registry, get_tool_definition


class TestUnknownTool:
    def test_unknown_tool_returns_invalid(self):
        result = handle_invalid_tool({"tool_name": "nonexistent_tool"})
        assert result.status == STATUS_INVALID
        assert result.failure_class == "TOOL_NOT_FOUND"

    def test_malformed_call_returns_invalid(self):
        result = handle_invalid_tool(None)
        assert result.status == STATUS_INVALID
        assert result.failure_class is not None

    def test_invalid_tool_does_not_execute_shell(self):
        result = handle_invalid_tool({"tool_name": "rm -rf /"})
        assert result.status == STATUS_INVALID


class TestBlockedTool:
    def test_disabled_tool_blocked(self):
        registry = load_default_tool_registry()
        td = get_tool_definition(registry, "patch_apply_guarded")
        assert td is not None
        tc = ToolCall(tool_name="patch_apply_guarded", caller_role="ORCHESTRATOR")
        result = check_tool_permission(tc, td, {})
        assert result.decision == DECISION_BLOCK

    def test_blocked_tier_tool_blocked(self):
        from agentx_evolve.tools.tool_models import ToolDefinition
        td = ToolDefinition(tool_name="blocked_tool", trust_tier=TRUST_TIER_6_BLOCKED, enabled=True)
        tc = ToolCall(tool_name="blocked_tool", caller_role="ORCHESTRATOR")
        result = check_tool_permission(tc, td, {})
        assert result.decision == DECISION_BLOCK

    def test_unknown_caller_blocked(self):
        from agentx_evolve.tools.tool_models import ToolDefinition
        td = ToolDefinition(tool_name="test_tool", enabled=True)
        tc = ToolCall(tool_name="test_tool", caller_role=ROLE_UNKNOWN_CALLER)
        result = check_tool_permission(tc, td, {})
        assert result.decision == DECISION_BLOCK


class TestPatchBlocked:
    def test_patch_apply_returns_blocked(self):
        from agentx_evolve.tools.patch_tools import patch_apply_guarded
        result = patch_apply_guarded({}, {})
        assert result.status == STATUS_BLOCKED

    def test_rollback_returns_blocked(self):
        from agentx_evolve.tools.patch_tools import rollback_session
        result = rollback_session({}, {})
        assert result.status == STATUS_BLOCKED


class TestGitWriteBlocked:
    @pytest.mark.parametrize("tool_name", [
        "git_create_branch", "git_stage_approved",
        "git_commit_approved", "git_push",
    ])
    def test_git_write_tools_blocked(self, tool_name):
        registry = load_default_tool_registry()
        td = get_tool_definition(registry, tool_name)
        assert td is not None
        assert not td.enabled


class TestPermissionDenial:
    def test_effect_mismatch_blocked(self):
        from agentx_evolve.tools.tool_models import ToolDefinition
        td = ToolDefinition(
            tool_name="read_only_tool",
            enabled=True,
            requested_effects=["READ"],
        )
        tc = ToolCall(tool_name="read_only_tool", caller_role="ORCHESTRATOR", requested_effect="WRITE")
        result = check_tool_permission(tc, td, {})
        assert result.decision == DECISION_BLOCK

    def test_role_mismatch_blocked(self):
        from agentx_evolve.tools.tool_models import ToolDefinition
        td = ToolDefinition(
            tool_name="agent_tool",
            enabled=True,
            allowed_roles=["ORCHESTRATOR"],
        )
        tc = ToolCall(tool_name="agent_tool", caller_role="MCP_CLIENT")
        result = check_tool_permission(tc, td, {})
        assert result.decision == DECISION_BLOCK
