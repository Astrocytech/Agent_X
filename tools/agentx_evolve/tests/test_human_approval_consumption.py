import os
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    import jsonschema
except ImportError:
    jsonschema = None


SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
CONSUMPTION_SCHEMA_NAME = "human_approval_consumption.schema.json"


def _load_schema(name):
    path = SCHEMA_DIR / name
    assert path.exists(), f"Schema file not found: {path}"
    return json.loads(path.read_text())


def test_consumption_schema_file_exists():
    path = SCHEMA_DIR / CONSUMPTION_SCHEMA_NAME
    assert path.exists()


def test_consumption_schema_validates_valid_instance():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    schema = _load_schema(CONSUMPTION_SCHEMA_NAME)
    try:
        jsonschema.Draft7Validator.check_schema(schema)
    except jsonschema.SchemaError as e:
        pytest.fail(f"Schema error: {e.message}")

    instance = {
        "schema_version": "1.0",
        "schema_id": CONSUMPTION_SCHEMA_NAME,
        "source_component": "HumanReviewApproval",
        "consumption_id": "con-001",
        "approval_decision_id": "hdec-001",
        "request_id": "hreq-001",
        "consumed_at": "",
        "consumer_id": "consumer-1",
        "max_uses": 5,
        "current_uses": 0,
        "status": "AVAILABLE",
        "warnings": [],
        "errors": [],
    }
    try:
        jsonschema.validate(instance, schema)
    except jsonschema.ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")


def test_consumption_schema_rejects_missing_required_fields():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    schema = _load_schema(CONSUMPTION_SCHEMA_NAME)
    instance = {
        "schema_version": "1.0",
        "schema_id": CONSUMPTION_SCHEMA_NAME,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_consumption_schema_rejects_invalid_enum():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    schema = _load_schema(CONSUMPTION_SCHEMA_NAME)
    instance = {
        "schema_version": "1.0",
        "schema_id": CONSUMPTION_SCHEMA_NAME,
        "source_component": "HumanReviewApproval",
        "consumption_id": "con-002",
        "approval_decision_id": "hdec-001",
        "request_id": "hreq-001",
        "consumed_at": "",
        "consumer_id": "consumer-1",
        "max_uses": 5,
        "current_uses": 0,
        "status": "INVALID_STATUS",
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)
