import json
from pathlib import Path
from jsonschema import Draft7Validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "evaluation_benchmark_lockfile.schema.json"


def _load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _valid_instance():
    return {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_lockfile.schema.json",
        "lockfile_id": "lf-001",
        "suite_id": "smoke_suite",
        "created_at": "2026-06-05T00:00:00Z",
        "suite_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
        "case_hashes": {
            "case-1": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        },
        "source_component": "EvaluationHarness",
        "warnings": [],
        "errors": [],
    }


def test_lockfile_schema_accepts_valid():
    schema = _load_schema()
    instance = _valid_instance()
    Draft7Validator(schema).validate(instance)


def test_lockfile_schema_rejects_missing_suite():
    schema = _load_schema()
    instance = _valid_instance()
    del instance["suite_id"]
    errors = list(Draft7Validator(schema).iter_errors(instance))
    assert len(errors) > 0


def test_lockfile_schema_rejects_invalid_case_hash():
    schema = _load_schema()
    instance = _valid_instance()
    instance["case_hashes"] = {"bad-hash": "not-a-valid-sha256"}
    errors = list(Draft7Validator(schema).iter_errors(instance))
    assert len(errors) > 0
