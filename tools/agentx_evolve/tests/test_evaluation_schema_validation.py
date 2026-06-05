import pytest
import json
import os

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")

REQUIRED_SCHEMAS = [
    "evaluation_result.schema.json",
    "evaluation_golden_task.schema.json",
]


class TestEvaluationSchemasExist:
    def test_all_required_schemas_exist(self):
        for fname in REQUIRED_SCHEMAS:
            path = os.path.join(SCHEMA_DIR, fname)
            assert os.path.exists(path), f"Missing schema: {fname}"

    def test_all_schemas_are_valid_json(self):
        for fname in REQUIRED_SCHEMAS:
            path = os.path.join(SCHEMA_DIR, fname)
            with open(path) as f:
                schema = json.load(f)
            assert "properties" in schema
            assert "$schema" in schema

    def test_schema_is_valid_draft07(self):
        import jsonschema
        for fname in REQUIRED_SCHEMAS:
            path = os.path.join(SCHEMA_DIR, fname)
            with open(path) as f:
                schema = json.load(f)
            jsonschema.Draft7Validator.check_schema(schema)

    def test_schema_has_required_fields(self):
        for fname in REQUIRED_SCHEMAS:
            path = os.path.join(SCHEMA_DIR, fname)
            with open(path) as f:
                schema = json.load(f)
            assert "required" in schema
            assert isinstance(schema["required"], list)
            assert len(schema["required"]) > 0


class TestEvaluationResultSchema:
    @pytest.fixture
    def schema(self):
        path = os.path.join(SCHEMA_DIR, "evaluation_result.schema.json")
        with open(path) as f:
            return json.load(f)

    def test_valid_result(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_result.schema.json",
            "task_id": "gt-test",
            "passed": True,
            "actual_outcome": "All checks passed",
            "duration_ms": 150.5,
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, schema)

    def test_valid_result_minimal(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_result.schema.json",
            "task_id": "gt-minimal",
            "passed": False,
            "actual_outcome": "",
            "duration_ms": 0,
        }
        jsonschema.validate(instance, schema)

    def test_invalid_result_missing_required(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_result.schema.json",
            "task_id": "gt-test",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)

    def test_invalid_result_extra_property(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_result.schema.json",
            "task_id": "gt-test",
            "passed": True,
            "actual_outcome": "ok",
            "duration_ms": 10,
            "extra_field": "not_allowed",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)

    def test_invalid_result_bad_passed_type(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_result.schema.json",
            "task_id": "gt-test",
            "passed": "true",
            "actual_outcome": "ok",
            "duration_ms": 10,
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)

    def test_invalid_result_negative_duration(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_result.schema.json",
            "task_id": "gt-test",
            "passed": True,
            "actual_outcome": "ok",
            "duration_ms": -1,
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


class TestGoldenTaskSchema:
    @pytest.fixture
    def schema(self):
        path = os.path.join(SCHEMA_DIR, "evaluation_golden_task.schema.json")
        with open(path) as f:
            return json.load(f)

    def test_valid_golden_task(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_golden_task.schema.json",
            "task_id": "gt-implement-simple-patch",
            "description": "Implement a simple approved file edit",
            "task_type": "IMPLEMENT_PATCH",
            "expected_outcome": "Patch applied successfully",
            "allowed_files": ["src/example.py"],
            "forbidden_files": ["L0/"],
            "tags": ["core", "patch"],
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, schema)

    def test_valid_golden_task_minimal(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_golden_task.schema.json",
            "task_id": "gt-minimal",
            "description": "Minimal task",
            "task_type": "SECURITY",
            "expected_outcome": "Blocked",
            "tags": ["core"],
        }
        jsonschema.validate(instance, schema)

    def test_invalid_task_missing_required(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_golden_task.schema.json",
            "task_id": "gt-test",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)

    def test_invalid_task_extra_property(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_golden_task.schema.json",
            "task_id": "gt-test",
            "description": "test",
            "task_type": "IMPLEMENT_PATCH",
            "expected_outcome": "ok",
            "tags": [],
            "extra_field": "not_allowed",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)

    def test_invalid_task_bad_tags_type(self, schema):
        import jsonschema
        instance = {
            "schema_version": "1.0",
            "schema_id": "evaluation_golden_task.schema.json",
            "task_id": "gt-test",
            "description": "test",
            "task_type": "IMPLEMENT_PATCH",
            "expected_outcome": "ok",
            "tags": "not_a_list",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)
