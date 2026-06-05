import pytest

from agentx_evolve.tools.tool_models import (
    ToolDefinition,
    ToolRegistry,
    ToolCall,
    ToolResult,
    ToolPermissionDecision,
    ToolAuditEvent,
    InvalidToolRecord,
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_1_LOCAL_STATE_WRITE,
    ROLE_ORCHESTRATOR,
    ROLE_MCP_CLIENT,
    STATUS_SUCCESS,
    STATUS_BLOCKED,
    STATUS_FAILED,
    EFFECT_READ,
    EFFECT_WRITE,
    ALL_TOOL_FAILURE_CLASSES,
    DECISION_ALLOW,
    DECISION_BLOCK,
    utc_now_iso,
    new_id,
    to_dict,
)


def test_tool_definition_defaults():
    td = ToolDefinition()
    assert td.tool_name == ""
    assert td.trust_tier == "TRUST_TIER_0_READ_ONLY"
    assert td.allowed_roles == []


def test_tool_registry_defaults():
    tr = ToolRegistry()
    assert tr.tools == []
    assert tr.schema_version == "1.0"


def test_tool_call_defaults():
    tc = ToolCall()
    assert tc.tool_name == ""
    assert tc.arguments == {}
    assert tc.requested_effect == "READ"


def test_tool_result_defaults():
    tr = ToolResult()
    assert tr.status == "BLOCKED"
    assert tr.failure_class is None


def test_tool_permission_decision_defaults():
    td = ToolPermissionDecision()
    assert td.decision == "BLOCK"
    assert td.reason == ""
    assert td.warnings == []
    assert td.errors == []


def test_tool_audit_event_defaults():
    ta = ToolAuditEvent()
    assert ta.event_type == ""
    assert ta.tool_name is None
    assert ta.status == ""


def test_invalid_tool_record_defaults():
    it = InvalidToolRecord()
    assert it.reason == ""
    assert it.tool_name is None


def test_constants_have_values():
    assert TRUST_TIER_0_READ_ONLY == "TRUST_TIER_0_READ_ONLY"
    assert TRUST_TIER_1_LOCAL_STATE_WRITE == "TRUST_TIER_1_LOCAL_STATE_WRITE"
    assert ROLE_ORCHESTRATOR == "ORCHESTRATOR"
    assert ROLE_MCP_CLIENT == "MCP_CLIENT"
    assert STATUS_SUCCESS == "SUCCESS"
    assert STATUS_BLOCKED == "BLOCKED"
    assert STATUS_FAILED == "FAILED"
    assert EFFECT_READ == "READ"
    assert EFFECT_WRITE == "WRITE"
    assert DECISION_ALLOW == "ALLOW"
    assert DECISION_BLOCK == "BLOCK"


def test_failure_classes_are_strings():
    for fc in ALL_TOOL_FAILURE_CLASSES:
        assert isinstance(fc, str)
        assert len(fc) > 0


def test_utc_now_iso_returns_string():
    ts = utc_now_iso()
    assert isinstance(ts, str)
    assert "T" in ts


def test_new_id_generates_unique():
    ids = {new_id() for _ in range(100)}
    assert len(ids) == 100


def test_new_id_prefix():
    nid = new_id("pre_")
    assert nid.startswith("pre_")


def test_to_dict_dataclass():
    from dataclasses import dataclass
    @dataclass
    class Simple:
        a: int = 1
        b: str = "hello"
    assert to_dict(Simple()) == {"a": 1, "b": "hello"}


def test_to_dict_double():
    result = to_dict({"key": "value"})
    assert result == {"key": "value"}


def test_to_dict_list():
    result = to_dict([1, 2, 3])
    assert result == [1, 2, 3]


def test_to_dict_string():
    assert to_dict("hello") == "hello"
