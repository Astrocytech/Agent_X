import pytest
import json
from pathlib import Path
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter, ToolStatus,
    TS_SUCCESS, TS_PARTIAL, TS_BLOCKED, TS_FAILED, TS_INVALID,
    ALL_TOOL_STATUSES, new_id, utc_now_iso, to_dict,
)
from agentx_evolve.tool.tool_registry import ToolRegistry, ToolAuditEntry
from agentx_evolve.tool.tool_policy import (
    ToolPolicyEnforcer, ToolPolicyRule, ToolPolicyResult,
    POLICY_DECISION_ALLOW, POLICY_DECISION_BLOCK, POLICY_DECISION_REQUIRE_APPROVAL,
)
from agentx_evolve.tool.mcp_server import MCPServer
from agentx_evolve.tool.filesystem_adapter import (
    make_read_file_tool, make_write_file_tool, make_list_files_tool,
)
from agentx_evolve.tool.command_runner_adapter import make_run_command_tool
from agentx_evolve.tool.git_adapter import make_git_status_tool, make_git_diff_tool
from agentx_evolve.tool.agentx_init_adapter import register_initiator_tools
from agentx_evolve.tool.patch_execution_adapter import register_patch_tools


# ---------------------------------------------------------------------------
# tool_models tests
# ---------------------------------------------------------------------------

def test_tool_parameter_defaults():
    p = ToolParameter()
    assert p.name == ""
    assert p.param_type == "string"
    assert not p.required


def test_tool_definition_defaults():
    d = ToolDefinition()
    assert d.tool_name == ""
    assert d.side_effect == "read"
    assert d.enabled


def test_tool_definition_custom():
    d = ToolDefinition(
        tool_name="test_tool",
        description="A test tool",
        requires_approval=True,
    )
    assert d.tool_name == "test_tool"
    assert d.requires_approval


def test_tool_definition_to_dict():
    d = ToolDefinition(tool_name="t1")
    dd = d.to_dict()
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
    assert r.status == TS_SUCCESS
    assert r.data == {}


def test_tool_result_custom():
    r = ToolResult(status=TS_FAILED, message="error", errors=["fail"])
    assert r.status == TS_FAILED
    assert r.errors == ["fail"]


def test_tool_result_to_simple_dict():
    r = ToolResult(
        tool_name="t1", status=TS_SUCCESS, message="ok",
        data={"key": "val"}, artifact_refs=["ref1"],
        warnings=["w1"], errors=["e1"],
    )
    d = r.to_simple_dict()
    assert d["tool_name"] == "t1"
    assert d["status"] == TS_SUCCESS
    assert d["data"]["key"] == "val"


def test_tool_status_enum():
    assert ToolStatus.SUCCESS.value == TS_SUCCESS
    assert ToolStatus.FAILED.value == TS_FAILED


def test_all_tool_statuses():
    assert len(ALL_TOOL_STATUSES) == 5
    assert TS_SUCCESS in ALL_TOOL_STATUSES
    assert TS_INVALID in ALL_TOOL_STATUSES


def test_helpers():
    nid = new_id("tool")
    assert nid.startswith("tool-")
    iso = utc_now_iso()
    assert "T" in iso


def test_to_dict_with_params():
    p = ToolParameter(name="path", param_type="string", required=True)
    d = to_dict(p)
    assert d["name"] == "path"
    assert d["required"] is True


# ---------------------------------------------------------------------------
# ToolRegistry tests
# ---------------------------------------------------------------------------

@pytest.fixture
def registry():
    return ToolRegistry()


@pytest.fixture
def sample_handler():
    def handler(call: ToolCall) -> ToolResult:
        return ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=call.tool_name, status=TS_SUCCESS,
            message=f"Handled {call.tool_name}",
            data={"args": call.arguments},
        )
    return handler


def test_registry_defaults(registry):
    assert registry.list_tools() == []


def test_registry_register(registry, sample_handler):
    d = ToolDefinition(tool_name="greet", description="Says hello")
    registry.register(d, sample_handler)
    assert registry.has_tool("greet")
    assert registry.get_definition("greet") is d


