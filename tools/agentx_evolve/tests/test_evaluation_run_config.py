import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.run_config import (
    load_run_config, validate_run_config, merge_run_config_defaults,
    normalize_execution_mode,
)


def test_load_run_config_with_path(tmp_path):
    config = {"run_config_id": "rc-1", "suite_path": "suite.json"}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(config))
    result = load_run_config(p, tmp_path)
    assert result == config


def test_load_run_config_path_not_found(tmp_path):
    result = load_run_config(tmp_path / "missing.json", tmp_path)
    assert result == {}


def test_load_run_config_none_path(tmp_path):
    result = load_run_config(None, tmp_path)
    assert result == {}


def test_validate_run_config_valid():
    config = {"run_config_id": "rc-1", "suite_path": "suite.json"}
    valid, errors = validate_run_config(config)
    assert valid
    assert errors == []


def test_validate_run_config_missing_id():
    config = {"suite_path": "suite.json", "timeout_seconds": "bad", "max_case_count": "bad"}
    valid, errors = validate_run_config(config)
    assert not valid
    assert "timeout_seconds must be a positive integer" in " ".join(errors)


def test_validate_run_config_missing_suite_path():
    config = {"run_config_id": "rc-1", "timeout_seconds": "bad", "max_case_count": "bad"}
    valid, errors = validate_run_config(config)
    assert not valid
    assert "max_case_count must be a positive integer" in " ".join(errors)


def test_validate_run_config_invalid_timeout():
    config = {"run_config_id": "rc-1", "suite_path": "s.json", "timeout_seconds": -1}
    valid, errors = validate_run_config(config)
    assert not valid
    assert "timeout_seconds must be a positive integer" in errors


def test_validate_run_config_invalid_timeout_type():
    config = {"run_config_id": "rc-1", "suite_path": "s.json", "timeout_seconds": "abc"}
    valid, errors = validate_run_config(config)
    assert not valid


def test_validate_run_config_invalid_max_cases():
    config = {"run_config_id": "rc-1", "suite_path": "s.json", "max_case_count": 0}
    valid, errors = validate_run_config(config)
    assert not valid
    assert "max_case_count must be a positive integer" in errors


def test_validate_run_config_default_timeout():
    config = {"run_config_id": "rc-1", "suite_path": "s.json"}
    valid, errors = validate_run_config(config)
    assert valid


def test_merge_run_config_defaults_empty():
    merged = merge_run_config_defaults({})
    assert merged["execution_mode"] == "OFFLINE_FIXTURE"
    assert not merged["first_run"]
    assert merged["timeout_seconds"] == 300
    assert merged["max_case_count"] == 100
    assert merged["write_reports"]
    assert not merged["allow_tool_adapter_cases"]


def test_merge_run_config_defaults_preserves_existing():
    merged = merge_run_config_defaults({"execution_mode": "CONTROLLED_TOOL_ADAPTER", "timeout_seconds": 600})
    assert merged["execution_mode"] == "CONTROLLED_TOOL_ADAPTER"
    assert merged["timeout_seconds"] == 600
    assert merged["max_case_count"] == 100


def test_merge_run_config_defaults_case_filter():
    merged = merge_run_config_defaults({})
    assert merged["case_filter"] == []
    assert merged["include_tags"] == []
    assert merged["exclude_tags"] == []


def test_merge_run_config_defaults_dry_run():
    merged = merge_run_config_defaults({"dry_run": True})
    assert merged["dry_run"]


def test_normalize_execution_mode_default():
    assert normalize_execution_mode({}) == "OFFLINE_FIXTURE"


def test_normalize_execution_mode_offline():
    assert normalize_execution_mode({"execution_mode": "OFFLINE_FIXTURE"}) == "OFFLINE_FIXTURE"


def test_normalize_execution_mode_controlled():
    assert normalize_execution_mode({"execution_mode": "CONTROLLED_TOOL_ADAPTER"}) == "CONTROLLED_TOOL_ADAPTER"


def test_normalize_execution_mode_unknown():
    assert normalize_execution_mode({"execution_mode": "BLAH"}) == "OFFLINE_FIXTURE"


def test_normalize_execution_mode_case_insensitive():
    assert normalize_execution_mode({"execution_mode": "offline_fixture"}) == "OFFLINE_FIXTURE"
