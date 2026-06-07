from __future__ import annotations
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from typing import Any

BLOCKED_AUTH = "authentication failed (401/403)"
BLOCKED_SERVER = "opencode server unavailable"
FAIL_MODEL = "model/endpoint not found (404)"
FAIL_RATE_LIMIT = "rate limited (429)"
FAIL_SERVER = "server error (5xx)"
FAIL_TIMEOUT = "provider timeout"
FAIL_MALFORMED = "malformed response"
FAIL_SERVER_START = "failed to start opencode server"


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
        base_url: str = "http://127.0.0.1:14096",
        api_key: str = "",
        model: str = "big-pickle",
        timeout_seconds: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._session_id: str | None = None
        self._provider_id: str = "opencode"
        self._server_proc: subprocess.Popen[str] | None = None

    def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        self._ensure_session()
        last_text = self._last_user_text(messages)
        parts = [{"type": "text", "text": last_text}]
        body = {
            "model": {"providerID": self._provider_id, "modelID": self.model},
            "parts": parts,
        }
        data = self._post_message(body)
        return self._parse_response(data)

    def complete_structured(
        self, messages: list[dict[str, Any]], **kwargs: Any,
    ) -> dict[str, Any]:
        self._session_id = None
        self._ensure_session()
        system_text = ""
        user_text = ""
        for m in messages:
            if m.get("role") == "system":
                system_text = m.get("content", "")
            elif m.get("role") == "user":
                user_text = m.get("content", "")
        fmt_instructions = (
            "\n\nYou MUST respond with ONLY a valid JSON object using this exact schema:\n"
            '{"schema_version":"agentx.structured_plan.v1",'
            '"summary":"<short description>",'
            '"actions":[{"type":"patch|validate|report|noop","description":"<what>","target":"<relative file path>","safety_notes":["<note>"]}],'
            '"patches":[{"format":"unified_diff","content":"<unified diff with ---/+++ markers>"}],'
            '"validation_commands":["<command>"]}\n'
            "Do NOT include markdown code fences, explanations, or any text outside the JSON."
        )
        if system_text:
            system_text += fmt_instructions
        body: dict[str, Any] = {
            "model": {"providerID": self._provider_id, "modelID": self.model},
            "parts": [{"type": "text", "text": user_text or "."}],
        }
        if system_text:
            body["system"] = system_text
        data = self._post_message(body)
        response = self._parse_response(data)
        content = response.get("content", "").strip()
        json_str = content
        idx = json_str.find("{")
        if idx != -1:
            json_str = json_str[idx:]
        end = json_str.rfind("}")
        if end != -1:
            json_str = json_str[:end + 1]
        if json_str.startswith("```"):
            json_str = json_str[json_str.find("\n") + 1:json_str.rfind("```")].strip()
        if json_str.startswith("{"):
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        raise OpenCodeProviderError(
            f"LLM did not return a valid structured plan JSON:\n{content[:500]}",
            exit_code=1,
        )

    @staticmethod
    def _last_user_text(messages: list[dict[str, Any]]) -> str:
        for m in reversed(messages):
            if m.get("role") == "user":
                return m.get("content", "")
        return messages[-1].get("content", "") if messages else ""

    def _health_check(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/global/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _ensure_server(self) -> None:
        if self._health_check():
            return
        port_match = re.search(r":(\d+)$", self.base_url)
        port = port_match.group(1) if port_match else "14096"
        try:
            self._server_proc = subprocess.Popen(
                ["opencode", "serve", "--port", port],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            raise OpenCodeProviderError(
                "opencode binary not found — install it from https://opencode.ai",
                exit_code=2, status="BLOCKED",
            )
        for _ in range(30):
            if self._health_check():
                return
            import time
            time.sleep(1)
        _, err = self._server_proc.communicate(timeout=5)
        self._server_proc = None
        raise OpenCodeProviderError(
            f"{FAIL_SERVER_START}: {err.strip() or 'timed out waiting for server'}",
            exit_code=2, status="BLOCKED",
        )

    def _ensure_session(self) -> None:
        if self._session_id is not None:
            return
        self._ensure_server()
        url = f"{self.base_url}/session"
        body = json.dumps({}).encode("utf-8")
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
        except urllib.error.HTTPError as e:
            self._classify_http_error(e)
        except urllib.error.URLError as e:
            raise OpenCodeProviderError(
                f"{BLOCKED_SERVER}: {e.reason if hasattr(e, 'reason') else e}",
                exit_code=2, status="BLOCKED",
            )
        sid = data.get("id")
        if not sid:
            raise OpenCodeProviderError(
                f"{FAIL_MALFORMED}: no session id in {data}",
                exit_code=1,
            )
        self._session_id = sid

    def _post_message(self, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/session/{self._session_id}/message"
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
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
            parts = data.get("parts", [])
            text = ""
            for p in parts:
                if p.get("type") == "text":
                    text = p.get("text", "")
                    break
            info = data.get("info", {})
            finish = info.get("finish", "stop")
            return {
                "role": "assistant",
                "content": text,
                "tool_calls": [],
                "finish_reason": finish,
            }
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            raise OpenCodeProviderError(
                f"{FAIL_MALFORMED}: {e}", exit_code=1,
            )
