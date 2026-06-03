import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "prompts")

REQUIRED_SCHEMAS = [
    "prompt_contract.schema.json",
    "prompt_version.schema.json",
    "prompt_registry.schema.json",
    "prompt_input_contract.schema.json",
    "prompt_output_contract.schema.json",
    "prompt_safety_rule.schema.json",
    "prompt_provenance.schema.json",
    "prompt_diff.schema.json",
    "prompt_migration.schema.json",
    "prompt_runtime_binding.schema.json",
    "prompt_worker_payload.schema.json",
    "prompt_registry_snapshot.schema.json",
    "prompt_permission_decision.schema.json",
    "prompt_audit.schema.json",
    "prompt_evidence_manifest.schema.json",
    "prompt_completion_record.schema.json",
]


class TestPromptSchemasExist:
    def test_all_required_schemas_exist(self):
        for fname in REQUIRED_SCHEMAS:
            path = os.path.join(SCHEMA_DIR, fname)
            assert os.path.exists(path), f"Missing schema: {fname}"

    def test_all_schemas_are_valid_json(self):
        import jsonschema
        for fname in REQUIRED_SCHEMAS:
            path = os.path.join(SCHEMA_DIR, fname)
            with open(path) as f:
                schema = json.load(f)
            jsonschema.Draft7Validator.check_schema(schema)


class TestPromptFixtures:
    @pytest.mark.parametrize("fname", [
        f for f in os.listdir(FIXTURES_DIR)
        if f.endswith(".json")
        and f.startswith("valid_")
    ] if os.path.isdir(FIXTURES_DIR) else [])
    def test_valid_fixture(self, fname):
        import jsonschema
        path = os.path.join(FIXTURES_DIR, fname)
        with open(path) as f:
            data = json.load(f)
        schema_id = data.get("schema_id", "")
        schema_path = os.path.join(SCHEMA_DIR, schema_id)
        with open(schema_path) as f:
            schema = json.load(f)
        jsonschema.validate(data, schema)

    @pytest.mark.parametrize("fname", [
        f for f in os.listdir(FIXTURES_DIR)
        if f.endswith(".json")
        and (f.startswith("missing_") or f.startswith("invalid_") or f.startswith("unknown_") or f.startswith("negative_"))
    ] if os.path.isdir(FIXTURES_DIR) else [])
    def test_invalid_fixture(self, fname):
        import jsonschema
        path = os.path.join(FIXTURES_DIR, fname)
        with open(path) as f:
            data = json.load(f)
        schema_id = data.get("schema_id", "")
        schema_path = os.path.join(SCHEMA_DIR, schema_id)
        with open(schema_path) as f:
            schema = json.load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)


class TestPromptContractSchema:
    def test_accepts_valid_contract(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_contract.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_contract.schema.json",
            "prompt_contract_id": "pc-test",
            "prompt_name": "test",
            "owner_component": "Test",
            "prompt_type": "TASK",
            "allowed_roles": ["developer"],
            "input_contract_id": "ic-001",
            "output_contract_id": "oc-001",
            "status": "DRAFT",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_contract_id(self):
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
            "prompt_contract_id": "pc-test",
            "prompt_name": "test",
            "owner_component": "Test",
            "prompt_type": "UNKNOWN_TYPE",
            "allowed_roles": ["developer"],
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
            "prompt_version_id": "pv-test",
            "prompt_contract_id": "pc-001",
            "version": "1.0.0",
            "created_at": "2026-06-05T00:00:00",
            "created_by": "developer",
            "status": "ACTIVE",
            "prompt_body": "test body",
            "prompt_body_sha256": "abc",
            "change_summary": "test",
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_body_sha256(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_version.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_version.schema.json",
            "prompt_version_id": "pv-test",
            "prompt_contract_id": "pc-001",
            "version": "1.0.0",
            "created_at": "2026-06-05T00:00:00",
            "created_by": "developer",
            "status": "ACTIVE",
            "prompt_body": "test body",
            "change_summary": "test",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)


class TestPromptRegistrySchema:
    def test_accepts_valid_registry(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_registry.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_registry.schema.json",
            "registry_id": "pr-test",
            "registry_version": "1.0",
            "created_at": "2026-06-05T00:00:00",
            "contracts": [],
            "versions": [],
            "active_bindings": {},
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_registry_id(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_registry.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_registry.schema.json",
            "registry_version": "1.0",
            "created_at": "2026-06-05T00:00:00",
            "contracts": [],
            "versions": [],
            "active_bindings": {},
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)
