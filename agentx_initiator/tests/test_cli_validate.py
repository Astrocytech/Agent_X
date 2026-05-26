from agentx_initiator.core.validation_runner import _resolve_command


def test_validate_resolve():
    cmd = _resolve_command("python --version")
    assert cmd == "python --version"
