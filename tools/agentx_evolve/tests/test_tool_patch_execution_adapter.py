from agentx_evolve.tools.patch_tools import (
    patch_session_status, patch_apply_guarded, rollback_session,
)
from agentx_evolve.tools.tool_models import ToolDefinition, STATUS_BLOCKED, STATUS_PARTIAL


def test_patch_session_status():
    result = patch_session_status({}, {})
    assert result.tool_name == "patch_session_status"
    assert result.status in (STATUS_BLOCKED, STATUS_PARTIAL)


def test_patch_apply_guarded():
    result = patch_apply_guarded({}, {})
    assert result.tool_name == "patch_apply_guarded"
    assert result.status == STATUS_BLOCKED


def test_rollback_session():
    result = rollback_session({}, {})
    assert result.tool_name == "rollback_session"
    assert result.status == STATUS_BLOCKED
