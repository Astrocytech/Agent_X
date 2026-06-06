"""
[DEPRECATED] agentx_evolve.tool — legacy v1 tool runtime.

This package is the v1 (class-based OO runtime) tool system.
It has been superseded by the v2 tool system at ``agentx_evolve.tools``
(data-schema + pure-functions with trust-tier security model).

New code should import from ``agentx_evolve.tools`` instead.
This package is preserved for existing consumers and will be removed
in a future release after all consumers are migrated.
"""
import warnings
warnings.warn(
    "agentx_evolve.tool is deprecated; use agentx_evolve.tools instead",
    DeprecationWarning, stacklevel=2,
)

from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter, ToolStatus,
    TS_SUCCESS, TS_PARTIAL, TS_BLOCKED, TS_FAILED, TS_INVALID,
    ALL_TOOL_STATUSES,
)
from agentx_evolve.tool.tool_registry import ToolRegistry, ToolAuditEntry
from agentx_evolve.tool.tool_policy import (
    ToolPolicyEnforcer, ToolPolicyRule, ToolPolicyResult,
    POLICY_DECISION_ALLOW, POLICY_DECISION_BLOCK, POLICY_DECISION_REQUIRE_APPROVAL,
)
from agentx_evolve.tool.mcp_server import MCPServer

__all__ = [
    "ToolDefinition", "ToolCall", "ToolResult", "ToolParameter", "ToolStatus",
    "TS_SUCCESS", "TS_PARTIAL", "TS_BLOCKED", "TS_FAILED", "TS_INVALID",
    "ALL_TOOL_STATUSES",
    "ToolRegistry", "ToolAuditEntry",
    "ToolPolicyEnforcer", "ToolPolicyRule", "ToolPolicyResult",
    "POLICY_DECISION_ALLOW", "POLICY_DECISION_BLOCK", "POLICY_DECISION_REQUIRE_APPROVAL",
    "MCPServer",
]
