import pytest
import json
from pathlib import Path
from agentx_evolve.model_runtime.schema_validator import validate_local_model_runtime_schemas


SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def _load_example(name):
    path = FIXTURES / name
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def test_schema_validation_all_schemas():
    examples = {}
    result = validate_local_model_runtime_schemas(SCHEMAS, examples)
    assert result["schema_count"] >= 12
    assert result["all_passed"] is True


def test_schema_validation_with_examples():
    examples = {}
    for fname in [
        "valid_model_profile_small_q4.json",
        "valid_model_profile_small_q8.json",
        "valid_runtime_profile_cpu.json",
        "valid_runtime_profile_gpu_optional.json",
        "valid_static_hardware_profile_cpu_only.json",
        "valid_static_hardware_profile_low_vram.json",
        "valid_model_inventory.json",
    ]:
        data = _load_example(fname)
        if data:
            label = fname.replace(".json", "")
            examples[label] = data
    result = validate_local_model_runtime_schemas(SCHEMAS, examples)
    assert result["all_passed"] is True
    assert result["example_count"] >= 1


def test_schema_validation_empty_examples():
    result = validate_local_model_runtime_schemas(SCHEMAS, {})
    assert result["example_count"] == 0
    assert result["all_passed"] is True


def test_schema_validation_with_invalid_example(tmp_path):
    bad_examples = {
        "invalid_missing_id": {"schema_id": "local_model_profile.schema.json", "model_name": "no-id"},
    }
    result = validate_local_model_runtime_schemas(SCHEMAS, bad_examples)
    assert result["all_passed"] is True


def test_schema_validation_nonexistent_schema_dir(tmp_path):
    bad_dir = tmp_path / "nonexistent_schemas"
    result = validate_local_model_runtime_schemas(bad_dir, {})
    assert result["all_passed"] is False
    assert result["schema_count"] == 0
