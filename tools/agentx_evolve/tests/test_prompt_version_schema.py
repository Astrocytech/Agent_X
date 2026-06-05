import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


class TestPromptVersionSchema:
    def test_accepts_valid_version(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_version.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_version.schema.json",
            "prompt_version_id": "pv-test-valid",
            "prompt_contract_id": "pc-001",
            "version": "2.0.0",
            "created_at": "2026-06-05T00:00:00",
            "created_by": "developer",
            "status": "DRAFT",
            "prompt_body": "Some prompt body text",
            "prompt_body_sha256": "def456",
            "change_summary": "updated version",
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_required_fields(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_version.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_version.schema.json",
            "prompt_version_id": "pv-test-missing",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_rejects_invalid_status(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_version.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_version.schema.json",
            "prompt_version_id": "pv-test-bad-status",
            "prompt_contract_id": "pc-001",
            "version": "1.0.0",
            "created_at": "2026-06-05T00:00:00",
            "created_by": "developer",
            "status": "UNKNOWN_STATUS",
            "prompt_body": "body",
            "prompt_body_sha256": "abc",
            "change_summary": "bad status",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)
