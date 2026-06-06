import json
from pathlib import Path

from tools.agentx_evolve.final_acceptance.audit_logger import (
    append_event, append_command_record,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import runtime_root


class TestAppendEvent:
    def test_writes_event_file(self, tmp_path: Path):
        append_event(tmp_path, "test_event", {"key": "value"})
        log_path = runtime_root(tmp_path) / "final_acceptance_event_history.jsonl"
        assert log_path.exists()

    def test_event_content(self, tmp_path: Path):
        append_event(tmp_path, "test_event", {"key": "value"})
        log_path = runtime_root(tmp_path) / "final_acceptance_event_history.jsonl"
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["event_type"] == "test_event"
        assert entry["data"]["key"] == "value"
        assert "timestamp" in entry

    def test_multiple_events_append(self, tmp_path: Path):
        append_event(tmp_path, "event1", {"n": 1})
        append_event(tmp_path, "event2", {"n": 2})
        log_path = runtime_root(tmp_path) / "final_acceptance_event_history.jsonl"
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

    def test_event_with_empty_data(self, tmp_path: Path):
        append_event(tmp_path, "empty_event", {})
        log_path = runtime_root(tmp_path) / "final_acceptance_event_history.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["data"] == {}

    def test_event_creates_runtime_root(self, tmp_path: Path):
        append_event(tmp_path, "test", {"x": 1})
        assert runtime_root(tmp_path).exists()

    def test_nested_data(self, tmp_path: Path):
        append_event(tmp_path, "nested", {"inner": {"a": [1, 2]}})
        log_path = runtime_root(tmp_path) / "final_acceptance_event_history.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["data"]["inner"]["a"] == [1, 2]


class TestAppendCommandRecord:
    def test_writes_command_file(self, tmp_path: Path):
        append_command_record(tmp_path, "test_cmd", "PASS", 0, "All good")
        log_path = runtime_root(tmp_path) / "final_acceptance_command_history.jsonl"
        assert log_path.exists()

    def test_command_content(self, tmp_path: Path):
        append_command_record(tmp_path, "compileall", "PASS", 0, "OK")
        log_path = runtime_root(tmp_path) / "final_acceptance_command_history.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["command_name"] == "compileall"
        assert entry["status"] == "PASS"
        assert entry["exit_code"] == 0
        assert entry["summary"] == "OK"

    def test_multiple_commands(self, tmp_path: Path):
        append_command_record(tmp_path, "cmd1", "PASS", 0, "ok")
        append_command_record(tmp_path, "cmd2", "FAIL", 1, "fail")
        log_path = runtime_root(tmp_path) / "final_acceptance_command_history.jsonl"
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

    def test_command_with_none_exit_code(self, tmp_path: Path):
        append_command_record(tmp_path, "skipped", "NOT_RUN", None, "Skipped")
        log_path = runtime_root(tmp_path) / "final_acceptance_command_history.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["exit_code"] is None

    def test_command_empty_summary(self, tmp_path: Path):
        append_command_record(tmp_path, "empty", "PASS", 0, "")
        log_path = runtime_root(tmp_path) / "final_acceptance_command_history.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["summary"] == ""
