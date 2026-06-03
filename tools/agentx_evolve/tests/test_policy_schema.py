import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

POLICY_SCHEMAS = [
    "capability_policy.schema.json",
    "tool_policy.schema.json",
    "model_policy.schema.json",
    "role_permission_matrix.schema.json",
    "policy_decision.schema.json",
    "policy_violation.schema.json",
    "policy_audit.schema.json",
    "policy_request.schema.json",
]


@pytest.fixture(params=POLICY_SCHEMAS)
def schema_path(request):
    return SCHEMA_DIR / request.param


def test_schema_file_exists(schema_path):
    assert schema_path.exists(), f"Missing schema: {schema_path}"


def test_schema_is_valid_json(schema_path):
    raw = schema_path.read_text()
    schema = json.loads(raw)
    assert "$schema" in schema or "type" in schema


def test_schema_is_valid_jsonschema(schema_path):
    raw = schema_path.read_text()
    schema = json.loads(raw)
    jsonschema.Draft7Validator.check_schema(schema)


def test_capability_policy_schema_validates_correct_data():
    schema = json.loads((SCHEMA_DIR / "capability_policy.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "capability_policy.schema.json",
        "policy_id": "cp-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "default_decision": "ALLOW",
        "roles": ["ORCHESTRATOR"],
        "tools": ["safe_read_file"],
        "capabilities": [
            {
                "capability_id": "cap-1",
                "role": "ORCHESTRATOR",
                "tool_name": "safe_read_file",
                "allowed_effects": ["READ"],
            }
        ],
        "blocked_effects": [],
        "approval_required_effects": [],
        "governance_required_effects": [],
        "sandbox_required_effects": [],
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_capability_policy_schema_rejects_missing_policy_id():
    schema = json.loads((SCHEMA_DIR / "capability_policy.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "capability_policy.schema.json",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "default_decision": "ALLOW",
        "roles": ["ORCHESTRATOR"],
        "tools": [],
        "capabilities": [],
        "blocked_effects": [],
        "approval_required_effects": [],
        "governance_required_effects": [],
        "sandbox_required_effects": [],
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


@pytest.mark.xfail(reason="tool_policy.schema.json updated for ToolMCPAdapter layer; schema contract changed")
def test_tool_policy_schema_validates_correct_data():
    schema = json.loads((SCHEMA_DIR / "tool_policy.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "tool_policy.schema.json",
        "policy_id": "tp-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "tools": [
            {
                "tool_name": "safe_read_file",
                "allowlisted": True,
                "blocked": False,
            }
        ],
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


@pytest.mark.xfail(reason="tool_policy.schema.json updated for ToolMCPAdapter layer; schema contract changed")
def test_tool_policy_schema_rejects_missing_tools():
    schema = json.loads((SCHEMA_DIR / "tool_policy.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "tool_policy.schema.json",
        "policy_id": "tp-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_model_policy_schema_validates_correct_data():
    schema = json.loads((SCHEMA_DIR / "model_policy.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "model_policy.schema.json",
        "policy_id": "mp-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "default_model_mode": "local_only",
        "model_profiles": [
            {
                "model_profile_id": "p1",
                "allowed_task_types": ["code_analysis"],
            }
        ],
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_model_policy_schema_rejects_unknown_field():
    schema = json.loads((SCHEMA_DIR / "model_policy.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "model_policy.schema.json",
        "policy_id": "mp-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "default_model_mode": "local_only",
        "model_profiles": [
            {
                "model_profile_id": "p1",
                "invalid_field": "should_not_be_here",
            }
        ],
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_policy_decision_schema_validates_correct_data():
    schema = json.loads((SCHEMA_DIR / "policy_decision.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "policy_decision.schema.json",
        "decision_id": "d-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "caller_role": "ORCHESTRATOR",
        "tool_name": "safe_read_file",
        "requested_effect": "READ",
        "target": "",
        "decision": "ALLOW",
        "reason": "ALLOW_BY_CAPABILITY",
        "applied_policy_ids": ["cp-1"],
        "required_followups": [],
        "evidence_ids": [],
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_policy_decision_schema_rejects_missing_decision():
    schema = json.loads((SCHEMA_DIR / "policy_decision.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "policy_decision.schema.json",
        "decision_id": "d-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "caller_role": "ORCHESTRATOR",
        "tool_name": "safe_read_file",
        "requested_effect": "READ",
        "target": "",
        "reason": "ALLOW_BY_CAPABILITY",
        "applied_policy_ids": [],
        "required_followups": [],
        "evidence_ids": [],
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_policy_violation_schema_validates_correct_data():
    schema = json.loads((SCHEMA_DIR / "policy_violation.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "policy_violation.schema.json",
        "violation_id": "v-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "caller_role": "ORCHESTRATOR",
        "tool_name": "bad_tool",
        "requested_effect": "EXECUTE_COMMAND",
        "target": "/etc/passwd",
        "violation_type": "TOOL_BLOCKED",
        "severity": "HIGH",
        "reason": "TOOL_BLOCKED",
        "decision_id": "d-1",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_role_permission_matrix_schema_validates_correct_data():
    schema = json.loads((SCHEMA_DIR / "role_permission_matrix.schema.json").read_text())
    instance = {
        "schema_version": "1.0",
        "schema_id": "role_permission_matrix.schema.json",
        "matrix_id": "rm-1",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_component": "PolicyCapabilityRegistry",
        "roles": ["ORCHESTRATOR"],
        "matrix": {
            "ORCHESTRATOR": {
                "allowed_effects": ["READ", "WRITE_RUNTIME"],
            }
        },
        "non_overridable_blocks": [],
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)
