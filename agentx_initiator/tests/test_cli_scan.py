from agentx_initiator.cli.commands.scan import run
from agentx_initiator.cli.models import CLICommandResponse


class _Args:
    def __init__(self, repo_root):
        self.repo_root = repo_root


def test_scan_cli_handler_default():
    result = run(_Args("."))
    assert isinstance(result, CLICommandResponse)
    assert result.command == "scan"
    assert result.status in ("SUCCESS", "PARTIAL")
    assert result.exit_code in (0, 4)
    assert result.data.get("total_files", 0) > 0


def test_scan_cli_invalid_path():
    result = run(_Args("/nonexistent_path_xyz123"))
    assert isinstance(result, CLICommandResponse)
    assert result.status == "FAILED"
    assert result.exit_code == 1


def test_scan_cli_file_not_directory():
    result = run(_Args("setup.py"))
    assert isinstance(result, CLICommandResponse)
    assert result.status == "FAILED"
    assert result.exit_code == 1
