from agentx_initiator.core.validation_runner import _resolve_command


def test_resolve_command_no_substitution():
    cmd = _resolve_command("python --version")
    assert "python --version" in cmd
