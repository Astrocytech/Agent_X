import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import redact_sensitive_fields


def test_redact_sensitive_fields_removes_secret_keys():
    data = {
        "name": "test",
        "secret": "should-not-appear",
        "normal_field": "visible",
    }
    redacted = redact_sensitive_fields(data)
    assert "name" in redacted
    assert "normal_field" in redacted
    assert "secret" not in redacted


def test_redact_sensitive_fields_is_case_insensitive():
    data = {
        "Secret": "should-not-appear",
        "PASSWORD": "should-not-appear",
        "API_KEY": "should-not-appear",
        "normal": "visible",
    }
    redacted = redact_sensitive_fields(data)
    assert "Secret" not in redacted
    assert "PASSWORD" not in redacted
    assert "API_KEY" not in redacted
    assert "normal" in redacted


def test_redact_sensitive_fields_preserves_non_sensitive_keys():
    data = {
        "name": "alice",
        "role": "admin",
        "reason": "approved",
        "request_id": "hreq-001",
    }
    redacted = redact_sensitive_fields(data)
    assert redacted == data


def test_redact_sensitive_fields_on_nested_dict():
    data = {
        "metadata": {
            "secret": "should-not-appear",
            "label": "visible",
        },
        "config": {
            "password": "should-not-appear",
            "timeout": 30,
        },
        "name": "test",
    }
    redacted = redact_sensitive_fields(data)
    assert "name" in redacted
    assert "metadata" in redacted
    assert "secret" in redacted["metadata"]
    assert "label" in redacted["metadata"]
    assert "config" in redacted
    assert "password" in redacted["config"]
    assert "timeout" in redacted["config"]


def test_redact_sensitive_fields_removes_all_sensitive_keys():
    data = {
        "secret": "s",
        "password": "p",
        "token": "t",
        "api_key": "ak",
        "private_key": "pk",
        "raw_prompt": "rp",
        "safe": "ok",
    }
    redacted = redact_sensitive_fields(data)
    assert "safe" in redacted
    assert "secret" not in redacted
    assert "password" not in redacted
    assert "token" not in redacted
    assert "api_key" not in redacted
    assert "private_key" not in redacted
    assert "raw_prompt" not in redacted
