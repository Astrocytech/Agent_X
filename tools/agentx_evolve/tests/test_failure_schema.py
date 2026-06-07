import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

RECOVERY_SCHEMAS = [
    "failure_record.schema.json",
    "recovery_action.schema.json",
    "recovery_decision.schema.json",
    "safe_mode_trigger.schema.json",
    "failure_evidence.schema.json",
    "recovery_playbook.schema.json",
    "failure_taxonomy.schema.json",
]


@pytest.fixture(params=RECOVERY_SCHEMAS)
def schema_path(request):
    return SCHEMA_DIR / request.param


def test_schema_file_exists(schema_path):
    assert schema_path.exists(), f"Missing schema: {schema_path}"


def test_schema_is_valid_json(schema_path):
    raw = schema_path.read_text()
    schema = json.loads(raw)
    assert "$schema" in schema or "type" in schema


def test_schema_is_valid_jsonschema(schema_path):
    raw = schema_path.read_text()
    schema = json.loads(raw)
    jsonschema.Draft7Validator.check_schema(schema)


def _load(name):
    p = SCHEMA_DIR / name
    if not p.exists():
        pytest.skip(f"Schema not found: {p}")
    return json.loads(p.read_text())


def test_failure_record_schema_accepts_valid_record():
    schema = _load("failure_record.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "failure_record.schema.json",
        "failure_id": "fail_001",
        "timestamp": "2025-06-01T12:00:00Z",
        "source_component": "Test",
        "source_layer": "test",
        "failure_class": "MODEL_INVALID_OUTPUT",
        "severity": "LOW",
        "message": "test",
        "details": {},
        "requires_recovery": True,
        "requires_safe_mode": False,
        "requires_human_review": False,
        "retryable": True,
        "rollback_required": False,
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_failure_record_schema_rejects_missing_failure_class():
    schema = _load("failure_record.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "failure_record.schema.json",
        "failure_id": "fail_001",
        "timestamp": "2025-06-01T12:00:00Z",
        "source_component": "Test",
        "source_layer": "test",
        "severity": "LOW",
        "message": "test",
        "details": {},
        "requires_recovery": True,
        "requires_safe_mode": False,
        "requires_human_review": False,
        "retryable": True,
        "rollback_required": False,
        "warnings": [],
        "errors": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_recovery_action_schema_accepts_valid_action():
    schema = _load("recovery_action.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "recovery_action.schema.json",
        "recovery_action_id": "recact_001",
        "session_id": "session_001",
        "run_id": "run_001",
        "created_at": "2025-06-01T12:00:00Z",
        "failure_class": "LOCAL_MODEL_NOT_FOUND",
        "failure_severity": "medium",
        "recovery_strategy": "RETRY",
        "action_status": "RETRYING",
        "retry_count": 0,
        "max_retries": 1,
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_recovery_decision_schema_accepts_valid_decision():
    schema = _load("recovery_decision.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "recovery_decision.schema.json",
        "recovery_decision_id": "recdec_001",
        "timestamp": "2025-06-01T12:00:00Z",
        "failure_id": "fail_001",
        "decision": "BLOCKED",
        "selected_actions": [],
        "reason": "blocked",
        "policy_rule_ids": [],
        "safe_mode_required": False,
        "human_review_required": False,
        "rollback_required": False,
        "retry_allowed": False,
        "continue_session_allowed": False,
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_safe_mode_trigger_schema_accepts_valid_trigger():
    schema = _load("safe_mode_trigger.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "safe_mode_trigger.schema.json",
        "safe_mode_trigger_id": "safemode_001",
        "timestamp": "2025-06-01T12:00:00Z",
        "failure_id": "fail_001",
        "trigger_type": "ROLLBACK_FAILED",
        "reason": "rollback failed",
        "required_actions": [],
        "system_state": "critical",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_failure_taxonomy_schema_accepts_valid_taxonomy():
    schema = _load("failure_taxonomy.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "failure_taxonomy.schema.json",
        "taxonomy_id": "tax_001",
        "timestamp": "2025-06-01T12:00:00Z",
        "version": "1.0",
        "failure_classes": ["MODEL_INVALID_OUTPUT"],
        "severity_matrix": {"MODEL_INVALID_OUTPUT": "LOW"},
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_recovery_playbook_schema_accepts_valid_playbook():
    schema = _load("recovery_playbook.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "recovery_playbook.schema.json",
        "playbook_id": "pb_001",
        "timestamp": "2025-06-01T12:00:00Z",
        "version": "1.0",
        "rules": [{"rule_id": "REC-POL-001", "actions": ["RETRY"]}],
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)
