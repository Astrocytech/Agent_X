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
QUORUM_SCHEMA_NAME = "human_review_quorum.schema.json"


def _load_schema(name):
    path = SCHEMA_DIR / name
    assert path.exists(), f"Schema file not found: {path}"
    return json.loads(path.read_text())


def test_quorum_schema_file_exists():
    path = SCHEMA_DIR / QUORUM_SCHEMA_NAME
    assert path.exists()


def test_quorum_schema_is_valid_json_schema():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    schema = _load_schema(QUORUM_SCHEMA_NAME)
    try:
        jsonschema.Draft7Validator.check_schema(schema)
    except jsonschema.SchemaError as e:
        pytest.fail(f"Schema error: {e.message}")


def test_quorum_schema_validates_valid_instance():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    schema = _load_schema(QUORUM_SCHEMA_NAME)
    instance = {
        "schema_version": "1.0",
        "schema_id": QUORUM_SCHEMA_NAME,
        "source_component": "HumanReviewApproval",
        "quorum_id": "qrm-001",
        "request_id": "hreq-001",
        "required_count": 2,
        "current_count": 1,
        "reviewers": [],
        "status": "PENDING",
        "warnings": [],
        "errors": [],
    }
    try:
        jsonschema.validate(instance, schema)
    except jsonschema.ValidationError as e:
        pytest.fail(f"Validation failed: {e.message}")


def test_quorum_schema_rejects_missing_required_fields():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    schema = _load_schema(QUORUM_SCHEMA_NAME)
    instance = {
        "schema_version": "1.0",
        "schema_id": QUORUM_SCHEMA_NAME,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)
