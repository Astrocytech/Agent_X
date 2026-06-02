import pytest
from pathlib import Path
from agentx_initiator.core.config import load_config, AgentXInitConfig


def test_load_default_config():
    config = load_config()
    assert isinstance(config, AgentXInitConfig)
    assert config.version == "1.0.0"
    assert config.state_dir == ".agentx-init"


def test_config_has_allowlisted_commands():
    config = load_config()
    assert len(config.allowlisted_commands) > 0


def test_config_has_risk_levels():
    config = load_config()
    assert "R0" in config.risk_levels
    assert "R4" in config.risk_levels
