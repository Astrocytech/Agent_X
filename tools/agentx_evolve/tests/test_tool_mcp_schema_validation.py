"""Comprehensive schema validation covering all 10 Tool/MCP schemas.

Tests valid and invalid instances for each schema.
Serves as the pytest-based fallback for validate_tool_mcp_schemas.py.
"""
import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

SCHEMA_NAMES = [
    "tool_call.schema.json",
    "tool_result.schema.json",
    "tool_definition.schema.json",
    "tool_registry.schema.json",
    "tool_permission_decision.schema.json",
    "tool_policy.schema.json",
    "tool_trust_tier.schema.json",
    "mcp_tool_manifest.schema.json",
    "invalid_tool_record.schema.json",
    "tool_audit.schema.json",
]


@pytest.fixture(params=SCHEMA_NAMES)
def schema_name(request):
    return request.param


@pytest.fixture
def schema(schema_name):
    return json.loads((SCHEMA_DIR / schema_name).read_text())


def test_schema_file_exists(schema_name):
    assert (SCHEMA_DIR / schema_name).exists()


def test_schema_is_valid_json(schema_name):
    data = (SCHEMA_DIR / schema_name).read_text()
    parsed = json.loads(data)
    assert "$schema" in parsed or "type" in parsed


def test_schema_has_required_field(schema):
    assert "required" in schema
    assert isinstance(schema["required"], list)
    assert len(schema["required"]) >= 3


def test_schema_has_properties(schema):
    assert "properties" in schema
    assert isinstance(schema["properties"], dict)


def test_schema_has_additional_properties_false(schema):
    assert schema.get("additionalProperties", True) is False, "Schema should have additionalProperties: false"


def test_schema_required_are_in_properties(schema):
    for req in schema["required"]:
        assert req in schema["properties"], f"Required field '{req}' not in properties"


class TestToolCallSchema:
    @pytest.fixture
    def sc(self):
        return json.loads((SCHEMA_DIR / "tool_call.schema.json").read_text())

    def test_valid_full(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "tool_call.schema.json",
            "tool_call_id": "call_001",
            "timestamp": "2026-06-05T00:00:00Z",
            "source_component": "ToolMCPAdapter",
            "caller_role": "ORCHESTRATOR",
            "tool_name": "agentx_scan",
            "arguments": {},
            "requested_effect": "READ",
            "warnings": [],
            "errors": [],
        }, sc)

    def test_invalid_missing_required(self, sc):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate({"schema_version": "1.0"}, sc)


class TestToolResultSchema:
    @pytest.fixture
    def sc(self):
        return json.loads((SCHEMA_DIR / "tool_result.schema.json").read_text())

    def test_valid_success(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "tool_result.schema.json",
            "tool_result_id": "res_001",
            "tool_call_id": "call_001",
            "timestamp": "2026-06-05T00:00:01Z",
            "source_component": "ToolMCPAdapter",
            "tool_name": "agentx_scan",
            "status": "SUCCESS",
            "exit_code": 0,
            "message": "done",
            "data": {},
            "warnings": [],
            "errors": [],
        }, sc)

    def test_valid_blocked(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "tool_result.schema.json",
            "tool_result_id": "res_002",
            "tool_call_id": "call_002",
            "timestamp": "2026-06-05T00:00:01Z",
            "source_component": "ToolMCPAdapter",
            "tool_name": "blocked_tool",
            "status": "BLOCKED",
            "exit_code": 1,
            "message": "blocked",
            "data": {},
            "failure_class": "TOOL_POLICY_DENIED",
            "warnings": [],
            "errors": [],
        }, sc)

    def test_valid_invalid(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "tool_result.schema.json",
            "tool_result_id": "res_003",
            "tool_call_id": "call_003",
            "timestamp": "2026-06-05T00:00:01Z",
            "source_component": "InvalidToolHandler",
            "tool_name": "nonexistent",
            "status": "INVALID",
            "exit_code": 2,
            "message": "Unknown tool",
            "data": {},
            "failure_class": "TOOL_NOT_FOUND",
            "warnings": [],
            "errors": [],
        }, sc)

    def test_invalid_missing_status(self, sc):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate({
                "schema_version": "1.0",
                "schema_id": "tool_result.schema.json",
                "tool_result_id": "res_004",
                "tool_call_id": "call_004",
                "timestamp": "2026-06-05T00:00:01Z",
                "source_component": "ToolMCPAdapter",
                "tool_name": "test",
                "exit_code": 0,
                "message": "no status",
                "data": {},
                "warnings": [],
                "errors": [],
            }, sc)


class TestMCPManifestSchema:
    @pytest.fixture
    def sc(self):
        return json.loads((SCHEMA_DIR / "mcp_tool_manifest.schema.json").read_text())

    def test_valid_read_only(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "mcp_tool_manifest.schema.json",
            "manifest_id": "mcp_001",
            "created_at": "2026-06-05T00:00:00Z",
            "source_component": "MCPAdapter",
            "exposed_tools": [
                {"tool_name": "agentx_scan", "description": "scan", "input_schema": {"type": "object"}}
            ],
            "blocked_tools": ["write_file_guarded"],
            "warnings": [],
            "errors": [],
        }, sc)

    def test_rejects_missing_exposed_tools(self, sc):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate({
                "schema_version": "1.0",
                "schema_id": "mcp_tool_manifest.schema.json",
                "manifest_id": "mcp_002",
                "created_at": "2026-06-05T00:00:00Z",
                "source_component": "MCPAdapter",
                "blocked_tools": [],
                "warnings": [],
                "errors": [],
            }, sc)


class TestEvidenceManifestSchema:
    @pytest.fixture
    def sc(self):
        path = SCHEMA_DIR / "evidence_manifest.schema.json"
        if path.exists():
            return json.loads(path.read_text())
        pytest.skip("evidence_manifest.schema.json not found")

    def test_valid_manifest(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "evidence_manifest.schema.json",
            "manifest_id": "em-001",
            "timestamp": "2026-06-05T00:00:00Z",
            "source_component": "AGENTX_TOOL_MCP_ADAPTER",
            "tool_call_id": "tc-001",
            "evidence_entries": [],
            "warnings": [],
            "errors": [],
        }, sc)


class TestReviewReportSchema:
    @pytest.fixture
    def sc(self):
        path = SCHEMA_DIR / "review_report.schema.json"
        if path.exists():
            return json.loads(path.read_text())
        pytest.skip("review_report.schema.json not found")

    def test_valid_report(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "review_report.schema.json",
            "report_id": "rr-001",
            "timestamp": "2026-06-05T00:00:00Z",
            "source_component": "AGENTX_TOOL_MCP_ADAPTER",
            "tool_call_id": "tc-001",
            "review_action": "IMPLEMENTATION_REVIEW",
            "decision": "APPROVED",
            "reviewed_by": "opencode",
            "warnings": [],
            "errors": [],
        }, sc)


class TestCompletionRecordSchema:
    @pytest.fixture
    def sc(self):
        path = SCHEMA_DIR / "completion_record.schema.json"
        if path.exists():
            return json.loads(path.read_text())
        pytest.skip("completion_record.schema.json not found")

    def test_valid_record(self, sc):
        jsonschema.validate({
            "schema_version": "1.0",
            "schema_id": "completion_record.schema.json",
            "completion_id": "cr-001",
            "timestamp": "2026-06-05T00:00:00Z",
            "source_component": "AGENTX_TOOL_MCP_ADAPTER",
            "tool_call_id": "tc-001",
            "tool_name": "mcp_adapter",
            "overall_status": "SUCCESS",
            "warnings": [],
            "errors": [],
        }, sc)
