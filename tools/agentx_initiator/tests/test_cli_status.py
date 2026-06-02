import json
from agentx_initiator.cli.commands.status import run
from agentx_initiator.cli.models import CLICommandResponse
from agentx_initiator.core.path_registry import get_path


class _Args:
    def __init__(self, repo_root):
        self.repo_root = repo_root


def _clear_scan_artifact():
    path = get_path("repo_scan_latest")
    if path.exists():
        path.unlink()


def test_status_blocked_without_scan():
    _clear_scan_artifact()
    result = run(_Args("."))
    assert isinstance(result, CLICommandResponse)
    assert result.status == "BLOCKED"
    assert result.exit_code == 3


def test_status_after_scan():
    from agentx_initiator.cli.commands.scan import run as scan_run
    scan_result = scan_run(_Args("."))
    assert scan_result.status in ("SUCCESS", "PARTIAL")
    result = run(_Args("."))
    assert isinstance(result, CLICommandResponse)
    assert result.command == "status"
    assert result.status in ("SUCCESS", "PARTIAL")
    assert result.exit_code in (0, 4)
