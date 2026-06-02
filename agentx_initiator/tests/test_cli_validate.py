import pytest
from agentx_initiator.core.validation_runner import _resolve_command, run_validator
from agentx_initiator.core.validation_allowlist import get_default_allowlist


def test_validate_resolve():
    cmd = _resolve_command("python --version")
    assert cmd == "python --version"


def test_validate_not_allowed():
    run = run_validator("rm -rf /")
    assert run.status == "ERROR"
