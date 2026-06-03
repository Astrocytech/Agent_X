import pytest
import json
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_valid_hardware_profile_schema():
    import jsonschema
    with open(SCHEMAS / "local_hardware_profile.schema.json") as f:
        schema = json.load(f)
    with open(FIXTURES / "valid_static_hardware_profile_cpu_only.json") as f:
        data = json.load(f)
    jsonschema.validate(data, schema)


def test_hardware_profile_rejects_negative_memory():
    import jsonschema
    with open(SCHEMAS / "local_hardware_profile.schema.json") as f:
        schema = json.load(f)
    bad = {"hardware_profile_id": "bad", "probe_mode": "STATIC_ONLY", "ram_total_bytes": -1}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)
