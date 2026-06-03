import pytest
from agentx_evolve.tools.tool_models import (
    ToolDefinition, ToolCall, ToolResult,
    STATUS_SUCCESS, STATUS_PARTIAL, STATUS_BLOCKED, STATUS_FAILED, STATUS_INVALID,
    ALL_STATUSES, new_id, utc_now_iso, to_dict,
)
from agentx_evolve.tools.tool_registry import (
    register_tool, get_tool_definition,
    list_enabled_tools, load_default_tool_registry,
)
from agentx_evolve.tools.tool_policy import check_tool_permission
from agentx_evolve.tools.initiator_tools import (
    agentx_scan, agentx_status, agentx_plan, agentx_propose,
    agentx_validate, agentx_report,
    agentx_graph_build, agentx_graph_status, agentx_graph_query,
)
from agentx_evolve.tools.patch_tools import (
    patch_session_status, patch_apply_guarded, rollback_session,
)
from agentx_evolve.tools.git_tools import git_status, git_diff


# ---------------------------------------------------------------------------
# tool_models tests
# ---------------------------------------------------------------------------

def test_tool_definition_defaults():
    d = ToolDefinition()
    assert d.tool_name == ""
    assert d.enabled


def test_tool_definition_custom():
    d = ToolDefinition(
        tool_name="test_tool",
        description="A test tool",
        requires_human_approval=True,
    )
    assert d.tool_name == "test_tool"
    assert d.requires_human_approval


def test_tool_definition_to_dict():
    d = ToolDefinition(tool_name="t1")
    dd = to_dict(d)
    assert dd["tool_name"] == "t1"
    assert dd["schema_version"] == "1.0"


def test_tool_call_defaults():
    c = ToolCall()
    assert c.tool_name == ""
    assert c.arguments == {}


def test_tool_call_custom():
    c = ToolCall(tool_name="scan", arguments={"path": "."}, session_id="s1")
    assert c.tool_name == "scan"
    assert c.arguments["path"] == "."
    assert c.session_id == "s1"


def test_tool_result_defaults():
    r = ToolResult()
    assert r.status == STATUS_BLOCKED
    assert r.data == {}


def test_tool_result_custom():
    r = ToolResult(status=STATUS_FAILED, message="error", errors=["fail"])
    assert r.status == STATUS_FAILED
    assert r.errors == ["fail"]


def test_all_statuses():
    assert len(ALL_STATUSES) == 5
    assert STATUS_SUCCESS in ALL_STATUSES
    assert STATUS_INVALID in ALL_STATUSES


def test_helpers():
    nid = new_id("tool")
    assert nid.startswith("tool")
    iso = utc_now_iso()
    assert "T" in iso


# ---------------------------------------------------------------------------
# ToolRegistry tests
# ---------------------------------------------------------------------------

def test_default_registry():
    reg = load_default_tool_registry()
    assert len(reg.tools) > 0


def test_register_and_get_tool():
    reg = load_default_tool_registry()
    d = ToolDefinition(tool_name="my_tool", description="test")
    register_tool(reg, d)
    assert get_tool_definition(reg, "my_tool") is d


def test_get_tool_not_found():
    reg = load_default_tool_registry()
    assert get_tool_definition(reg, "nonexistent") is None


def test_list_enabled_tools():
    reg = load_default_tool_registry()
    enabled = list_enabled_tools(reg)
    assert len(enabled) > 0
    assert all(t.enabled for t in enabled)


# ---------------------------------------------------------------------------
# Initiator tools
# ---------------------------------------------------------------------------

def test_initiator_tool_functions():
    for fn in [agentx_scan, agentx_status, agentx_plan, agentx_propose,
               agentx_validate, agentx_report, agentx_graph_build,
               agentx_graph_status, agentx_graph_query]:
        result = fn({}, {})
        assert result.status in (STATUS_SUCCESS, STATUS_BLOCKED, STATUS_FAILED)


# ---------------------------------------------------------------------------
# Git tools
# ---------------------------------------------------------------------------

def test_git_tool_functions():
    result = git_status({}, {})
    assert result.status in (STATUS_SUCCESS, STATUS_BLOCKED, STATUS_FAILED)
    result = git_diff({}, {})
    assert result.status in (STATUS_SUCCESS, STATUS_BLOCKED, STATUS_FAILED)


# ---------------------------------------------------------------------------
# Patch tools
# ---------------------------------------------------------------------------

def test_patch_tool_functions():
    result = patch_session_status({}, {})
    assert result.status in (STATUS_BLOCKED, STATUS_FAILED, STATUS_PARTIAL)
    result = patch_apply_guarded({}, {})
    assert result.status in (STATUS_BLOCKED, STATUS_FAILED)
    result = rollback_session({}, {})
    assert result.status in (STATUS_BLOCKED, STATUS_FAILED)
