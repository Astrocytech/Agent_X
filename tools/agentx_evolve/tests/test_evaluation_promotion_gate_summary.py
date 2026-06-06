import json
from pathlib import Path
from jsonschema import Draft7Validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "evaluation_promotion_gate_summary.schema.json"


def _load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _valid_instance():
    return {
        "schema_version": "1.0",
        "schema_id": "evaluation_promotion_gate_summary.schema.json",
        "gate_id": "gate-001",
        "suite_id": "smoke_suite",
        "run_id": "eval-abc123",
        "timestamp": "2026-06-05T00:00:00Z",
        "decision": "PASS",
        "score_summary": {},
        "warnings": [],
        "errors": [],
    }


def test_promotion_gate_schema_accepts_valid():
    schema = _load_schema()
    instance = _valid_instance()
    Draft7Validator(schema).validate(instance)


def test_promotion_gate_schema_rejects_missing_gate_id():
    schema = _load_schema()
    instance = _valid_instance()
    del instance["gate_id"]
    errors = list(Draft7Validator(schema).iter_errors(instance))
    assert len(errors) > 0
