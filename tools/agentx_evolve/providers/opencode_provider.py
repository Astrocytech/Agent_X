from __future__ import annotations
import json
import os
import re
import socket
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
FAIL_USAGE_LIMIT = "free usage limit reached"
FAIL_SERVER = "server error (5xx)"
FAIL_TIMEOUT = "provider timeout"
FAIL_MALFORMED = "malformed response"
FAIL_SERVER_START = "failed to start opencode server"


def _looks_like_usage_limit(text: str) -> bool:
    lower = (text or "").lower()
    patterns = (
        "free limit reached",
        "free usage exceeded",
        "freeusagelimiterror",
        "usage limit",
        "insufficient_quota",
        "rate limit",
        "rate limited",
        "quota",
        "exceeded your current quota",
        "opencode go",
        "go_upsell",
        "too many requests",
    )
    return any(pattern in lower for pattern in patterns)


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
        timeout_seconds: int = 0,
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
        self._subagent_sessions: dict[str, list[str]] = {}
        self._agent_mode: str = "general"
        self._fic_document: str = ""
        self._event_resp: Any = None
        self._prev_cancel_event: threading.Event | None = None
        self._subagent_event_meta: dict[str, dict[str, str]] = {}

    def cancel_streaming(self) -> None:
        """Close the active SSE connection and signal cancellation.

        This causes any in-flight *complete_streaming* generator to break
        out of its event loop promptly instead of waiting for a socket
        timeout.
        """
        if self._prev_cancel_event is not None:
            self._prev_cancel_event.set()
        if self._event_resp is not None:
            try:
                self._event_resp.close()
            except Exception:
                pass
            self._event_resp = None

    def abandon_session(self) -> None:
        """Drop the current provider session without making a network call."""
        self.cancel_streaming()
        self._session_id = None

    def reset_session(self) -> str:
        """Create a new session, discarding the old one."""
        old = self._session_id
        self._session_id = None
        self._agent_mode = "general"
        self._fic_document = ""
        self._ensure_session()
        return self._session_id or ""

    @property
    def _timeout(self) -> float | None:
        return None if self.timeout_seconds == 0 else float(self.timeout_seconds)

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def agent_mode(self) -> str:
        return self._agent_mode

    @property
    def fic_document(self) -> str:
        return self._fic_document

    def set_agent_mode(self, mode: str, fic_document: str = "") -> None:
        self._agent_mode = mode if mode in ("general", "governed") else "general"
        self._fic_document = fic_document if mode == "governed" else ""

    def reset_agent_mode(self) -> None:
        self._agent_mode = "general"
        self._fic_document = ""

    def get_governance_info(self) -> dict[str, Any]:
        if self._agent_mode == "governed":
            return {
                "agent_mode": "governed",
                "fic_document": self._fic_document,
                "ceiling": "P7_PUBLIC_API_CHANGE",
                "allowed_tools": [
                    "read", "write", "edit", "glob", "grep",
                    "bash", "websearch", "webfetch", "question",
                    "seed.emit_answer",
                ],
                "forbidden_tools": [
                    "shell.run", "filesystem.write", "network.request",
                    "evolution.promote", "runtime.mutate",
                ],
                "phase_0_active": True,
            }
        return {
            "agent_mode": "general",
            "fic_document": "",
            "ceiling": "P9_EXTERNAL_SIDE_EFFECT",
            "allowed_tools": [],
            "forbidden_tools": [
                "shell.run", "filesystem.write", "network.request",
                "evolution.promote", "runtime.mutate",
            ],
            "phase_0_active": False,
        }

    def get_models(self) -> list[dict[str, Any]]:
        try:
            req = urllib.request.Request(f"{self.base_url}/config/providers", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                providers = data.get("providers", [])
                models = []
                for prov in providers:
                    pid = prov.get("id", "")
                    for mid, minfo in (prov.get("models") or {}).items():
                        models.append({
                            "id": mid,
                            "name": minfo.get("name", mid) if isinstance(minfo, dict) else mid,
                            "provider": pid,
                        })
                return models
        except Exception:
            return [{"id": self.model, "name": f"{self.model} (current)", "provider": self._provider_id}]

    def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        self._conversation_logger.log_request(
            provider=self._provider_id, model=self.model,
            messages=messages, kwargs=kwargs,
        )
        start = time.perf_counter()
        try:
            self._ensure_session()
            system_text = ""
            user_text = ""
            for m in messages:
                if m.get("role") == "system":
                    system_text = m.get("content", "")
                elif m.get("role") == "user":
                    user_text = m.get("content", "")
            body: dict[str, Any] = {
                "model": {"providerID": self._provider_id, "modelID": self.model},
                "parts": [{"type": "text", "text": user_text or "."}],
            }
            if system_text:
                body["system"] = system_text
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
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
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
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
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
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        if _looks_like_usage_limit(body):
            raise OpenCodeProviderError(FAIL_USAGE_LIMIT, exit_code=4, status="BLOCKED")
        if code == 401 or code == 403:
            raise OpenCodeProviderError(BLOCKED_AUTH, exit_code=2, status="BLOCKED")
        if code == 404:
            raise OpenCodeProviderError(FAIL_MODEL, exit_code=4)
        if code == 429:
            raise OpenCodeProviderError(FAIL_RATE_LIMIT, exit_code=4)
        if code >= 500:
            raise OpenCodeProviderError(FAIL_SERVER, exit_code=4)
        detail = f": {body[:500]}" if body else ""
        raise OpenCodeProviderError(f"HTTP {code}: {e.reason}{detail}", exit_code=4)

    def complete_streaming(
        self, messages: list[dict[str, Any]], cancel_event: threading.Event | None = None, **kwargs: Any,
    ) -> Generator[dict[str, Any], None, dict[str, Any]]:
        self._conversation_logger.log_request(
            provider=self._provider_id, model=self.model,
            messages=messages, kwargs=kwargs,
        )
        start = time.perf_counter()
        event_resp = None
        try:
            self._ensure_session()
            system_text = ""
            user_text = ""
            for m in messages:
                if m.get("role") == "system":
                    system_text = m.get("content", "")
                elif m.get("role") == "user":
                    user_text = m.get("content", "")
            body: dict[str, Any] = {
                "model": {"providerID": self._provider_id, "modelID": self.model},
                "parts": [{"type": "text", "text": user_text or "."}],
            }
            if system_text:
                body["system"] = system_text
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
                    with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                        response_data[0] = json.loads(resp.read().decode("utf-8"))
                except urllib.error.HTTPError as e:
                    try:
                        self._classify_http_error(e)
                    except Exception as classified:
                        error_data[0] = classified
                except Exception as e:
                    error_data[0] = e

            send_thread = threading.Thread(target=send, daemon=True)
            event_req = urllib.request.Request(event_url)
            if self._prev_cancel_event is not None:
                self._prev_cancel_event.set()
            self._prev_cancel_event = cancel_event
            event_resp = urllib.request.urlopen(event_req, timeout=self._timeout)
            self._event_resp = event_resp
            send_thread.start()

            _is_user_turn = True

            for evt in _sse_events(event_resp, cancel_event=cancel_event):
                evt_type = evt.get("type", "")
                props = evt.get("properties", {})

                if evt_type == "session.next.agent.switched":
                    _is_user_turn = True
                    yield {"type": "agent", "agent": props.get("agent", "")}

                elif evt_type in ("permission.asked", "permission.v2.asked"):
                    yield {
                        "type": "permission",
                        "request_id": evt.get("id", ""),
                        "action": props.get("action", ""),
                        "resources": props.get("resources", []),
                        "metadata": props.get("metadata", {}),
                        "save": props.get("save", []),
                    }

                elif evt_type in ("permission.replied", "permission.v2.replied"):
                    yield {
                        "type": "permission_cleared",
                        "request_id": props.get("requestID", props.get("request_id", "")),
                    }

                elif evt_type in ("question.v2.asked", "question.asked"):
                    yield {
                        "type": "question",
                        "request_id": evt.get("id", ""),
                        "questions": props.get("questions", []),
                    }

                elif evt_type in ("question.v2.replied", "question.replied"):
                    yield {
                        "type": "question_cleared",
                        "request_id": props.get("requestID", props.get("request_id", "")),
                    }

                elif evt_type == "todo.updated":
                    yield {
                        "type": "todo",
                        "todos": props.get("todos", []),
                    }

                elif evt_type == "session.status":
                    status = props.get("status", {})
                    if isinstance(status, dict):
                        message = str(status.get("message", ""))
                        if _looks_like_usage_limit(message):
                            yield {
                                "type": "usage_limit",
                                "text": FAIL_USAGE_LIMIT,
                                "detail": message,
                                "author": "system",
                            }

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
                        if tool_name == "task":
                            subagent_id = ""
                            sub_match = re.search(r'<task\s+id="([^"]+)"', outp if outp else "")
                            if sub_match:
                                subagent_id = sub_match.group(1)
                            fallback_key = ""
                            if isinstance(inp, dict):
                                fallback_key = f"{inp.get('subagent_type', 'subagent')}|{inp.get('description', '')}"
                            meta_key = subagent_id or fallback_key
                            if status == "running":
                                subagent_name = inp.get("subagent_type", "subagent") if isinstance(inp, dict) else "subagent"
                                subagent_desc = inp.get("description", "") if isinstance(inp, dict) else ""
                                if meta_key:
                                    self._subagent_event_meta[meta_key] = {
                                        "name": subagent_name,
                                        "description": subagent_desc,
                                    }
                                yield {
                                    "type": "subagent",
                                    "status": "running",
                                    "session_id": subagent_id or "",
                                    "parent_session_id": self._session_id or "",
                                    "name": subagent_name,
                                    "description": subagent_desc,
                                    "author": "assistant",
                                }
                            elif status == "completed":
                                meta = self._subagent_event_meta.get(meta_key, {})
                                if subagent_id:
                                    self._subagent_sessions.setdefault(self._session_id or "", [])
                                    if subagent_id not in self._subagent_sessions.get(self._session_id or "", []):
                                        self._subagent_sessions[self._session_id or ""].append(subagent_id)
                                yield {
                                    "type": "subagent",
                                    "status": "completed",
                                    "session_id": subagent_id,
                                    "parent_session_id": self._session_id or "",
                                    "name": meta.get("name", "subagent"),
                                    "description": meta.get("description", ""),
                                    "output": outp,
                                    "author": "assistant",
                                }
                            elif status == "error":
                                meta = self._subagent_event_meta.get(meta_key, {})
                                yield {
                                    "type": "subagent",
                                    "status": "error",
                                    "session_id": subagent_id,
                                    "parent_session_id": self._session_id or "",
                                    "name": meta.get("name", "subagent"),
                                    "description": meta.get("description", ""),
                                    "error": str(err)[:300],
                                    "author": "assistant",
                                }
                        else:
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
                if cancel_event is not None and cancel_event.is_set():
                    return {"role": "assistant", "content": "", "tool_calls": [], "finish_reason": "cancelled"}
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
        finally:
            if event_resp is not None:
                if self._event_resp is event_resp:
                    self._event_resp = None
                try:
                    event_resp.close()
                except Exception:
                    pass

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

    def get_subagent_sessions(self, parent_session_id: str) -> list[str]:
        """Return subagent session IDs for a given parent session."""
        return self._subagent_sessions.get(parent_session_id, [])

    def get_session_messages(self, session_id: str) -> list[dict[str, Any]]:
        """Fetch session messages from opencode API."""
        self._ensure_server()
        url = f"{self.base_url}/session/{session_id}/message"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                msgs = []
                for item in data if isinstance(data, list) else [data]:
                    info = item.get("info", {})
                    role = info.get("role", "assistant")
                    parts = item.get("parts", [])
                    text = ""
                    for p in parts:
                        if p.get("type") == "text":
                            pt = p.get("text", "")
                            if pt:
                                text += pt
                    if text:
                        msgs.append({"role": role, "text": text})
                return msgs
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            self._classify_http_error(e)
        except urllib.error.URLError as e:
            raise OpenCodeProviderError(f"provider unavailable: {e}", exit_code=4)


    def get_todos(self, session_id: str) -> list[dict[str, Any]]:
        """Fetch the current todo list for a session."""
        try:
            url = f"{self.base_url}/session/{session_id}/todo"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            self._classify_http_error(e)
        except urllib.error.URLError as e:
            raise OpenCodeProviderError(f"provider unavailable: {e}", exit_code=4)

    def reply_question(self, request_id: str, answers: list[list[str]]) -> None:
        body = json.dumps({"answers": answers}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/session/{self._session_id}/question/{request_id}/reply",
            data=body, headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=self._timeout)
        except urllib.error.HTTPError:
            pass

    def reject_question(self, request_id: str) -> None:
        req = urllib.request.Request(
            f"{self.base_url}/session/{self._session_id}/question/{request_id}/reject",
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=self._timeout)
        except urllib.error.HTTPError:
            pass

    def reply_permission(self, request_id: str, reply: str, message: str = "") -> None:
        body = json.dumps({"reply": reply, "message": message}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/permission/{request_id}/reply",
            data=body, headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=self._timeout)
        except urllib.error.HTTPError:
            pass


def _sse_events(resp: urllib.request.AddInfoHandler, cancel_event: threading.Event | None = None) -> Generator[dict[str, Any], None, None]:
    """Yield parsed SSE events from an HTTP response (bytes-safe).

    When *cancel_event* is provided, sets a short socket timeout so the
    generator can be interrupted between events.
    """
    buf = b""
    if cancel_event is not None:
        try:
            if hasattr(resp, "fp") and hasattr(resp.fp, "raw"):
                resp.fp.raw.settimeout(0.5)
        except Exception:
            pass
    while True:
        if cancel_event is not None and cancel_event.is_set():
            break
        try:
            chunk = resp.readline()
        except socket.timeout:
            if cancel_event is not None and cancel_event.is_set():
                break
            continue
        except Exception:
            break
        if not chunk:
            break
        buf += chunk
        while b"\n\n" in buf:
            line, buf = buf.split(b"\n\n", 1)
            for l in line.split(b"\n"):
                if l.startswith(b"data: "):
                    try:
                        yield json.loads(l[6:].decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
