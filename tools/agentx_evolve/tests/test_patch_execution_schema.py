import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

GPEL_SCHEMAS = [
    "implementation_session.schema.json",
    "patch_application.schema.json",
    "patch_operation.schema.json",
    "patch_result.schema.json",
    "rollback_snapshot.schema.json",
    "rollback_record.schema.json",
    "source_change_guard.schema.json",
    "implementation_validation_gate.schema.json",
    "patch_execution_decision.schema.json",
    "patch_execution_audit.schema.json",
    "dry_run_result.schema.json",
    "source_inventory.schema.json",
    "patch_limits.schema.json",
    "temporary_policy_bridge.schema.json",
]


@pytest.fixture(params=GPEL_SCHEMAS)
def schema_path(request):
    return SCHEMA_DIR / request.param


def test_schema_file_exists(schema_path):
    assert schema_path.exists(), f"Missing GPEL schema: {schema_path}"


def test_schema_is_valid_json(schema_path):
    raw = schema_path.read_text()
    schema = json.loads(raw)
    assert "$schema" in schema or "type" in schema


def test_schema_is_valid_jsonschema(schema_path):
    raw = schema_path.read_text()
    schema = json.loads(raw)
    jsonschema.Draft7Validator.check_schema(schema)


def _load_schema(name):
    path = SCHEMA_DIR / name
    if not path.exists():
        pytest.skip(f"Schema not found: {path}")
    return json.loads(path.read_text())


def test_implementation_session_valid_instance():
    schema = _load_schema("implementation_session.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "implementation_session.schema.json",
        "session_id": "is-001",
        "timestamp": "2025-06-01T12:00:00Z",
        "source_component": "AgentX",
        "lifecycle_state": "initiated",
        "status": "pending",
        "final_decision": "undecided",
        "target_paths": ["src/main.py"],
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_implementation_session_missing_required():
    schema = _load_schema("implementation_session.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "implementation_session.schema.json",
        "timestamp": "2025-06-01T12:00:00Z",
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_patch_application_valid_instance():
    schema = _load_schema("patch_application.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "patch_application.schema.json",
        "application_id": "pa-001",
        "session_id": "is-001",
        "timestamp": "2025-06-01T12:00:00Z",
        "source_component": "AgentX",
        "mode": "INLINE",
        "operations": ["op-001"],
        "target_paths": ["src/main.py"],
        "status": "pending",
        "before_hashes": {"src/main.py": "abc123"},
        "after_hashes": {"src/main.py": "def456"},
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_patch_operation_valid_instance():
    schema = _load_schema("patch_operation.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "patch_operation.schema.json",
        "operation_id": "po-001",
        "operation_type": "UPDATE",
        "target_path": "src/main.py",
        "requires_rollback_snapshot": True,
        "approved": True,
    }
    jsonschema.validate(instance, schema)


def test_rollback_snapshot_valid_instance():
    schema = _load_schema("rollback_snapshot.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "rollback_snapshot.schema.json",
        "snapshot_id": "rs-001",
        "session_id": "is-001",
        "timestamp": "2025-06-01T12:00:00Z",
        "source_component": "AgentX",
        "snapshot_root": "/tmp/snapshots/rs-001",
        "files": ["src/main.py"],
        "status": "created",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_rollback_record_valid_instance():
    schema = _load_schema("rollback_record.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "rollback_record.schema.json",
        "rollback_id": "rr-001",
        "session_id": "is-001",
        "snapshot_id": "rs-001",
        "timestamp": "2025-06-01T12:05:00Z",
        "source_component": "AgentX",
        "trigger": "validation_failure",
        "restored_files": ["src/main.py"],
        "removed_created_files": [],
        "verification_status": "verified",
        "status": "completed",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_source_change_guard_valid_instance():
    schema = _load_schema("source_change_guard.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "source_change_guard.schema.json",
        "guard_id": "scg-001",
        "session_id": "is-001",
        "timestamp": "2025-06-01T12:00:00Z",
        "source_component": "AgentX",
        "approved_paths": ["src/main.py"],
        "actual_changed_paths": ["src/main.py"],
        "unexpected_paths": [],
        "missing_expected_paths": [],
        "forbidden_paths": [],
        "status": "clean",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)


def test_implementation_validation_gate_valid_instance():
    schema = _load_schema("implementation_validation_gate.schema.json")
    instance = {
        "schema_version": "1.0",
        "schema_id": "implementation_validation_gate.schema.json",
        "validation_gate_id": "ivg-001",
        "session_id": "is-001",
        "timestamp": "2025-06-01T12:00:00Z",
        "source_component": "AgentX",
        "commands_requested": ["python3 -m pytest"],
        "commands_allowed": ["python3 -m pytest"],
        "commands_blocked": [],
        "validation_status": "passed",
        "requires_rollback": False,
        "reason": "all checks passed",
        "warnings": [],
        "errors": [],
    }
    jsonschema.validate(instance, schema)
