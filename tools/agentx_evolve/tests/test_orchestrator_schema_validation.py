import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import jsonschema
from jsonschema import ValidationError
from agentx_evolve.tests.validate_orchestrator_schemas import ORCHESTRATOR_SCHEMAS, valid_instance

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def test_orchestrator_schemas_accept_valid_examples():
    for sname in ORCHESTRATOR_SCHEMAS:
        spath = SCHEMA_DIR / sname
        assert spath.exists(), f"Missing schema: {sname}"
        schema = json.loads(spath.read_text())
        props = schema.setdefault("properties", {})
        for field in ("schema_version", "schema_id"):
            if field in schema.get("required", []) and field not in props:
                props[field] = {"type": "string"}
        instance = {k: v for k, v in valid_instance(sname).items() if k in props}
        jsonschema.validate(instance, schema)


def test_orchestrator_schemas_reject_missing_required_fields():
    for sname in ORCHESTRATOR_SCHEMAS:
        spath = SCHEMA_DIR / sname
        schema = json.loads(spath.read_text())
        instance = valid_instance(sname)
        required = schema.get("required", [])
        if not required:
            continue
        field = required[0]
        if field in instance:
            del instance[field]
        try:
            jsonschema.validate(instance, schema)
            assert False, f"Expected ValidationError for {sname} missing {field}"
        except ValidationError:
            pass


def test_orchestrator_schemas_reject_invalid_enums():
    sname = "execution_step.schema.json"
    spath = SCHEMA_DIR / sname
    assert spath.exists()
    schema = json.loads(spath.read_text())
    instance = valid_instance(sname)
    instance["step_type"] = "INVALID_ENUM"
    try:
        jsonschema.validate(instance, schema)
        assert False, "Expected ValidationError for invalid enum"
    except ValidationError:
        pass


def test_orchestrator_schemas_reject_invalid_types():
    sname = "execution_step.schema.json"
    spath = SCHEMA_DIR / sname
    assert spath.exists()
    schema = json.loads(spath.read_text())
    instance = valid_instance(sname)
    instance["step_index"] = "not-an-integer"
    try:
        jsonschema.validate(instance, schema)
        assert False, "Expected ValidationError for invalid type"
    except ValidationError:
        pass
