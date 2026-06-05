import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "context")

REQUIRED_SCHEMAS = [
    "context_source.schema.json",
    "task_input.schema.json",
    "context_item.schema.json",
    "context_pack.schema.json",
    "task_pack.schema.json",
    "context_priority_score.schema.json",
    "context_budget_estimate.schema.json",
    "context_deduplication_report.schema.json",
    "context_compression_plan.schema.json",
    "context_redaction_report.schema.json",
    "context_injection_filter_report.schema.json",
    "context_model_compatibility.schema.json",
    "context_tool_compatibility.schema.json",
    "context_pack_evidence.schema.json",
]

ALL_REQUIRED = [
    "context_source",
    "task_input",
    "context_item",
    "context_pack",
    "task_pack",
]


class TestSchemasExist:
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


class TestFixtureValidation:
    @pytest.mark.parametrize("fname", [
        f for f in os.listdir(FIXTURES_DIR) if f.endswith(".json") and not f.startswith("missing_") and not f.startswith("unknown_") and not f.startswith("invalid_") and not f.startswith("negative_")
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
        f for f in os.listdir(FIXTURES_DIR) if f.endswith(".json") and (f.startswith("missing_") or f.startswith("unknown_") or f.startswith("invalid_") or f.startswith("negative_"))
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


class TestCompileAndImport:
    def test_compile_context_package(self):
        import py_compile
        base = os.path.join(os.path.dirname(__file__), "..", "context")
        for fname in os.listdir(base):
            if fname.endswith(".py"):
                path = os.path.join(base, fname)
                py_compile.compile(path, doraise=True)

    def test_import_context_models(self):
        from agentx_evolve.context.context_models import ContextSource, TaskInput, ContextItem, ContextPack, TaskPack
        assert ContextSource is not None
        assert TaskPack is not None
