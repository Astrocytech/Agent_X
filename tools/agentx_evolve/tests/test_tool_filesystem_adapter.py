import tempfile
from pathlib import Path

from agentx_evolve.tool.filesystem_adapter import (
    make_read_file_tool, make_write_file_tool, make_list_files_tool,
)
from agentx_evolve.tool.tool_models import ToolCall, TS_SUCCESS, TS_FAILED


def test_make_read_file_tool():
    defn, handler = make_read_file_tool()
    assert defn.tool_name == "read_file_guarded"


def test_make_write_file_tool():
    defn, handler = make_write_file_tool()
    assert defn.tool_name == "write_file_guarded"
    assert defn.requires_approval is True


def test_make_list_files_tool():
    defn, handler = make_list_files_tool()
    assert defn.tool_name == "list_files_guarded"


def test_read_file_success(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    _defn, handler = make_read_file_tool()
    call = ToolCall(tool_name="read_file_guarded", arguments={"path": str(test_file)})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.data["content"] == "hello world"
    assert result.data["bytes"] == 11


def test_read_file_not_found():
    _defn, handler = make_read_file_tool()
    call = ToolCall(tool_name="read_file_guarded", arguments={"path": "/nonexistent/path"})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "File not found" in result.message or "not found" in result.message


def test_read_file_missing_path():
    _defn, handler = make_read_file_tool()
    call = ToolCall(tool_name="read_file_guarded", arguments={})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "Missing required argument" in result.message


def test_write_file_success(tmp_path):
    target = tmp_path / "sub" / "out.txt"
    _defn, handler = make_write_file_tool()
    call = ToolCall(tool_name="write_file_guarded", arguments={"path": str(target), "content": "test data"})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert target.read_text() == "test data"


def test_write_file_missing_path():
    _defn, handler = make_write_file_tool()
    call = ToolCall(tool_name="write_file_guarded", arguments={"content": "data"})
    result = handler(call)
    assert result.status == TS_FAILED


def test_list_files_success(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    _defn, handler = make_list_files_tool()
    call = ToolCall(tool_name="list_files_guarded", arguments={"path": str(tmp_path), "pattern": "*.txt"})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.data["count"] == 2


def test_list_files_not_found():
    _defn, handler = make_list_files_tool()
    call = ToolCall(tool_name="list_files_guarded", arguments={"path": "/nonexistent"})
    result = handler(call)
    assert result.status == TS_FAILED
