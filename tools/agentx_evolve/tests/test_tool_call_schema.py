import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"


@pytest.fixture
def call_schema():
    return json.loads((SCHEMA_DIR / "tool_call.schema.json").read_text())


def test_valid_call(call_schema):
    instance = {
        "schema_version": "1.0",
        "schema_id": "tool_call.schema.json",
        "tool_call_id": "call_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolMCPAdapter",
        "caller_role": "ORCHESTRATOR",
        "tool_name": "agentx_scan",
        "arguments": {"action": "list"},
        "requested_effect": "READ",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, call_schema)


def test_valid_call_with_optionals(call_schema):
    instance = {
        "schema_version": "1.0",
        "schema_id": "tool_call.schema.json",
        "tool_call_id": "call_002",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolMCPAdapter",
        "caller_role": "MCP_CLIENT",
        "caller_id": "client_01",
        "session_id": "sess_01",
        "tool_name": "git_status",
        "arguments": {},
        "requested_effect": "READ",
        "dry_run": False,
        "policy_decision_id": "pol_001",
        "sandbox_decision_id": "sand_001",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, call_schema)


def test_rejects_missing_tool_name(call_schema):
    instance = {
        "schema_version": "1.0",
        "schema_id": "tool_call.schema.json",
        "tool_call_id": "call_003",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolMCPAdapter",
        "caller_role": "ORCHESTRATOR",
        "arguments": {},
        "requested_effect": "READ",
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, call_schema)


def test_rejects_missing_schema_version(call_schema):
    instance = {
        "schema_id": "tool_call.schema.json",
        "tool_call_id": "call_004",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolMCPAdapter",
        "caller_role": "ORCHESTRATOR",
        "tool_name": "agentx_scan",
        "arguments": {},
        "requested_effect": "READ",
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, call_schema)


def test_rejects_missing_arguments(call_schema):
    instance = {
        "schema_version": "1.0",
        "schema_id": "tool_call.schema.json",
        "tool_call_id": "call_005",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolMCPAdapter",
        "caller_role": "ORCHESTRATOR",
        "tool_name": "agentx_scan",
        "requested_effect": "READ",
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, call_schema)
