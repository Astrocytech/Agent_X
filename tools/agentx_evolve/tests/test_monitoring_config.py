from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_config import (
    MonitoringConfig, DEFAULT_CONFIG, load_monitoring_config,
)


def test_monitoring_config_defaults():
    config = MonitoringConfig()
    assert config.enabled is True
    assert config.monitoring_root == ".agentx-init/monitoring"
    assert config.retention_days == 30
    assert config.max_events == 10000
    assert config.max_metrics == 100000
    assert config.health_check_interval_seconds == 300
    assert config.alert_evaluation_interval_seconds == 60
    assert config.trace_enabled is True
    assert config.metric_collection_enabled is True
    assert config.redact_secrets is True
    assert "password" in config.redacted_keys
    assert config.component == "monitoring"


def test_default_config():
    assert DEFAULT_CONFIG.enabled is True
    assert DEFAULT_CONFIG.retention_days == 30


def test_monitoring_config_custom():
    config = MonitoringConfig(
        enabled=False,
        retention_days=7,
        component="custom_monitor",
        max_events=100,
    )
    assert config.enabled is False
    assert config.retention_days == 7
    assert config.component == "custom_monitor"
    assert config.max_events == 100


def test_load_monitoring_config_none():
    config = load_monitoring_config()
    assert config is DEFAULT_CONFIG


def test_load_monitoring_config_nonexistent_path(tmp_path):
    path = tmp_path / "nonexistent.json"
    config = load_monitoring_config(path)
    assert config is DEFAULT_CONFIG


def test_load_monitoring_config_from_file(tmp_path):
    config_path = tmp_path / "monitoring_config.json"
    config_path.write_text('{"enabled": false, "retention_days": 7, "component": "test"}')
    config = load_monitoring_config(config_path)
    assert config.enabled is False
    assert config.retention_days == 7
    assert config.component == "test"


def test_load_monitoring_config_ignores_unknown_keys(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"enabled": false, "unknown_key": "ignored"}')
    config = load_monitoring_config(config_path)
    assert config.enabled is False
    assert not hasattr(config, "unknown_key")


def test_load_monitoring_config_default_overrides(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"enabled": false}')
    config = load_monitoring_config(config_path)
    assert config.enabled is False
    assert config.retention_days == 30
    assert config.max_events == 10000


def test_monitoring_config_redacted_keys_tuple():
    config = MonitoringConfig()
    assert isinstance(config.redacted_keys, tuple)
    assert "secret" in config.redacted_keys
    assert "token" in config.redacted_keys
    assert "api_key" in config.redacted_keys
