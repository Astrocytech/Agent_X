from __future__ import annotations
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter,
    TS_SUCCESS, TS_FAILED,
    new_id, utc_now_iso,
)

_ALLOWLISTED_COMMANDS: dict[str, list[str]] = {
    "python3": ["python3", "-c", "--version", "--help"],
    "python": ["python", "-c", "--version"],
    "pytest": ["python3", "-m", "pytest"],
    "pip": ["pip", "install", "--upgrade"],
    "ruff": ["ruff", "check", "format"],
    "mypy": ["mypy"],
    "black": ["black"],
    "git": ["git", "status", "diff", "log", "show", "branch"],
    "ls": ["ls"],
    "cat": ["cat"],
    "head": ["head"],
    "tail": ["tail"],
    "wc": ["wc"],
    "find": ["find"],
    "grep": ["grep", "rg", "grep"],
    "sort": ["sort"],
    "uniq": ["uniq"],
    "echo": ["echo"],
    "make": ["make"],
    "npm": ["npm", "test", "run", "install", "build"],
    "node": ["node"],
}


def _validate_command(command: list[str]) -> tuple[bool, str]:
    if not command:
        return False, "Empty command"
    base = command[0]
    if base not in _ALLOWLISTED_COMMANDS:
        return False, f"Command '{base}' is not allowlisted"
    prefix = _ALLOWLISTED_COMMANDS[base]
    for i, part in enumerate(command):
        if part in {"&&", "||", ";", "|", "$", "`"}:
            return False, f"Shell metacharacter not allowed: {part}"
        if part.startswith("-") and i > 0:
            allowed_flags = set(prefix[1:])
            flag_base = part.split("=")[0]
            if part not in allowed_flags:
                return False, f"Flag '{part}' not allowed for '{base}'"
    return True, ""


def _run_command(call: ToolCall) -> ToolResult:
    command = call.arguments.get("command", [])
    if not command:
        return ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=call.tool_name, status=TS_FAILED,
            message="Missing required argument: command",
            errors=["command must be a non-empty list of strings"],
        )
    valid, reason = _validate_command(command)
    if not valid:
        return ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=call.tool_name, status=TS_FAILED,
            message=f"Command blocked: {reason}",
            errors=[reason],
        )
    import subprocess
    try:
        proc = subprocess.run(
            command,
            capture_output=True, text=True, timeout=30,
        )
        return ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=call.tool_name, status=TS_SUCCESS,
            message=f"Command completed with exit code {proc.returncode}",
            data={
                "command": command,
                "returncode": proc.returncode,
                "stdout": proc.stdout[:100000],
                "stderr": proc.stderr[:50000],
            },
        )
    except subprocess.TimeoutExpired:
        return ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=call.tool_name, status=TS_FAILED,
            message="Command timed out after 30 seconds",
            errors=["TimeoutExpired"],
        )
    except FileNotFoundError:
        return ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=call.tool_name, status=TS_FAILED,
            message=f"Command not found: {command[0]}",
            errors=[f"FileNotFoundError: {command[0]}"],
        )
    except Exception as e:
        return ToolResult(
            result_id=new_id("tr"), timestamp=utc_now_iso(),
            tool_name=call.tool_name, status=TS_FAILED,
            message=f"Execution error: {e}",
            errors=[str(e)],
        )


def make_run_command_tool() -> tuple[ToolDefinition, callable]:
    defn = ToolDefinition(
        tool_id=new_id("td"), timestamp=utc_now_iso(),
        tool_name="run_allowlisted_command",
        description="Run an allowlisted command with arguments",
        parameters=[
            ToolParameter(name="command", param_type="array",
                          description="Command and arguments as a list", required=True),
        ],
        handler_name="command_runner_adapter.run_command",
        side_effect="read",
        requires_approval=True,
    )
    return defn, _run_command
