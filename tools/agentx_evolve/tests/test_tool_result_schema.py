import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"


@pytest.fixture
def result_schema():
    return json.loads((SCHEMA_DIR / "tool_result.schema.json").read_text())


def _valid_base():
    return {
        "schema_version": "1.0",
        "schema_id": "tool_result.schema.json",
        "tool_result_id": "res_001",
        "tool_call_id": "call_001",
        "timestamp": "2026-06-05T00:00:01Z",
        "source_component": "ToolMCPAdapter",
        "tool_name": "agentx_scan",
        "status": "SUCCESS",
        "exit_code": 0,
        "message": "completed",
        "data": {},
        "failure_class": None,
        "warnings": [],
        "errors": [],
    }


def test_accepts_success(result_schema):
    jsonschema.validate(_valid_base(), result_schema)


def test_accepts_blocked(result_schema):
    instance = _valid_base()
    instance["status"] = "BLOCKED"
    instance["exit_code"] = 1
    jsonschema.validate(instance, result_schema)


def test_accepts_failed(result_schema):
    instance = _valid_base()
    instance["status"] = "FAILED"
    instance["exit_code"] = 1
    instance["failure_class"] = "UNKNOWN_TOOL_FAILURE"
    jsonschema.validate(instance, result_schema)


def test_accepts_invalid(result_schema):
    instance = _valid_base()
    instance["status"] = "INVALID"
    instance["exit_code"] = 2
    instance["failure_class"] = "TOOL_NOT_FOUND"
    jsonschema.validate(instance, result_schema)


def test_accepts_partial(result_schema):
    instance = _valid_base()
    instance["status"] = "PARTIAL"
    instance["exit_code"] = 0
    jsonschema.validate(instance, result_schema)


def test_rejects_missing_status(result_schema):
    instance = _valid_base()
    del instance["status"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, result_schema)


def test_rejects_missing_tool_call_id(result_schema):
    instance = _valid_base()
    del instance["tool_call_id"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, result_schema)


def test_accepts_with_artifact_refs(result_schema):
    instance = _valid_base()
    instance["artifact_refs"] = ["/path/to/artifact"]
    instance["evidence_refs"] = ["/path/to/evidence"]
    jsonschema.validate(instance, result_schema)


def test_rejects_nonexistent_required(result_schema):
    instance = _valid_base()
    del instance["schema_version"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, result_schema)
