import pytest
from agentx_initiator.core.jsonl_store import append_jsonl, read_jsonl


def test_append_and_read(tmp_path):
    log = tmp_path / "events.jsonl"
    result = append_jsonl(log, {"event": "test"})
    assert result.status == "SUCCESS"
    records = read_jsonl(log)
    assert len(records) == 1
    assert records[0]["event"] == "test"


def test_read_nonexistent(tmp_path):
    records = read_jsonl(tmp_path / "nonexistent.jsonl")
    assert records == []


def test_append_multiple(tmp_path):
    log = tmp_path / "events.jsonl"
    for i in range(3):
        append_jsonl(log, {"i": i})
    records = read_jsonl(log)
    assert len(records) == 3
