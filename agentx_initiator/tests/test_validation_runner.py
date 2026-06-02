import pytest
from agentx_initiator.core.validation_runner import _resolve_command


pytestmark = pytest.mark.skip(reason="PM2 validation_runner not active in Product Milestone 1")


def test_resolve_command_no_substitution():
    cmd = _resolve_command("python --version")
    assert "python --version" in cmd
