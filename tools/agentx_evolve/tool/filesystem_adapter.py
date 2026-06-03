from __future__ import annotations
from pathlib import Path
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter,
    TS_SUCCESS, TS_BLOCKED, TS_FAILED,
    new_id, utc_now_iso,
)


def _make_result(call: ToolCall, status: str, message: str, data: dict | None = None) -> ToolResult:
    return ToolResult(
        result_id=new_id("tr"),
        timestamp=utc_now_iso(),
        tool_name=call.tool_name,
        status=status,
        message=message,
        data=data or {},
    )


def _read_file(call: ToolCall) -> ToolResult:
    path = call.arguments.get("path", "")
    if not path:
        return _make_result(call, TS_FAILED, "Missing required argument: path")
    file_path = Path(path)
    if not file_path.exists():
        return _make_result(call, TS_FAILED, f"File not found: {path}")
    if not file_path.is_file():
        return _make_result(call, TS_FAILED, f"Not a file: {path}")
    try:
        content = file_path.read_text(encoding="utf-8")
        return _make_result(call, TS_SUCCESS, f"Read {len(content)} bytes from {path}", {
            "path": str(file_path),
            "content": content,
            "bytes": len(content),
        })
    except Exception as e:
        return _make_result(call, TS_FAILED, f"Read error: {e}")


def _write_file(call: ToolCall) -> ToolResult:
    path = call.arguments.get("path", "")
    content = call.arguments.get("content", "")
    if not path:
        return _make_result(call, TS_FAILED, "Missing required argument: path")
    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return _make_result(call, TS_SUCCESS, f"Wrote {len(content)} bytes to {path}", {
            "path": str(file_path),
            "bytes": len(content),
        })
    except Exception as e:
        return _make_result(call, TS_FAILED, f"Write error: {e}")


def _list_files(call: ToolCall) -> ToolResult:
    path = call.arguments.get("path", ".")
    pattern = call.arguments.get("pattern", "*")
    dir_path = Path(path)
    if not dir_path.exists():
        return _make_result(call, TS_FAILED, f"Directory not found: {path}")
    if not dir_path.is_dir():
        return _make_result(call, TS_FAILED, f"Not a directory: {path}")
    try:
        files = sorted(str(p) for p in dir_path.glob(pattern))
        return _make_result(call, TS_SUCCESS, f"Found {len(files)} entries in {path}", {
            "path": str(dir_path),
            "files": files,
            "count": len(files),
        })
    except Exception as e:
        return _make_result(call, TS_FAILED, f"List error: {e}")


def make_read_file_tool() -> tuple[ToolDefinition, callable]:
    defn = ToolDefinition(
        tool_id=new_id("td"),
        timestamp=utc_now_iso(),
        tool_name="read_file_guarded",
        description="Read a file from disk with path validation",
        parameters=[
            ToolParameter(name="path", param_type="string", description="Absolute path to file", required=True),
        ],
        handler_name="filesystem_adapter.read_file",
        side_effect="read",
    )
    return defn, _read_file


def make_write_file_tool() -> tuple[ToolDefinition, callable]:
    defn = ToolDefinition(
        tool_id=new_id("td"),
        timestamp=utc_now_iso(),
        tool_name="write_file_guarded",
        description="Write content to a file with path validation",
        parameters=[
            ToolParameter(name="path", param_type="string", description="Absolute path to file", required=True),
            ToolParameter(name="content", param_type="string", description="File content to write", required=True),
        ],
        handler_name="filesystem_adapter.write_file",
        side_effect="write",
        requires_approval=True,
    )
    return defn, _write_file


def make_list_files_tool() -> tuple[ToolDefinition, callable]:
    defn = ToolDefinition(
        tool_id=new_id("td"),
        timestamp=utc_now_iso(),
        tool_name="list_files_guarded",
        description="List files in a directory using a glob pattern",
        parameters=[
            ToolParameter(name="path", param_type="string", description="Directory path", required=False, default="."),
            ToolParameter(name="pattern", param_type="string", description="Glob pattern", required=False, default="*"),
        ],
        handler_name="filesystem_adapter.list_files",
        side_effect="read",
    )
    return defn, _list_files
