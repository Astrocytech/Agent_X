import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


class TestPromptContractSchema:
    def test_accepts_valid_contract(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_contract.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_contract.schema.json",
            "prompt_contract_id": "pc-test-1",
            "prompt_name": "test-contract",
            "owner_component": "TestSuite",
            "prompt_type": "TASK",
            "allowed_roles": ["developer"],
            "input_contract_id": "ic-001",
            "output_contract_id": "oc-001",
            "status": "DRAFT",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_prompt_contract_id(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_contract.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_contract.schema.json",
            "prompt_name": "test",
            "owner_component": "Test",
            "prompt_type": "TASK",
            "allowed_roles": ["developer"],
            "input_contract_id": "ic-001",
            "output_contract_id": "oc-001",
            "status": "DRAFT",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_rejects_invalid_prompt_type(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_contract.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_contract.schema.json",
            "prompt_contract_id": "pc-test-2",
            "prompt_name": "test",
            "owner_component": "Test",
            "prompt_type": "INVALID_TYPE",
            "allowed_roles": ["developer"],
            "input_contract_id": "ic-001",
            "output_contract_id": "oc-001",
            "status": "DRAFT",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_rejects_empty_allowed_roles(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_contract.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_contract.schema.json",
            "prompt_contract_id": "pc-test-3",
            "prompt_name": "test",
            "owner_component": "Test",
            "prompt_type": "TASK",
            "allowed_roles": [],
            "input_contract_id": "ic-001",
            "output_contract_id": "oc-001",
            "status": "DRAFT",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)


class TestPromptVersionSchema:
    def test_accepts_valid_version(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_version.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_version.schema.json",
            "prompt_version_id": "pv-test-1",
            "prompt_contract_id": "pc-001",
            "version": "1.0.0",
            "created_at": "2026-06-05T00:00:00",
            "created_by": "developer",
            "status": "ACTIVE",
            "prompt_body": "Implement the requested change.",
            "prompt_body_sha256": "abc123",
            "change_summary": "initial version",
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_prompt_body_hash(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_version.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_version.schema.json",
            "prompt_version_id": "pv-test-2",
            "prompt_contract_id": "pc-001",
            "version": "1.0.0",
            "created_at": "2026-06-05T00:00:00",
            "created_by": "developer",
            "status": "ACTIVE",
            "prompt_body": "test body",
            "change_summary": "missing hash",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)
