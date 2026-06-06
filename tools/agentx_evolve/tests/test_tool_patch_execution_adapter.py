from agentx_evolve.tool.patch_execution_adapter import (
    make_patch_apply_tool, make_patch_rollback_tool,
    make_patch_session_status_tool, register_patch_tools,
)
from agentx_evolve.tool.tool_models import ToolDefinition, ToolCall, TS_SUCCESS


def test_make_patch_apply_tool():
    defn, handler = make_patch_apply_tool()
    assert defn.tool_name == "patch_apply"
    assert defn.requires_approval is True


def test_make_patch_rollback_tool():
    defn, handler = make_patch_rollback_tool()
    assert defn.tool_name == "patch_rollback"
    assert defn.requires_approval is True


def test_make_patch_session_status_tool():
    defn, handler = make_patch_session_status_tool()
    assert defn.tool_name == "patch_session_status"
    assert defn.requires_approval is True


def test_patch_apply_handler():
    _defn, handler = make_patch_apply_tool()
    call = ToolCall(tool_name="patch_apply", arguments={"session_id": "sess-1"})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.message == "Patch applied"


def test_patch_rollback_handler():
    _defn, handler = make_patch_rollback_tool()
    call = ToolCall(tool_name="patch_rollback", arguments={})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert "rolled back" in result.message.lower()


def test_patch_session_status_handler():
    _defn, handler = make_patch_session_status_tool()
    call = ToolCall(tool_name="patch_session_status", arguments={})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert "status" in result.message.lower()


class FakeRegistry:
    def __init__(self):
        self.registered = []

    def register(self, defn, handler):
        self.registered.append((defn, handler))


def test_register_patch_tools():
    registry = FakeRegistry()
    defns = register_patch_tools(registry)
    assert len(defns) == 3
    assert len(registry.registered) == 3
