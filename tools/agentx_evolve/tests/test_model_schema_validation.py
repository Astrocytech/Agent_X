import pytest
import json
from pathlib import Path

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
MODEL_SCHEMA_NAMES = [
    "model_adapter_completion_record.schema",
    "model_adapter_evidence_manifest.schema",
    "model_audit.schema",
    "model_call_evidence.schema",
    "model_capability_profile.schema",
    "model_policy_decision.schema",
    "model_policy.schema",
    "model_profile.schema",
    "model_provider_profile.schema",
    "model_registry.schema",
    "model_request.schema",
    "model_response.schema",
    "model_retry_record.schema",
    "model_runtime_profile.schema",
    "model_selection_decision.schema",
]


class TestModelSchemaFiles:
    def test_schemas_directory_exists(self):
        assert SCHEMAS_DIR.is_dir()

    def test_all_model_schemas_exist(self):
        for name in MODEL_SCHEMA_NAMES:
            path = SCHEMAS_DIR / f"{name}.json"
            assert path.is_file(), f"Missing schema: {name}.json"

    def test_all_schemas_are_valid_json(self):
        for name in MODEL_SCHEMA_NAMES:
            path = SCHEMAS_DIR / f"{name}.json"
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, dict), f"{name}.json is not a dict"

    def test_all_schemas_have_schema_field(self):
        for name in MODEL_SCHEMA_NAMES:
            path = SCHEMAS_DIR / f"{name}.json"
            with open(path) as f:
                data = json.load(f)
            assert "$schema" in data or "schema" in data, f"{name}.json missing $schema"

    def test_all_schemas_have_type_object(self):
        for name in MODEL_SCHEMA_NAMES:
            path = SCHEMAS_DIR / f"{name}.json"
            with open(path) as f:
                data = json.load(f)
            assert data.get("type") == "object", f"{name}.json type is not 'object'"

    def test_all_schemas_have_properties(self):
        for name in MODEL_SCHEMA_NAMES:
            path = SCHEMAS_DIR / f"{name}.json"
            with open(path) as f:
                data = json.load(f)
            assert "properties" in data, f"{name}.json missing properties"

    def test_schema_file_sizes_reasonable(self):
        for name in MODEL_SCHEMA_NAMES:
            path = SCHEMAS_DIR / f"{name}.json"
            size = path.stat().st_size
            assert 50 < size < 50000, f"{name}.json size {size} out of range [50, 50000]"


class TestModelSchemaContent:
    @pytest.fixture(params=MODEL_SCHEMA_NAMES)
    def schema_data(self, request):
        path = SCHEMAS_DIR / f"{request.param}.json"
        with open(path) as f:
            return json.load(f), request.param

    def test_required_fields_valid(self, schema_data):
        data, name = schema_data
        if "required" in data:
            assert isinstance(data["required"], list)
            for field in data["required"]:
                assert isinstance(field, str)

    def test_properties_have_types(self, schema_data):
        data, name = schema_data
        for prop_name, prop_def in data.get("properties", {}).items():
            assert "type" in prop_def or "$ref" in prop_def or "anyOf" in prop_def or "oneOf" in prop_def, \
                f"{name}.json property '{prop_name}' missing type"
