import pytest
import json
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_valid_runtime_profile_schema():
    import jsonschema
    with open(SCHEMAS / "local_runtime_profile.schema.json") as f:
        schema = json.load(f)
    with open(FIXTURES / "valid_runtime_profile_cpu.json") as f:
        data = json.load(f)
    jsonschema.validate(data, schema)


def test_invalid_runtime_profile_unknown_quantization():
    import jsonschema
    with open(SCHEMAS / "local_runtime_profile.schema.json") as f:
        schema = json.load(f)
    with open(FIXTURES / "invalid_runtime_profile_unknown_quantization.json") as f:
        data = json.load(f)
    jsonschema.validate(data, schema)
