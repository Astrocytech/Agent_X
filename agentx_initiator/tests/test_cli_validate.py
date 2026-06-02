import pytest
from agentx_initiator.core.validation_runner import _resolve_command


pytestmark = pytest.mark.skip(reason="PM2 validation_runner not active in Product Milestone 1")


def test_validate_resolve():
    cmd = _resolve_command("python --version")
    assert cmd == "python --version"
