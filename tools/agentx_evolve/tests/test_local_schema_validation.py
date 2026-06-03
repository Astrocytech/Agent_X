import pytest
from pathlib import Path
from agentx_evolve.model_runtime.schema_validator import validate_local_model_runtime_schemas

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"


def test_schema_validation_all_schemas():
    examples = {}
    result = validate_local_model_runtime_schemas(SCHEMAS, examples)
    assert result["schema_count"] >= 12
    assert result["all_passed"] is True
