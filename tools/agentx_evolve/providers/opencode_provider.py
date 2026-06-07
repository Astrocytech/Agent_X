from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Any

BLOCKED_MISSING_KEY = "missing API key"
BLOCKED_AUTH = "authentication failed (401/403)"
FAIL_MODEL = "model/endpoint not found (404)"
FAIL_RATE_LIMIT = "rate limited (429)"
FAIL_SERVER = "server error (5xx)"
FAIL_TIMEOUT = "provider timeout"
FAIL_MALFORMED = "malformed response"


class OpenCodeProviderError(Exception):
    def __init__(self, message: str, exit_code: int, status: str = "FAIL"):
        self.message = message
        self.exit_code = exit_code
        self.status = status
        super().__init__(message)


class OpenCodeProvider:
    def __init__(
        self,
        *,
        base_url: str = "https://opencode.ai/zen/v1",
        api_key: str = "",
        model: str = "big-pickle",
        timeout_seconds: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    @property
    def _chat_url(self) -> str:
        base = self.base_url
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        self._check_key()
        payload = self._build_payload(messages)
        data = self._post(payload)
        return self._parse_response(data)

    def _check_key(self) -> None:
        if not self.api_key:
            raise OpenCodeProviderError(
                BLOCKED_MISSING_KEY, exit_code=2, status="BLOCKED",
            )

    def _build_payload(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": False,
        }

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self._chat_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            self._classify_http_error(e)
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower():
                raise OpenCodeProviderError(FAIL_TIMEOUT, exit_code=4)
            raise OpenCodeProviderError(f"provider unavailable: {e}", exit_code=4)

    @staticmethod
    def _classify_http_error(e: urllib.error.HTTPError) -> None:
        code = e.code
        if code == 401 or code == 403:
            raise OpenCodeProviderError(BLOCKED_AUTH, exit_code=2, status="BLOCKED")
        if code == 404:
            raise OpenCodeProviderError(FAIL_MODEL, exit_code=4)
        if code == 429:
            raise OpenCodeProviderError(FAIL_RATE_LIMIT, exit_code=4)
        if code >= 500:
            raise OpenCodeProviderError(FAIL_SERVER, exit_code=4)
        raise OpenCodeProviderError(f"HTTP {code}: {e.reason}", exit_code=4)

    @staticmethod
    def _parse_response(data: dict[str, Any]) -> dict[str, Any]:
        try:
            choices = data.get("choices", [])
            if not choices:
                raise ValueError("no choices in response")
            choice = choices[0]
            msg = choice.get("message", {})
            return {
                "role": msg.get("role", "assistant"),
                "content": msg.get("content", ""),
                "tool_calls": msg.get("tool_calls", []),
                "finish_reason": choice.get("finish_reason", "stop"),
            }
        except (KeyError, ValueError, TypeError) as e:
            raise OpenCodeProviderError(
                f"{FAIL_MALFORMED}: {e}", exit_code=1,
            )
