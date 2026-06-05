import pytest
import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"
SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"


def _load_schema(name):
    with open(SCHEMAS / name) as f:
        return json.load(f)


def _load_fixture(name):
    with open(FIXTURES / name) as f:
        return json.load(f)


def test_valid_model_profile_schema():
    import jsonschema
    schema = _load_schema("local_model_profile.schema.json")
    data = _load_fixture("valid_model_profile_small_q4.json")
    jsonschema.validate(data, schema)


def test_invalid_model_profile_missing_model_id():
    import jsonschema
    schema = _load_schema("local_model_profile.schema.json")
    data = _load_fixture("invalid_model_profile_missing_model_id.json")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, schema)
