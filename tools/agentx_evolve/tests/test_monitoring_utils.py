from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_utils import (
    sha256_file, write_json_atomic, append_jsonl,
    read_json, ensure_dir, redact_payload,
)


def test_sha256_file(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("hello")
    h = sha256_file(p)
    assert isinstance(h, str)
    assert len(h) == 64


def test_sha256_file_deterministic(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("hello")
    assert sha256_file(p) == sha256_file(p)


def test_write_json_atomic(tmp_path):
    path = tmp_path / "test.json"
    data = {"key": "value"}
    result = write_json_atomic(path, data)
    assert result == path
    assert path.exists()
    import json
    assert json.loads(path.read_text()) == data


def test_write_json_atomic_nested_dir(tmp_path):
    path = tmp_path / "sub" / "nested" / "test.json"
    data = {"a": 1}
    result = write_json_atomic(path, data)
    assert result == path
    assert path.exists()


def test_write_json_atomic_empty_dict(tmp_path):
    path = tmp_path / "empty.json"
    result = write_json_atomic(path, {})
    assert result == path
    import json
    assert json.loads(path.read_text()) == {}


def test_append_jsonl(tmp_path):
    path = tmp_path / "log.jsonl"
    d1 = {"a": 1}
    d2 = {"b": 2}
    append_jsonl(path, d1)
    append_jsonl(path, d2)
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2
    import json
    assert json.loads(lines[0]) == d1
    assert json.loads(lines[1]) == d2


def test_append_jsonl_creates_parent(tmp_path):
    path = tmp_path / "sub" / "log.jsonl"
    append_jsonl(path, {"test": 1})
    assert path.exists()
    import json
    assert json.loads(path.read_text()) == {"test": 1}


def test_read_json(tmp_path):
    p = tmp_path / "data.json"
    p.write_text('{"key": "val"}')
    result = read_json(p)
    assert result == {"key": "val"}


def test_read_json_not_found(tmp_path):
    result = read_json(tmp_path / "nonexistent.json")
    assert result is None


def test_read_json_empty_file(tmp_path):
    p = tmp_path / "empty.json"
    p.write_text("")
    import json
    with pytest.raises(json.JSONDecodeError):
        read_json(p)


def test_ensure_dir(tmp_path):
    d = tmp_path / "new_dir" / "nested"
    result = ensure_dir(d)
    assert result == d
    assert d.exists()
    assert d.is_dir()


def test_ensure_dir_existing(tmp_path):
    d = tmp_path / "existing"
    d.mkdir()
    result = ensure_dir(d)
    assert result == d
    assert d.exists()


def test_redact_payload():
    payload = {
        "user": "alice",
        "password": "secret123",
        "nested": {"token": "abc", "keep": "visible"},
        "items": [{"api_key": "xyz"}, "plain"],
    }
    result = redact_payload(payload)
    assert result["user"] == "alice"
    assert result["password"] == "***REDACTED***"
    assert result["nested"]["token"] == "***REDACTED***"
    assert result["nested"]["keep"] == "visible"
    assert result["items"][0]["api_key"] == "***REDACTED***"
    assert result["items"][1] == "plain"


def test_redact_payload_empty():
    assert redact_payload({}) == {}


def test_redact_payload_custom_keys():
    payload = {"username": "alice", "secret_key": "s3cr3t"}
    result = redact_payload(payload, keys_to_redact={"secret_key"})
    assert result["username"] == "alice"
    assert result["secret_key"] == "***REDACTED***"


def test_redact_payload_no_matches():
    payload = {"name": "alice", "role": "admin"}
    result = redact_payload(payload)
    assert result == payload
