from agentx_initiator.cli.commands.help import run, register
from agentx_initiator.cli.registry import register as reg_register, CommandEntry, clear
import argparse


def _make_args(command="help"):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    register(sub)
    return parser.parse_args(["help"])


def test_cli_help_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    register(sub)
    parsed = parser.parse_args(["help"])
    assert parsed.command == "help"


def test_cli_help_runs_without_error():
    clear()
    reg_register(CommandEntry(
        name="scan", category="SCAN",
        description="Scan repository",
        writes_artifacts=True,
    ))
    reg_register(CommandEntry(
        name="status", category="STATUS",
        description="Status report",
        writes_artifacts=True,
    ))
    reg_register(CommandEntry(
        name="explain", category="RESERVED",
        description="Explain (PM2)",
        writes_artifacts=False,
    ))
    try:
        run(None)
    except SystemExit:
        pass


def test_cli_help_lists_active_commands():
    clear()
    reg_register(CommandEntry(
        name="help", category="HELP", description="Show help",
        writes_artifacts=False,
    ))
    reg_register(CommandEntry(
        name="scan", category="SCAN", description="Scan repo",
        writes_artifacts=True,
    ))
    reg_register(CommandEntry(
        name="status", category="STATUS", description="Show status",
        writes_artifacts=True,
    ))
    import io
    import sys
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        run(None)
    except SystemExit:
        pass
    sys.stdout = old_stdout
    output = captured.getvalue()
    assert "help" in output
    assert "scan" in output
    assert "status" in output