def test_registry_register_and_call(registry, sample_handler):
    d = ToolDefinition(tool_name="echo")
    registry.register(d, sample_handler)
    result = registry.call_tool("echo", {"msg": "hello"})
    assert result.status == TS_SUCCESS
    assert result.data["args"]["msg"] == "hello"


def test_registry_call_unknown_tool(registry):
    result = registry.call_tool("nonexistent", {})
    assert result.status == TS_FAILED
    assert "Unknown tool" in result.message


def test_registry_call_disabled_tool(registry, sample_handler):
    d = ToolDefinition(tool_name="disabled_tool", enabled=False)
    registry.register(d, sample_handler)
    result = registry.call_tool("disabled_tool", {})
    assert result.status == TS_FAILED
    assert "disabled" in result.message


def test_registry_get_handler(registry, sample_handler):
    d = ToolDefinition(tool_name="h1")
    registry.register(d, sample_handler)
    assert registry.get_handler("h1") is sample_handler


def test_registry_get_handler_not_found(registry):
    assert registry.get_handler("nope") is None


def test_registry_list_tools(registry, sample_handler):
    d1 = ToolDefinition(tool_name="t1", enabled=True)
    d2 = ToolDefinition(tool_name="t2", enabled=True)
    d3 = ToolDefinition(tool_name="t3", enabled=False)
    registry.register(d1, sample_handler)
    registry.register(d2, sample_handler)
    registry.register(d3, sample_handler)
    tools = registry.list_tools()
    assert len(tools) == 2
    assert all(t.enabled for t in tools)


def test_registry_list_all(registry, sample_handler):
    d1 = ToolDefinition(tool_name="t1", enabled=True)
    d2 = ToolDefinition(tool_name="t2", enabled=False)
    registry.register(d1, sample_handler)
    registry.register(d2, sample_handler)
    assert len(registry.list_all()) == 2


def test_registry_remove(registry, sample_handler):
    registry.register(ToolDefinition(tool_name="t1"), sample_handler)
    assert registry.has_tool("t1")
    registry.remove("t1")
    assert not registry.has_tool("t1")


def test_registry_audit_log(registry, sample_handler):
    registry.register(ToolDefinition(tool_name="t1"), sample_handler)
    registry.call_tool("t1", {})
    assert len(registry.get_audit_log()) == 1
    entry = registry.get_audit_log()[0]
    assert entry.tool_name == "t1"


def test_registry_audit_log_clear(registry, sample_handler):
    registry.register(ToolDefinition(tool_name="t1"), sample_handler)
    registry.call_tool("t1", {})
    registry.clear_audit_log()
    assert len(registry.get_audit_log()) == 0


def test_registry_handler_exception(registry):
    def bad_handler(call):
        raise RuntimeError("oops")
    registry.register(ToolDefinition(tool_name="bad"), bad_handler)
    result = registry.call_tool("bad", {})
    assert result.status == TS_FAILED
    assert "oops" in result.message


def test_registry_execute_call(registry, sample_handler):
    registry.register(ToolDefinition(tool_name="t1"), sample_handler)
    call = ToolCall(tool_name="t1", arguments={"x": 1})
    result = registry.execute_call(call)
    assert result.status == TS_SUCCESS


def test_registry_policy_blocks(registry):
    registry.policy.add_rule(ToolPolicyRule(tool_name="blocked", effect=POLICY_DECISION_BLOCK))
    registry.register(ToolDefinition(tool_name="blocked"), lambda c: ToolResult(status=TS_SUCCESS))
    result = registry.call_tool("blocked", {})
    assert result.status == TS_BLOCKED


def test_registry_no_handler(registry):
    registry._definitions["orphan"] = ToolDefinition(tool_name="orphan")
    result = registry.call_tool("orphan", {})
    assert result.status == TS_FAILED
    assert "No handler" in result.message


def test_registry_audit_entry_to_dict():
    e = ToolAuditEntry(call_id="c1", tool_name="t1", status=TS_SUCCESS, duration_ms=1.5)
    d = e.to_dict()
    assert d["call_id"] == "c1"
    assert d["tool_name"] == "t1"


