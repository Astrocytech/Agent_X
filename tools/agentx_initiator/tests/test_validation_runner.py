import pytest
from agentx_initiator.core.validation_runner import _resolve_command, run_validation, run_validator
from agentx_initiator.core.validation_allowlist import get_default_allowlist, is_allowlisted
from agentx_initiator.core.validation_model import ValidationRun


def test_resolve_command_no_substitution():
    cmd = _resolve_command("python --version")
    assert "python --version" in cmd


def test_is_allowlisted_found():
    allowed, entry_id = is_allowlisted("python -m pytest", get_default_allowlist())
    assert allowed
    assert entry_id


def test_is_allowlisted_not_found():
    allowed, entry_id = is_allowlisted("rm -rf /", get_default_allowlist())
    assert not allowed
    assert not entry_id


def test_run_validator_not_allowed():
    run = run_validator("rm -rf /")
    assert run.status == "ERROR"
    assert "not in allowlist" in run.stderr


def test_validation_run_dataclass():
    vr = ValidationRun(run_id="test-1", command="echo hi", status="PASS", returncode=0, stdout="hi", stderr="", duration_ms=10, entry_id="val-001")
    assert vr.status == "PASS"
