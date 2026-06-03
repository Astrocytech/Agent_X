import json
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

import pytest

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _load_schema(name: str) -> dict:
    path = _SCHEMA_DIR / name
    if not path.exists():
        path = _SCHEMA_DIR / f"{name}.schema.json"
    with open(path) as f:
        return json.load(f)


def _validate(instance: dict, schema_name: str) -> tuple[bool, list[str]]:
    schema = _load_schema(schema_name)
    try:
        jsonschema.validate(instance, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [e.message]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]


def _make_valid_policy_dict():
    return {
        "schema_version": "1.0",
        "schema_id": "sandbox_policy.schema.json",
        "policy_id": str(uuid4()),
        "repo_root": "/tmp/test",
        "runtime_state_root": ".agentx-init",
        "protected_paths": ["L0/"],
        "source_write_allowed": False,
        "runtime_write_allowed": True,
        "network_allowed": False,
        "shell_allowed": False,
        "allowlisted_commands": [],
        "allowlisted_write_paths": [".agentx-init/"],
        "blocked_write_paths": ["L0/"],
        "max_file_size_bytes": 1048576,
        "resolve_symlinks": True,
        "require_governance_for_source_write": True,
        "require_session_for_source_write": True,
        "require_rollback_for_source_write": True,
        "redact_secret_patterns": [],
        "warnings": [],
        "errors": [],
    }


def _make_valid_decision_dict():
    return {
        "schema_version": "1.0",
        "schema_id": "sandbox_decision.schema.json",
        "decision_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "SecuritySandbox",
        "operation": "READ",
        "target": "src/file.txt",
        "decision": "ALLOW",
        "reason": "Boundary check passed",
        "applied_rule_ids": ["ALLOW"],
        "evidence_ids": [],
        "violations": [],
        "warnings": [],
        "errors": [],
    }


def _make_valid_path_boundary_dict():
    return {
        "schema_version": "1.0",
        "schema_id": "path_boundary_result.schema.json",
        "result_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "PathBoundary",
        "input_path": "src/file.txt",
        "resolved_path": "/tmp/repo/src/file.txt",
        "repo_relative_path": "src/file.txt",
        "inside_repo": True,
        "is_symlink": False,
        "symlink_escape": False,
        "is_l0": False,
        "is_protected": False,
        "operation": "READ",
        "status": "SUCCESS",
        "warnings": [],
        "errors": [],
    }


def _make_valid_file_op_dict():
    return {
        "schema_version": "1.0",
        "schema_id": "safe_file_operation.schema.json",
        "operation_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "SafeFileOps",
        "operation": "READ",
        "target_path": "/tmp/repo/src/file.txt",
        "status": "SUCCESS",
        "before_hash": None,
        "after_hash": "abc123",
        "bytes_read": 100,
        "bytes_written": 0,
        "decision_id": str(uuid4()),
        "warnings": [],
        "errors": [],
    }


def _make_valid_subprocess_dict():
    return {
        "schema_version": "1.0",
        "schema_id": "safe_subprocess_result.schema.json",
        "result_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "SafeSubprocess",
        "command": ["echo", "hello"],
        "working_directory": "/tmp/repo",
        "status": "ALLOW",
        "reason": "Allowed by policy",
        "timeout_seconds": 60,
        "stdout_redacted": None,
        "stderr_redacted": None,
        "warnings": [],
        "errors": [],
    }


def _make_valid_audit_dict():
    return {
        "schema_version": "1.0",
        "schema_id": "sandbox_audit.schema.json",
        "audit_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "SecuritySandbox",
        "event_type": "sandbox_decision",
        "operation": "READ",
        "target": "src/file.txt",
        "decision": "ALLOW",
        "reason": "Boundary check passed",
        "artifacts": [".agentx-init/security/sandbox_decisions.jsonl"],
        "success": True,
        "operation_allowed": True,
        "enforcement_success": True,
        "warnings": [],
        "errors": [],
    }


def _make_valid_redaction_dict():
    return {
        "schema_version": "1.0",
        "schema_id": "secret_redaction_result.schema.json",
        "result_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "SecretRedactor",
        "status": "SUCCESS",
        "redacted_text": "[REDACTED_API_KEY]",
        "redaction_count": 1,
        "redaction_types": ["OPENAI_API_KEY"],
        "warnings": [],
        "errors": [],
    }


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_sandbox_policy_schema_accepts_valid_policy():
    valid, errors = _validate(_make_valid_policy_dict(), "sandbox_policy.schema.json")
    assert valid, errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_sandbox_decision_schema_accepts_valid_decision():
    valid, errors = _validate(_make_valid_decision_dict(), "sandbox_decision.schema.json")
    assert valid, errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_sandbox_decision_schema_rejects_missing_required_fields():
    obj = _make_valid_decision_dict()
    del obj["decision"]
    valid, errors = _validate(obj, "sandbox_decision.schema.json")
    assert not valid


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_path_boundary_result_schema_accepts_valid_result():
    valid, errors = _validate(_make_valid_path_boundary_dict(), "path_boundary_result.schema.json")
    assert valid, errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_safe_file_operation_schema_accepts_valid_result():
    valid, errors = _validate(_make_valid_file_op_dict(), "safe_file_operation.schema.json")
    assert valid, errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_safe_subprocess_result_schema_accepts_valid_result():
    valid, errors = _validate(_make_valid_subprocess_dict(), "safe_subprocess_result.schema.json")
    assert valid, errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_secret_redaction_schema_accepts_valid_result():
    valid, errors = _validate(_make_valid_redaction_dict(), "secret_redaction_result.schema.json")
    assert valid, errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_sandbox_audit_schema_accepts_valid_audit():
    valid, errors = _validate(_make_valid_audit_dict(), "sandbox_audit.schema.json")
    assert valid, errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema package required")
def test_sandbox_audit_schema_rejects_missing_required_fields():
    obj = _make_valid_audit_dict()
    del obj["decision"]
    valid, errors = _validate(obj, "sandbox_audit.schema.json")
    assert not valid