# ---------------------------------------------------------------------------
# ToolPolicy tests
# ---------------------------------------------------------------------------

def test_policy_enforcer_defaults():
    e = ToolPolicyEnforcer()
    result = e.enforce("any_tool")
    assert result.decision == POLICY_DECISION_ALLOW


def test_policy_enforcer_block():
    e = ToolPolicyEnforcer()
    e.add_rule(ToolPolicyRule(tool_name="bad_tool", effect=POLICY_DECISION_BLOCK, reason="Not allowed"))
    result = e.enforce("bad_tool")
    assert result.decision == POLICY_DECISION_BLOCK


def test_policy_enforcer_wildcard():
    e = ToolPolicyEnforcer()
    e.add_rule(ToolPolicyRule(tool_name="*", effect=POLICY_DECISION_BLOCK, reason="All blocked"))
    result = e.enforce("anything")
    assert result.decision == POLICY_DECISION_BLOCK


def test_policy_enforcer_require_approval():
    e = ToolPolicyEnforcer()
    e.add_rule(ToolPolicyRule(tool_name="sensitive", effect=POLICY_DECISION_REQUIRE_APPROVAL))
    result = e.enforce("sensitive")
    assert result.decision == POLICY_DECISION_REQUIRE_APPROVAL


def test_policy_enforcer_require_approval_from_defn():
    e = ToolPolicyEnforcer()
    d = ToolDefinition(tool_name="needs_ok", requires_approval=True)
    result = e.enforce("needs_ok", d)
    assert result.decision == POLICY_DECISION_REQUIRE_APPROVAL


def test_policy_enforcer_construction_with_rules():
    rules = [
        ToolPolicyRule(tool_name="t1", effect=POLICY_DECISION_BLOCK),
        ToolPolicyRule(tool_name="t2", effect=POLICY_DECISION_REQUIRE_APPROVAL),
    ]
    e = ToolPolicyEnforcer(rules)
    assert e.enforce("t1").decision == POLICY_DECISION_BLOCK
    assert e.enforce("t2").decision == POLICY_DECISION_REQUIRE_APPROVAL
    assert e.enforce("unknown").decision == POLICY_DECISION_ALLOW


def test_policy_result_to_dict():
    r = ToolPolicyResult(result_id="pr1", tool_name="t1", decision=POLICY_DECISION_BLOCK)
    d = r.to_dict()
    assert d["result_id"] == "pr1"
    assert d["decision"] == POLICY_DECISION_BLOCK


def test_policy_check_tool_call_blocked():
    e = ToolPolicyEnforcer()
    e.add_rule(ToolPolicyRule(tool_name="banned", effect=POLICY_DECISION_BLOCK))
    call = ToolCall(tool_name="banned")
    result = e.check_tool_call(call)
    assert result.status == TS_BLOCKED


def test_policy_check_tool_call_approval():
    e = ToolPolicyEnforcer()
    e.add_rule(ToolPolicyRule(tool_name="need_ok", effect=POLICY_DECISION_REQUIRE_APPROVAL))
    call = ToolCall(tool_name="need_ok")
    result = e.check_tool_call(call)
    assert "requires approval" in result.message


# ---------------------------------------------------------------------------
# MCPServer tests
# ---------------------------------------------------------------------------

@pytest.fixture
def mcp_registry():
    r = ToolRegistry()
    r.register(
        ToolDefinition(tool_name="ping_tool"),
        lambda c: ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=c.tool_name, status=TS_SUCCESS,
            message="pong",
        ),
    )
    return r


def test_mcp_server_list_tools(mcp_registry):
    srv = MCPServer(mcp_registry)
    tools = srv.list_tools()
    assert len(tools) == 1
    assert tools[0]["tool_name"] == "ping_tool"


def test_mcp_server_call_tool(mcp_registry):
    srv = MCPServer(mcp_registry)
    result = srv.call_tool("ping_tool", {})
    assert result["status"] == TS_SUCCESS
    assert result["message"] == "pong"


def test_mcp_server_call_unknown_tool(mcp_registry):
    srv = MCPServer(mcp_registry)
    result = srv.call_tool("unknown", {})
    assert result["status"] == TS_FAILED


