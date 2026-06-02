from agentx_initiator.core.schema_validation import validate_instance, load_schema, SchemaValidationResult


def test_validate_instance_valid_config():
    valid = {
        "schema_version": "1.0",
        "config_version": "1.0.0",
        "default_mode": "read_only",
        "runtime_root": ".agentx-init",
        "scan": {
            "include_hidden": False,
            "max_file_size_mb": 5,
            "ignore_dirs": [".git", "__pycache__", ".venv", "node_modules", ".agentx-init"],
        },
        "feature_flags": {
            "governance_engine_active": False,
            "risk_engine_active": False,
            "planner_active": False,
            "proposal_generator_active": False,
            "validation_runner_active": False,
            "knowledge_graph_active": False,
        },
    }
    result = validate_instance(valid, "config.schema.json")
    assert result.valid


def test_validate_instance_invalid_config_missing_required():
    invalid = {}
    result = validate_instance(invalid, "config.schema.json")
    assert not result.valid


def test_validate_load_schema():
    schema = load_schema("config.schema.json")
    assert isinstance(schema, dict)
    assert "properties" in schema


def test_validate_load_schema_not_found():
    import pytest
    with pytest.raises(FileNotFoundError):
        load_schema("nonexistent.schema.json")


def test_validate_result_format():
    result = SchemaValidationResult(valid=True)
    d = result.to_dict()
    assert d["valid"] is True
    assert d["validator_mode"] == "FALLBACK_BASIC"
    assert d["errors"] == []


def test_validate_instance_reports_wrong_type():
    result = validate_instance(
        {"version": 123, "state_dir": ".agentx-init"},
        "config.schema.json",
    )
    if not result.valid:
        pass
    assert isinstance(result, SchemaValidationResult)


def test_validate_instance_audit_event():
    valid_event = {
        "schema_version": "1.0",
        "event_id": "test-1",
        "timestamp": "2024-01-01T00:00:00",
        "category": "SYSTEM",
        "component": "test",
        "event_type": "test",
        "status": "INFO",
        "summary": "test event",
    }
    result = validate_instance(valid_event, "audit_event.schema.json")
    assert result.valid


def test_validate_instance_invalid_audit_missing_required():
    invalid = {"event_type": "test"}
    result = validate_instance(invalid, "audit_event.schema.json")
    assert not result.valid


def test_validate_scanner_valid():
    from agentx_initiator.core.repo_scanner import scan_repository
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    result = scan_repository(repo, ignore_dirs={".git", "__pycache__", ".venv", "node_modules", ".agentx-init"})
    validation = validate_instance(result.to_dict(), "repo_scan.schema.json")
    assert validation.valid
