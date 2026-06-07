import json
import urllib.error
from unittest.mock import patch, MagicMock

import pytest

from agentx_evolve.providers.opencode_provider import (
    OpenCodeProvider, OpenCodeProviderError,
    BLOCKED_AUTH, BLOCKED_SERVER,
    FAIL_MODEL, FAIL_RATE_LIMIT, FAIL_SERVER, FAIL_TIMEOUT, FAIL_MALFORMED,
)

SESSION_ID = "ses_test123"
MESSAGE_TEXT = "Hello!"
SESSION_RESPONSE = {"id": SESSION_ID}
MESSAGE_RESPONSE = {
    "info": {"finish": "stop"},
    "parts": [
        {"type": "step-start", "id": "p1"},
        {"type": "reasoning", "text": "thinking..."},
        {"type": "text", "text": MESSAGE_TEXT, "id": "p2"},
        {"type": "step-finish", "reason": "stop"},
    ],
}


def _mock_cm(data: dict) -> MagicMock:
    """Build a context manager mock whose __enter__ returns a response mock."""
    cm = MagicMock()
    cm.__enter__.return_value.read.return_value = json.dumps(data).encode("utf-8")
    return cm


class TestOpenCodeProvider:
    def setup_method(self):
        self.provider = OpenCodeProvider(
            base_url="http://127.0.0.1:14096",
            model="big-pickle",
            timeout_seconds=60,
        )

    def test_last_user_text_returns_last_user_content(self):
        msgs = [
            {"role": "system", "content": "be helpful"},
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "ok"},
            {"role": "user", "content": "second"},
        ]
        assert OpenCodeProvider._last_user_text(msgs) == "second"

    def test_last_user_text_no_user_message(self):
        msgs = [{"role": "assistant", "content": "hi"}]
        assert OpenCodeProvider._last_user_text(msgs) == "hi"

    def test_last_user_text_empty_list(self):
        assert OpenCodeProvider._last_user_text([]) == ""

    def test_parse_response_standard(self):
        result = OpenCodeProvider._parse_response(MESSAGE_RESPONSE)
        assert result["role"] == "assistant"
        assert result["content"] == MESSAGE_TEXT
        assert result["finish_reason"] == "stop"
        assert result["tool_calls"] == []

    def test_parse_response_no_text_part(self):
        data = {"info": {"finish": "stop"}, "parts": [{"type": "step-start"}]}
        result = OpenCodeProvider._parse_response(data)
        assert result["content"] == ""

    def test_parse_response_missing_parts_returns_empty(self):
        result = OpenCodeProvider._parse_response({})
        assert result["content"] == ""

    def test_parse_response_none_data_raises(self):
        with pytest.raises(OpenCodeProviderError) as exc:
            OpenCodeProvider._parse_response(None)  # type: ignore
        assert exc.value.exit_code == 1

    @patch("urllib.request.urlopen")
    def test_complete_success(self, mock_urlopen):
        mock_urlopen.side_effect = [
            _mock_cm(SESSION_RESPONSE),
            _mock_cm(MESSAGE_RESPONSE),
        ]
        with patch.object(self.provider, "_ensure_server"):
            result = self.provider.complete(
                [{"role": "user", "content": "Say READY"}],
            )
        assert result["content"] == MESSAGE_TEXT
        assert result["finish_reason"] == "stop"

    @patch("urllib.request.urlopen")
    def test_session_creation_fails_server_unavailable(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        with patch.object(self.provider, "_ensure_server"):
            with pytest.raises(OpenCodeProviderError) as exc:
                self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 2
        assert exc.value.status == "BLOCKED"
        assert BLOCKED_SERVER in str(exc.value)

    @patch("urllib.request.urlopen")
    def test_session_creation_http_error_401(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=401, msg="Unauthorized",
            hdrs={}, fp=MagicMock(),
        )
        with patch.object(self.provider, "_ensure_server"):
            with pytest.raises(OpenCodeProviderError) as exc:
                self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 2
        assert exc.value.status == "BLOCKED"

    @patch("urllib.request.urlopen")
    def test_session_creation_http_error_403(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=403, msg="Forbidden",
            hdrs={}, fp=MagicMock(),
        )
        with patch.object(self.provider, "_ensure_server"):
            with pytest.raises(OpenCodeProviderError) as exc:
                self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 2
        assert exc.value.status == "BLOCKED"

    @patch("urllib.request.urlopen")
    def test_message_post_http_error_404(self, mock_urlopen):
        mock_urlopen.side_effect = [
            _mock_cm(SESSION_RESPONSE),
            urllib.error.HTTPError(url="", code=404, msg="Not Found", hdrs={}, fp=MagicMock()),
        ]
        with patch.object(self.provider, "_ensure_server"):
            with pytest.raises(OpenCodeProviderError) as exc:
                self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 4

    @patch("urllib.request.urlopen")
    def test_message_post_http_error_429(self, mock_urlopen):
        mock_urlopen.side_effect = [
            _mock_cm(SESSION_RESPONSE),
            urllib.error.HTTPError(url="", code=429, msg="Too Many Requests", hdrs={}, fp=MagicMock()),
        ]
        with patch.object(self.provider, "_ensure_server"):
            with pytest.raises(OpenCodeProviderError) as exc:
                self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 4

    @patch("urllib.request.urlopen")
    def test_message_post_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = [
            _mock_cm(SESSION_RESPONSE),
            urllib.error.URLError("timed out"),
        ]
        with patch.object(self.provider, "_ensure_server"):
            with pytest.raises(OpenCodeProviderError) as exc:
                self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 4
        assert "timeout" in str(exc.value).lower()

    def test_payload_model_from_opencode_model_id(self):
        from agentx_evolve.providers.provider_router import ProviderRouter
        assert ProviderRouter._payload_model("opencode/big-pickle") == "big-pickle"
        assert ProviderRouter._payload_model("custom/model") == "custom/model"

    def test_redacted_api_key_in_config(self):
        from agentx_evolve.runtime.config import RuntimeConfig
        config = RuntimeConfig(
            provider="opencode", opencode_api_key="sk-real-key",
        )
        d = config.redacted_dict()
        assert d["opencode_api_key"] == "***REDACTED***"


class TestProviderRouter:
    def test_router_selects_mock(self):
        from agentx_evolve.runtime.config import RuntimeConfig
        from agentx_evolve.providers.provider_router import ProviderRouter
        from agentx_evolve.providers.mock_provider import MockProvider

        config = RuntimeConfig(provider="mock")
        router = ProviderRouter(config)
        provider = router.get_provider()
        assert isinstance(provider, MockProvider)

    def test_router_selects_opencode(self):
        from agentx_evolve.runtime.config import RuntimeConfig
        from agentx_evolve.providers.provider_router import ProviderRouter
        from agentx_evolve.providers.opencode_provider import OpenCodeProvider

        config = RuntimeConfig(
            provider="opencode", opencode_api_key="sk-test",
        )
        router = ProviderRouter(config)
        provider = router.get_provider()
        assert isinstance(provider, OpenCodeProvider)

    def test_router_unknown_provider_raises(self):
        from agentx_evolve.runtime.config import RuntimeConfig
        from agentx_evolve.providers.provider_router import ProviderRouter
        from agentx_evolve.providers.opencode_provider import OpenCodeProviderError

        config = RuntimeConfig(provider="unknown")
        router = ProviderRouter(config)
        with pytest.raises(OpenCodeProviderError) as exc:
            router.get_provider()
        assert exc.value.exit_code == 2
        assert exc.value.status == "BLOCKED"