def test_mcp_server_handle_list_tools(mcp_registry):
    srv = MCPServer(mcp_registry)
    resp = srv.handle_json_request({"method": "list_tools", "id": 1})
    assert resp["jsonrpc"] == "2.0"
    assert "tools" in resp["result"]


def test_mcp_server_handle_call_tool(mcp_registry):
    srv = MCPServer(mcp_registry)
    resp = srv.handle_json_request({
        "method": "call_tool",
        "params": {"tool_name": "ping_tool", "arguments": {}},
        "id": 2,
    })
    assert resp["jsonrpc"] == "2.0"
    assert resp["result"]["status"] == TS_SUCCESS


def test_mcp_server_handle_ping(mcp_registry):
    srv = MCPServer(mcp_registry)
    resp = srv.handle_json_request({"method": "ping", "id": 3})
    assert resp["result"]["status"] == "pong"


def test_mcp_server_handle_unknown_method(mcp_registry):
    srv = MCPServer(mcp_registry)
    resp = srv.handle_json_request({"method": "bogus", "id": 4})
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_mcp_server_name():
    srv = MCPServer(ToolRegistry(), name="test-mcp")
    assert srv.name == "test-mcp"


# ---------------------------------------------------------------------------
# Filesystem adapter tests
# ---------------------------------------------------------------------------

def test_read_file_tool_defn():
    defn, _ = make_read_file_tool()
    assert defn.tool_name == "read_file_guarded"
    assert defn.side_effect == "read"


def test_write_file_tool_defn():
    defn, _ = make_write_file_tool()
    assert defn.tool_name == "write_file_guarded"
    assert defn.requires_approval


def test_list_files_tool_defn():
    defn, _ = make_list_files_tool()
    assert defn.tool_name == "list_files_guarded"
    assert not defn.requires_approval


def test_read_file_missing(tmp_path):
    _, handler = make_read_file_tool()
    call = ToolCall(tool_name="read_file_guarded", arguments={"path": str(tmp_path / "nope.txt")})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "not found" in result.message


def test_read_file_success(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello world")
    _, handler = make_read_file_tool()
    call = ToolCall(tool_name="read_file_guarded", arguments={"path": str(f)})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.data["content"] == "hello world"


def test_read_file_missing_path():
    _, handler = make_read_file_tool()
    call = ToolCall(tool_name="read_file_guarded", arguments={})
    result = handler(call)
    assert result.status == TS_FAILED


def test_write_file_success(tmp_path):
    _, handler = make_write_file_tool()
    f = tmp_path / "output.txt"
    call = ToolCall(tool_name="write_file_guarded", arguments={"path": str(f), "content": "test data"})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert f.read_text() == "test data"


def test_write_file_missing_path():
    _, handler = make_write_file_tool()
    call = ToolCall(tool_name="write_file_guarded", arguments={"content": "data"})
    result = handler(call)
    assert result.status == TS_FAILED


def test_list_files_dir(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "sub").mkdir()
    _, handler = make_list_files_tool()
    call = ToolCall(tool_name="list_files_guarded", arguments={"path": str(tmp_path), "pattern": "*"})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.data["count"] >= 2


def test_list_files_missing_dir():
    _, handler = make_list_files_tool()
    call = ToolCall(tool_name="list_files_guarded", arguments={"path": "/nonexistent_dir_xyz"})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "not found" in result.message


def test_list_files_default_path(tmp_path):
    _, handler = make_list_files_tool()
    (tmp_path / "x.txt").write_text("x")
    import os
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        call = ToolCall(tool_name="list_files_guarded", arguments={})
        result = handler(call)
        assert result.status == TS_SUCCESS
    finally:
        os.chdir(old)


# ---------------------------------------------------------------------------
# Command runner adapter tests
# ---------------------------------------------------------------------------

def test_run_command_tool_defn():
    defn, _ = make_run_command_tool()
    assert defn.tool_name == "run_allowlisted_command"
    assert defn.requires_approval


def test_run_command_missing_command():
    _, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={})
    result = handler(call)
    assert result.status == TS_FAILED


