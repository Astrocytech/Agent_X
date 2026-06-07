import json
import urllib.error
from unittest.mock import patch, MagicMock

import pytest

from agentx_evolve.providers.opencode_provider import (
    OpenCodeProvider, OpenCodeProviderError,
    BLOCKED_MISSING_KEY, BLOCKED_AUTH,
    FAIL_MODEL, FAIL_RATE_LIMIT, FAIL_SERVER, FAIL_TIMEOUT, FAIL_MALFORMED,
)


class TestOpenCodeProvider:
    def setup_method(self):
        self.provider = OpenCodeProvider(
            api_key="sk-test-key",
            base_url="https://opencode.ai/zen/v1",
            model="big-pickle",
        )

    def test_chat_url_no_double_v1(self):
        url = self.provider._chat_url
        assert url == "https://opencode.ai/zen/v1/chat/completions"
        assert url.count("/v1") == 1

    def test_chat_url_without_v1_suffix(self):
        p = OpenCodeProvider(api_key="k", base_url="https://example.com/api/v2")
        url = p._chat_url
        assert url == "https://example.com/api/v2/v1/chat/completions"

    def test_missing_key_raises_blocked(self):
        p = OpenCodeProvider(api_key="")
        with pytest.raises(OpenCodeProviderError) as exc:
            p._check_key()
        assert exc.value.exit_code == 2
        assert exc.value.status == "BLOCKED"
        assert BLOCKED_MISSING_KEY in str(exc.value)

    def test_build_payload(self):
        messages = [
            {"role": "system", "content": "you are helpful"},
            {"role": "user", "content": "Say READY"},
        ]
        payload = self.provider._build_payload(messages)
        assert payload["model"] == "big-pickle"
        assert payload["messages"] == messages
        assert payload["temperature"] == 0.2
        assert payload["stream"] is False

    def test_payload_model_from_opencode_model_id(self):
        from agentx_evolve.providers.provider_router import ProviderRouter
        assert ProviderRouter._payload_model("opencode/big-pickle") == "big-pickle"
        assert ProviderRouter._payload_model("custom/model") == "custom/model"

    def test_parse_response_standard(self):
        data = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello"},
                    "finish_reason": "stop",
                }
            ]
        }
        result = self.provider._parse_response(data)
        assert result["role"] == "assistant"
        assert result["content"] == "Hello"
        assert result["finish_reason"] == "stop"

    def test_parse_response_empty_choices_raises(self):
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider._parse_response({"choices": []})
        assert exc.value.exit_code == 1

    def test_parse_response_missing_choices_raises(self):
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider._parse_response({})
        assert exc.value.exit_code == 1

    @patch("urllib.request.urlopen")
    def test_complete_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [
                {
                    "message": {"role": "assistant", "content": "READY"},
                    "finish_reason": "stop",
                }
            ]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.provider.complete(
            [{"role": "user", "content": "Say READY"}],
        )
        assert result["content"] == "READY"
        assert result["finish_reason"] == "stop"

    @patch("urllib.request.urlopen")
    def test_complete_server_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=500, msg="Internal Server Error",
            hdrs={}, fp=MagicMock(),
        )
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 4
        assert FAIL_SERVER in str(exc.value)

    @patch("urllib.request.urlopen")
    def test_complete_401_raises_blocked(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=401, msg="Unauthorized",
            hdrs={}, fp=MagicMock(),
        )
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 2
        assert exc.value.status == "BLOCKED"

    @patch("urllib.request.urlopen")
    def test_complete_403_raises_blocked(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=403, msg="Forbidden",
            hdrs={}, fp=MagicMock(),
        )
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 2
        assert exc.value.status == "BLOCKED"

    @patch("urllib.request.urlopen")
    def test_complete_404_raises_fail(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=404, msg="Not Found",
            hdrs={}, fp=MagicMock(),
        )
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 4

    @patch("urllib.request.urlopen")
    def test_complete_429_raises_fail(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=429, msg="Too Many Requests",
            hdrs={}, fp=MagicMock(),
        )
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 4

    @patch("urllib.request.urlopen")
    def test_complete_timeout(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("timed out")
        with pytest.raises(OpenCodeProviderError) as exc:
            self.provider.complete([{"role": "user", "content": "hi"}])
        assert exc.value.exit_code == 4

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
