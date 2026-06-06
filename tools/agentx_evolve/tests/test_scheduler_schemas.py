import json
import pytest
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

SCHEDULER_SCHEMA_FILES = [
    "task_record.schema.json",
    "session_record.schema.json",
    "queue_state.schema.json",
    "task_claim.schema.json",
    "scheduler_event.schema.json",
    "scheduler_audit.schema.json",
    "scheduler_evidence_manifest.schema.json",
    "scheduler_review_report.schema.json",
    "scheduler_completion_record.schema.json",
    "scheduler_config.schema.json",
    "dead_letter_record.schema.json",
    "dependency_resolution.schema.json",
    "scheduler_lock.schema.json",
    "scheduler_lease.schema.json",
    "scheduler_retry_record.schema.json",
    "scheduler_recovery_event.schema.json",
    "scheduler_summary.schema.json",
    "scheduler_health.schema.json",
    "scheduler_transition_log.schema.json",
    "scheduler_queue_snapshot.schema.json",
]


@pytest.mark.parametrize("fname", SCHEDULER_SCHEMA_FILES)
def test_schema_exists(fname):
    path = SCHEMA_DIR / fname
    assert path.exists(), f"Schema file missing: {fname}"


@pytest.mark.parametrize("fname", SCHEDULER_SCHEMA_FILES)
def test_schema_valid_json(fname):
    path = SCHEMA_DIR / fname
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert isinstance(schema, dict)


@pytest.mark.parametrize("fname", SCHEDULER_SCHEMA_FILES)
def test_schema_required_fields(fname):
    path = SCHEMA_DIR / fname
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert "$schema" in schema, f"Missing $schema in {fname}"
    assert "type" in schema, f"Missing type in {fname}"
    assert "properties" in schema, f"Missing properties in {fname}"
    assert "required" in schema, f"Missing required in {fname}"
    assert "additionalProperties" in schema, f"Missing additionalProperties in {fname}"


@pytest.mark.parametrize("fname", SCHEDULER_SCHEMA_FILES)
def test_schema_id_const(fname):
    path = SCHEMA_DIR / fname
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert schema.get("schema_id") == fname, f"schema_id mismatch in {fname}"