def test_run_command_empty_command():
    _, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": []})
    result = handler(call)
    assert result.status == TS_FAILED


def test_run_command_blocked_base():
    _, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["sudo", "rm", "-rf", "/"]})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "not allowlisted" in result.message or "blocked" in result.message


def test_run_command_echo(tmp_path):
    _, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["echo", "hello"]})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.data["returncode"] == 0


def test_run_command_shell_metachar():
    _, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["echo", "hello", "&&", "rm", "-rf"]})
    result = handler(call)
    assert result.status == TS_FAILED


def test_run_command_not_found():
    _, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["nonexistent_cmd_xyz"]})
    result = handler(call)
    assert result.status == TS_FAILED


# ---------------------------------------------------------------------------
# Git adapter tests
# ---------------------------------------------------------------------------

def test_git_status_tool_defn():
    defn, _ = make_git_status_tool()
    assert defn.tool_name == "git_status"


def test_git_diff_tool_defn():
    defn, _ = make_git_diff_tool()
    assert defn.tool_name == "git_diff"


def test_git_status_not_a_repo(tmp_path):
    _, handler = make_git_status_tool()
    call = ToolCall(tool_name="git_status", arguments={"repo_path": str(tmp_path)})
    result = handler(call)
    assert result.status in (TS_SUCCESS, TS_FAILED)


def test_git_diff_not_a_repo(tmp_path):
    _, handler = make_git_diff_tool()
    call = ToolCall(tool_name="git_diff", arguments={"repo_path": str(tmp_path)})
    result = handler(call)
    assert result.status in (TS_SUCCESS, TS_FAILED)


# ---------------------------------------------------------------------------
# Initiator adapter tests
# ---------------------------------------------------------------------------

def test_register_initiator_tools(registry, sample_handler):
    defns = register_initiator_tools(registry)
    assert len(defns) == 11
    assert registry.has_tool("agentx_scan")
    assert registry.has_tool("agentx_status")
    assert registry.has_tool("agentx_graph_query")


def test_initiator_tool_calls(registry):
    register_initiator_tools(registry)
    for name in ["agentx_scan", "agentx_status", "agentx_plan", "agentx_propose"]:
        result = registry.call_tool(name, {})
        assert result.status == TS_SUCCESS, f"{name} failed: {result.message}"


# ---------------------------------------------------------------------------
# Patch adapter tests
# ---------------------------------------------------------------------------

def test_register_patch_tools(registry, sample_handler):
    defns = register_patch_tools(registry)
    assert len(defns) == 3
    assert registry.has_tool("patch_apply")
    assert registry.has_tool("patch_rollback")
    assert registry.has_tool("patch_session_status")


def test_patch_tool_calls(registry):
    register_patch_tools(registry)
    for name in ["patch_apply", "patch_rollback", "patch_session_status"]:
        result = registry.call_tool(name, {"session_id": "s1"})
        assert result.status == TS_SUCCESS, f"{name} failed: {result.message}"


# ---------------------------------------------------------------------------
# Integration: full registry with all adapters
# ---------------------------------------------------------------------------

def test_full_registry_smoke():
    registry = ToolRegistry()
    register_initiator_tools(registry)
    register_patch_tools(registry)
    defn_fs, handler_fs = make_read_file_tool()
    registry.register(defn_fs, handler_fs)
    defn_cmd, handler_cmd = make_run_command_tool()
    registry.register(defn_cmd, handler_cmd)
    defn_gs, handler_gs = make_git_status_tool()
    registry.register(defn_gs, handler_gs)
    total = len(registry.list_all())
    assert total == 11 + 3 + 1 + 1 + 1


def test_mcp_server_full_integration():
    registry = ToolRegistry()
    register_initiator_tools(registry)
    srv = MCPServer(registry)
    tools = srv.list_tools()
    assert len(tools) >= 11
    resp = srv.handle_json_request({
        "method": "call_tool",
        "params": {"tool_name": "agentx_scan", "arguments": {}},
        "id": 1,
    })
    assert resp["result"]["status"] == TS_SUCCESS
