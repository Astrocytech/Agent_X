import json
import os
from pathlib import Path
import pytest

from agentx_evolve.tools.tool_call_logger import (
    append_tool_call,
    append_tool_result,
    append_blocked_tool,
    append_invalid_tool,
    write_latest_tool_call,
    write_latest_tool_result,
    write_tool_call_evidence,
)
from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    InvalidToolRecord,
)


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    return tmp_path


def _new_call(tool_name="test_tool") -> ToolCall:
    return ToolCall(
        tool_call_id="call_abc123",
        timestamp="2025-06-05T00:00:00",
        source_component="test",
        tool_name=tool_name,
        arguments={"key": "value"},
    )


def _new_result(tool_call: ToolCall | None = None) -> ToolResult:
    tc = tool_call or _new_call()
    return ToolResult(
        tool_result_id="res_abc123",
        tool_call_id=tc.tool_call_id,
        timestamp="2025-06-05T00:00:01",
        source_component="test",
        tool_name=tc.tool_name,
        status="SUCCESS",
        exit_code=0,
        message="ok",
        data={"result": 42},
    )


def _call_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "tool_calls"


def test_append_tool_call_creates_file(repo_root):
    tc = _new_call()
    result = append_tool_call(tc, repo_root)
    assert result.get("status") == "SUCCESS"
    call_dir = _call_dir(repo_root)
    assert (call_dir / "tool_call_history.jsonl").exists()


def test_append_tool_call_appends(repo_root):
    tc1 = _new_call()
    tc2 = _new_call()
    tc2.tool_call_id = "call_def456"
    append_tool_call(tc1, repo_root)
    append_tool_call(tc2, repo_root)
    path = _call_dir(repo_root) / "tool_call_history.jsonl"
    with open(path) as f:
        assert len(f.readlines()) == 2


def test_append_tool_result_creates_file(repo_root):
    tr = _new_result()
    result = append_tool_result(tr, repo_root)
    assert result.get("status") == "SUCCESS"
    assert (_call_dir(repo_root) / "tool_result_history.jsonl").exists()


def test_append_blocked_tool_logs(repo_root):
    tc = _new_call()
    tr = _new_result(tc)
    result = append_blocked_tool(tc, tr, repo_root)
    assert result.get("status") == "SUCCESS"


def test_append_invalid_tool_logs(repo_root):
    record = InvalidToolRecord(tool_name="nonexistent_tool", reason="TOOL_NOT_FOUND")
    result = append_invalid_tool(record, repo_root)
    assert result.get("status") == "SUCCESS"


def test_write_latest_tool_call_atomic(repo_root):
    tc = _new_call()
    result = write_latest_tool_call(tc, repo_root)
    assert result.get("status") == "SUCCESS"
    path = _call_dir(repo_root) / "latest_tool_call.json"
    assert path.exists()
    with open(path) as f:
        parsed = json.loads(f.read())
    assert parsed["tool_call_id"] == "call_abc123"


def test_write_latest_tool_result_atomic(repo_root):
    tr = _new_result()
    result = write_latest_tool_result(tr, repo_root)
    assert result.get("status") == "SUCCESS"
    path = _call_dir(repo_root) / "latest_tool_result.json"
    assert path.exists()


def test_write_tool_call_evidence_integration(repo_root):
    tc = _new_call()
    tr = _new_result(tc)
    result = write_tool_call_evidence(tc, tr, repo_root)
    assert result.get("status") == "SUCCESS"
    assert "call_history" in result
    assert "result_history" in result
    assert "latest_call" in result
    assert "latest_result" in result


def test_append_tool_call_redacts_secrets(repo_root):
    tc = _new_call()
    tc.arguments = {"api_key": "sk-1234567890abcdef"}
    append_tool_call(tc, repo_root)
    path = _call_dir(repo_root) / "tool_call_history.jsonl"
    with open(path) as f:
        content = f.read()
    assert "sk-1234567890abcdef" not in content
