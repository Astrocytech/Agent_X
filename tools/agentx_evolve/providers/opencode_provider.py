from __future__ import annotations
import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Generator

from agentx_evolve.runtime.logging_manager import ConversationLogger

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
        session_id: str = "",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._session_id: str | None = session_id or None
        self._provider_id: str = "opencode"
        self._server_proc: subprocess.Popen[str] | None = None
        self._conversation_logger = ConversationLogger()

    @property
    def session_id(self) -> str | None:
        return self._session_id

    def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        self._conversation_logger.log_request(
            provider=self._provider_id, model=self.model,
            messages=messages, kwargs=kwargs,
        )
        start = time.perf_counter()
        try:
            self._ensure_session()
            last_text = self._last_user_text(messages)
            parts = [{"type": "text", "text": last_text}]
            body = {
                "model": {"providerID": self._provider_id, "modelID": self.model},
                "parts": parts,
            }
            data = self._post_message(body)
            response = self._parse_response(data)
            elapsed = (time.perf_counter() - start) * 1000
            self._conversation_logger.log_response(
                provider=self._provider_id, model=self.model,
                response=response, duration_ms=elapsed,
            )
            return response
        except OpenCodeProviderError:
            elapsed = (time.perf_counter() - start) * 1000
            self._conversation_logger.log_error(
                provider=self._provider_id, model=self.model,
                error="OpenCodeProviderError", duration_ms=elapsed,
            )
            raise

    def complete_structured(
        self, messages: list[dict[str, Any]], **kwargs: Any,
    ) -> dict[str, Any]:
        self._conversation_logger.log_request(
            provider=self._provider_id, model=self.model,
            messages=messages, kwargs=kwargs,
        )
        start = time.perf_counter()
        try:
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
                    parsed = json.loads(json_str)
                    elapsed = (time.perf_counter() - start) * 1000
                    self._conversation_logger.log_response(
                        provider=self._provider_id, model=self.model,
                        response=parsed, duration_ms=elapsed,
                    )
                    return parsed
                except json.JSONDecodeError:
                    pass
            elapsed = (time.perf_counter() - start) * 1000
            self._conversation_logger.log_error(
                provider=self._provider_id, model=self.model,
                error="LLM did not return valid JSON", duration_ms=elapsed,
            )
            raise OpenCodeProviderError(
                f"LLM did not return a valid structured plan JSON:\n{content[:500]}",
                exit_code=1,
            )
        except OpenCodeProviderError:
            elapsed = (time.perf_counter() - start) * 1000
            self._conversation_logger.log_error(
                provider=self._provider_id, model=self.model,
                error="OpenCodeProviderError", duration_ms=elapsed,
            )
            raise

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

    def complete_streaming(
        self, messages: list[dict[str, Any]], **kwargs: Any,
    ) -> Generator[dict[str, Any], None, dict[str, Any]]:
        self._conversation_logger.log_request(
            provider=self._provider_id, model=self.model,
            messages=messages, kwargs=kwargs,
        )
        start = time.perf_counter()
        try:
            self._ensure_session()
            last_text = self._last_user_text(messages)
            parts = [{"type": "text", "text": last_text}]
            body = {
                "model": {"providerID": self._provider_id, "modelID": self.model},
                "parts": parts,
            }
            payload = json.dumps(body).encode("utf-8")
            msg_url = f"{self.base_url}/session/{self._session_id}/message"
            event_url = f"{self.base_url}/event"

            response_data: list[dict | None] = [None]
            error_data: list[Exception | None] = [None]

            def send() -> None:
                try:
                    req = urllib.request.Request(
                        msg_url, data=payload,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                        response_data[0] = json.loads(resp.read().decode("utf-8"))
                except Exception as e:
                    error_data[0] = e

            send_thread = threading.Thread(target=send, daemon=True)
            event_req = urllib.request.Request(event_url)
            event_resp = urllib.request.urlopen(event_req, timeout=self.timeout_seconds)
            send_thread.start()

            _is_user_turn = False

            for evt in _sse_events(event_resp):
                evt_type = evt.get("type", "")
                props = evt.get("properties", {})

                if evt_type == "session.next.agent.switched":
                    _is_user_turn = True
                    yield {"type": "agent", "agent": props.get("agent", "")}

                elif evt_type == "message.part.updated":
                    part = props.get("part", {})
                    ptype = part.get("type", "")
                    if ptype == "reasoning":
                        text = part.get("text", "")
                        if text:
                            yield {"type": "reasoning", "text": text.strip(), "author": "assistant"}
                    elif ptype == "text":
                        text = part.get("text", "")
                        if text:
                            if _is_user_turn:
                                yield {"type": "text", "text": text.strip(), "author": "user"}
                                _is_user_turn = False
                            else:
                                yield {"type": "text", "text": text.strip(), "author": "assistant"}
                    elif ptype == "tool":
                        tool_name = part.get("tool", "")
                        state = part.get("state", {})
                        status = state.get("status", "")
                        inp = state.get("input", {})
                        outp = state.get("output", "")
                        err = state.get("error", "")
                        if status == "running":
                            yield {"type": "tool", "name": tool_name, "status": "running", "input": inp, "author": "assistant"}
                        elif status == "completed":
                            yield {"type": "tool", "name": tool_name, "status": "completed", "output": outp, "author": "assistant"}
                        elif status == "error":
                            yield {"type": "tool", "name": tool_name, "status": "error", "error": str(err)[:300], "author": "assistant"}

                if response_data[0] is not None or error_data[0] is not None:
                    break

            send_thread.join(timeout=10)

            if error_data[0]:
                raise error_data[0]

            data = response_data[0]
            if data is None:
                raise OpenCodeProviderError("no response from server", exit_code=4)

            response = self._parse_response(data)
            elapsed = (time.perf_counter() - start) * 1000
            self._conversation_logger.log_response(
                provider=self._provider_id, model=self.model,
                response=response, duration_ms=elapsed,
            )
            return response

        except OpenCodeProviderError:
            elapsed = (time.perf_counter() - start) * 1000
            self._conversation_logger.log_error(
                provider=self._provider_id, model=self.model,
                error="OpenCodeProviderError", duration_ms=elapsed,
            )
            raise

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


def _sse_events(resp: urllib.request.AddInfoHandler) -> Generator[dict[str, Any], None, None]:
    """Yield parsed SSE events from an HTTP response (bytes-safe)."""
    buf = b""
    for chunk in iter(lambda: resp.read(1), b""):
        buf += chunk
        while b"\n\n" in buf:
            line, buf = buf.split(b"\n\n", 1)
            for l in line.split(b"\n"):
                if l.startswith(b"data: "):
                    try:
                        yield json.loads(l[6:].decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
