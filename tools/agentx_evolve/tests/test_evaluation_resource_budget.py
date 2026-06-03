import json
from pathlib import Path
from jsonschema import Draft7Validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "evaluation_resource_budget.schema.json"


def _load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _valid_instance():
    return {
        "schema_version": "1.0",
        "schema_id": "evaluation_resource_budget.schema.json",
        "budget_id": "budget-001",
        "suite_id": "smoke_suite",
        "warnings": [],
        "errors": [],
    }


def test_resource_budget_schema_accepts_valid():
    schema = _load_schema()
    instance = _valid_instance()
    Draft7Validator(schema).validate(instance)


def test_resource_budget_schema_rejects_missing_max_runtime():
    schema = _load_schema()
    instance = _valid_instance()
    del instance["budget_id"]
    errors = list(Draft7Validator(schema).iter_errors(instance))
    assert len(errors) > 0
