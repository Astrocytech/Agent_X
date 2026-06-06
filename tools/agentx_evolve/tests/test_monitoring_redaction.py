import pytest
from agentx_evolve.monitoring.monitoring_config import redact_sensitive_keys


class TestRedactSensitiveKeys:
    def test_redaction_hides_specified_keys(self):
        data = {
            "username": "alice",
            "password": "supersecret",
            "api_key": "sk-12345",
            "token": "ghp_abc",
        }
        result = redact_sensitive_keys(data)
        assert result["username"] == "alice"
        assert result["password"] == "***REDACTED***"
        assert result["api_key"] == "***REDACTED***"
        assert result["token"] == "***REDACTED***"

    def test_redaction_preserves_non_sensitive_keys(self):
        data = {
            "event_type": "INFO",
            "session_id": "sess-001",
            "message": "all good",
        }
        result = redact_sensitive_keys(data)
        assert result == data

    def test_redaction_case_insensitive(self):
        data = {"Secret": "value", "API_Key": "value"}
        result = redact_sensitive_keys(data)
        assert result["Secret"] == "***REDACTED***"
        assert result["API_Key"] == "***REDACTED***"

    def test_redaction_recurses_into_nested_dicts(self):
        data = {
            "config": {
                "password": "nested_secret",
                "normal": "visible",
            },
        }
        result = redact_sensitive_keys(data)
        assert result["config"]["password"] == "***REDACTED***"
        assert result["config"]["normal"] == "visible"

    def test_redaction_recurses_into_lists(self):
        data = {
            "items": [
                {"password": "secret1", "name": "a"},
                {"password": "secret2", "name": "b"},
            ],
        }
        result = redact_sensitive_keys(data)
        assert result["items"][0]["password"] == "***REDACTED***"
        assert result["items"][1]["password"] == "***REDACTED***"
        assert result["items"][0]["name"] == "a"

    def test_custom_keys_set(self):
        data = {"my_key": "secret", "other": "visible"}
        result = redact_sensitive_keys(data, keys={"my_key"})
        assert result["my_key"] == "***REDACTED***"
        assert result["other"] == "visible"
