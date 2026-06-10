from __future__ import annotations

import json
import logging
import re
import subprocess
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

BLOCKED_SERVER = "opencode server unavailable"
FAIL_SERVER_START = "failed to start opencode server"
FAIL_MALFORMED = "malformed response"


class LLMProviderError(Exception):
    def __init__(self, message: str, exit_code: int, status: str = "FAIL"):
        self.message = message
        self.exit_code = exit_code
        self.status = status
        super().__init__(message)


class LLMProvider:
    """OpenCode API caller — mirrors agent_x's OpenCodeProvider exactly.

    Auto-starts the opencode server if not already running. Never falls
    back — raises on failure.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:14096",
        model: str = "big-pickle",
        timeout_seconds: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._session_id: str | None = None
        self._server_proc: subprocess.Popen[str] | None = None

    @property
    def _timeout(self) -> float | None:
        return None if self.timeout_seconds == 0 else float(self.timeout_seconds)

    # ── public API ──────────────────────────────────────────────────────

    def complete(
        self,
        system_prompt: str,
        user_text: str,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        self._ensure_server()
        self._ensure_session()

        body: dict[str, Any] = {
            "model": {"providerID": "opencode", "modelID": self.model},
            "parts": [{"type": "text", "text": user_text}],
        }
        if system_prompt:
            body["system"] = system_prompt

        data = self._post_message(body)
        return self._parse_response(data)

    # ── server lifecycle (mirrors OpenCodeProvider._ensure_server) ─────

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
            raise LLMProviderError(
                "opencode binary not found — install it from https://opencode.ai",
                exit_code=2,
                status="BLOCKED",
            )
        for _ in range(60):
            if self._health_check():
                return
            import time

            time.sleep(1)
        _, err = self._server_proc.communicate(timeout=5)
        self._server_proc = None
        raise LLMProviderError(
            f"{FAIL_SERVER_START}: {err.strip() or 'timed out waiting for server'}",
            exit_code=2,
            status="BLOCKED",
        )

    # ── session lifecycle ──────────────────────────────────────────────

    def _ensure_session(self) -> None:
        if self._session_id is not None:
            return
        body = json.dumps({}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/session",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
        except urllib.error.URLError as e:
            raise LLMProviderError(
                f"{BLOCKED_SERVER}: {e.reason if hasattr(e, 'reason') else e}",
                exit_code=2,
                status="BLOCKED",
            )
        sid = data.get("id")
        if not sid:
            raise LLMProviderError(
                f"{FAIL_MALFORMED}: no session id in {data}", exit_code=1
            )
        self._session_id = sid

    # ── message sending (mirrors OpenCodeProvider._post_message) ───────

    def _post_message(self, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/session/{self._session_id}/message"
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            self._classify_http_error(e)
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower():
                raise LLMProviderError("provider timeout", exit_code=4)
            raise LLMProviderError(f"provider unavailable: {e}", exit_code=4)

    @staticmethod
    def _classify_http_error(e: urllib.error.HTTPError) -> None:
        code = e.code
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        if code == 401 or code == 403:
            raise LLMProviderError(
                "authentication failed (401/403)", exit_code=2, status="BLOCKED"
            )
        if code == 404:
            raise LLMProviderError("model/endpoint not found (404)", exit_code=4)
        if code == 429:
            raise LLMProviderError("rate limited (429)", exit_code=4)
        if code >= 500:
            raise LLMProviderError("server error (5xx)", exit_code=4)
        detail = f": {body[:500]}" if body else ""
        raise LLMProviderError(f"HTTP {code}: {e.reason}{detail}", exit_code=4)

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
            raise LLMProviderError(f"{FAIL_MALFORMED}: {e}", exit_code=1)
