from __future__ import annotations
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Generator
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BLOCKED_SERVER = "API server unavailable"
FAIL_MODEL = "model/endpoint not found (404)"
FAIL_RATE_LIMIT = "rate limited (429)"
FAIL_SERVER = "server error (5xx)"
FAIL_TIMEOUT = "provider timeout"
FAIL_MALFORMED = "malformed response"


_CHAT_ROOT = Path(".agentx-chat")


class APIProviderError(Exception):
    def __init__(self, message: str, exit_code: int, status: str = "FAIL"):
        self.message = message
        self.exit_code = exit_code
        self.status = status
        super().__init__(message)


def _chat_messages_path(session_id: str) -> Path:
    return _CHAT_ROOT / session_id / "messages.jsonl"


class APIProvider:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434/v1",
        api_key: str = "",
        model: str = "qwen2.5-coder:7b",
        timeout_seconds: int = 0,
        session_id: str = "",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("AGENTX_API_KEY", "")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._session_id: str = session_id or str(uuid.uuid4())
        self._provider_id: str = "api"
        self._subagent_sessions: dict[str, list[str]] = {}

    def reset_session(self) -> str:
        self._session_id = str(uuid.uuid4())
        return self._session_id

    @property
    def session_id(self) -> str:
        return self._session_id

    def get_models(self) -> list[dict[str, Any]]:
        try:
            url = f"{self.base_url}/models"
            req = Request(url, headers=self._headers(), method="GET")
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw = data.get("data") or data.get("models") or []
                return [{"id": m.get("id", ""), "name": m.get("id", ""), "provider": self._provider_id} for m in raw if m.get("id")]
        except Exception:
            return [{"id": self.model, "name": f"{self.model} (current)", "provider": self._provider_id}]

    @property
    def _timeout(self) -> float | None:
        return None if self.timeout_seconds == 0 else float(self.timeout_seconds)

    def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        data = self._post(body)
        return self._parse_response(data)

    def complete_structured(
        self, messages: list[dict[str, Any]], **kwargs: Any,
    ) -> dict[str, Any]:
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
            "model": self.model,
            "messages": [{"role": "user", "content": user_text or "."}],
            "stream": False,
        }
        if system_text:
            body["messages"].insert(0, {"role": "system", "content": system_text})
        data = self._post(body)
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
        raise APIProviderError(
            f"LLM did not return a valid structured plan JSON:\n{content[:500]}",
            exit_code=1,
        )

    def complete_streaming(
        self, messages: list[dict[str, Any]], **kwargs: Any,
    ) -> Generator[dict[str, Any], None, dict[str, Any]]:
        body = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        resp = self._post_stream(body)
        full_text = ""
        reasoning_text = ""
        subagent_text_buf = ""
        in_subagent = False
        subagent_desc = ""
        try:
            for event in _sse_events(resp):
                if not event:
                    continue
                delta = event.get("choices", [{}])[0].get("delta", {})
                if delta.get("reasoning_content"):
                    chunk = delta["reasoning_content"]
                    reasoning_text += chunk
                    yield {"type": "reasoning", "text": chunk, "author": "assistant"}
                if delta.get("content"):
                    chunk = delta["content"]
                    full_text += chunk

                    if in_subagent:
                        subagent_text_buf += chunk
                        end_idx = subagent_text_buf.find("</task>")
                        if end_idx != -1:
                            subagent_text_buf = subagent_text_buf[:end_idx]
                            in_subagent = False
                            result = self._execute_subtask(subagent_desc)
                            yield {"type": "subagent", "status": "completed", "session_id": result["session_id"], "name": subagent_desc[:50], "description": subagent_desc, "output": result["output"]}
                            yield {"type": "text", "text": result["output"], "author": "assistant"}
                            subagent_text_buf = ""
                            subagent_desc = ""
                        continue

                    task_start = chunk.find("<task>")
                    if task_start != -1:
                        in_subagent = True
                        before = chunk[:task_start]
                        after = chunk[task_start + 6:]
                        if before:
                            yield {"type": "text", "text": before, "author": "assistant"}
                        subagent_text_buf = after
                        desc_end = after.find("</description>")
                        if desc_end != -1:
                            subagent_desc = after[len("<description>"):desc_end] if after.startswith("<description>") else ""
                            subagent_text_buf = after[desc_end + 14:]
                        else:
                            desc_start = after.find("<description>")
                            if desc_start != -1:
                                subagent_desc = after[desc_start + len("<description>"):]
                                subagent_text_buf = after[desc_start:]
                            else:
                                subagent_text_buf = after
                        yield {"type": "subagent", "status": "running", "name": "subtask", "description": subagent_desc[:80] if subagent_desc else "Processing..."}
                        continue

                    sub_start = chunk.find("<subtask>")
                    if sub_start != -1:
                        in_subagent = True
                        before = chunk[:sub_start]
                        after = chunk[sub_start + 9:]
                        if before:
                            yield {"type": "text", "text": before, "author": "assistant"}
                        subagent_text_buf = after
                        subagent_desc = after
                        yield {"type": "subagent", "status": "running", "name": "subtask", "description": subagent_desc[:80]}
                        continue

                    yield {"type": "text", "text": chunk, "author": "assistant"}
        except Exception as e:
            yield {"type": "error", "text": f"Stream error: {e}"}
        return {"role": "assistant", "content": full_text, "finish_reason": "stop"}

    def _execute_subtask(self, description: str) -> dict[str, Any]:
        sub_id = str(uuid.uuid4())
        self._subagent_sessions.setdefault(self._session_id or "", []).append(sub_id)
        sub = APIProvider(
            base_url=self.base_url,
            api_key=self.api_key,
            model=self.model,
            timeout_seconds=self.timeout_seconds,
            session_id=sub_id,
        )
        try:
            resp = sub.complete([{"role": "user", "content": description}])
            output = resp.get("content", "")
        except Exception as e:
            output = f"Subtask failed: {e}"
        return {"session_id": sub_id, "output": output}

    def get_subagent_sessions(self, parent_session_id: str) -> list[str]:
        return self._subagent_sessions.get(parent_session_id, [])

    def get_session_messages(self, session_id: str) -> list[dict[str, Any]]:
        path = _chat_messages_path(session_id)
        if not path.exists():
            return []
        msgs = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    role = data.get("role", "")
                    content = data.get("content", "")
                    if content:
                        msgs.append({"role": role, "text": content})
        return msgs

    def _chat_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8")
        req = Request(
            self._chat_url(), data=data,
            headers=self._headers(),
            method="POST",
        )
        try:
            with urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as e:
            self._raise_http_error(e)
        except URLError as e:
            raise APIProviderError(
                f"{BLOCKED_SERVER}: {e.reason if hasattr(e, 'reason') else e}",
                exit_code=2, status="BLOCKED",
            )

    def _post_stream(self, body: dict[str, Any]):
        data = json.dumps(body).encode("utf-8")
        req = Request(
            self._chat_url(), data=data,
            headers=self._headers(),
            method="POST",
        )
        try:
            return urlopen(req, timeout=self._timeout)
        except HTTPError as e:
            self._raise_http_error(e)
        except URLError as e:
            raise APIProviderError(
                f"{BLOCKED_SERVER}: {e.reason if hasattr(e, 'reason') else e}",
                exit_code=2, status="BLOCKED",
            )

    def _raise_http_error(self, e: HTTPError) -> None:
        code = e.code
        if code in (404,):
            raise APIProviderError(FAIL_MODEL, exit_code=1)
        elif code == 429:
            raise APIProviderError(FAIL_RATE_LIMIT, exit_code=1)
        elif 500 <= code < 600:
            raise APIProviderError(FAIL_SERVER, exit_code=1)
        else:
            raise APIProviderError(
                f"HTTP {code}: {e.reason}", exit_code=1,
            )

    @staticmethod
    def _parse_response(data: dict[str, Any]) -> dict[str, Any]:
        choices = data.get("choices", [])
        if not choices:
            return {"role": "assistant", "content": "", "tool_calls": [], "finish_reason": "stop"}
        choice = choices[0]
        message = choice.get("message", {})
        finish = choice.get("finish_reason", "stop")
        return {
            "role": "assistant",
            "content": message.get("content", ""),
            "tool_calls": [],
            "finish_reason": finish,
        }


def _sse_events(resp) -> Generator[dict[str, Any], None, None]:
    buf = b""
    for chunk in iter(lambda: resp.read(4096), b""):
        if not chunk:
            break
        buf += chunk
        while b"\n\n" in buf:
            line, buf = buf.split(b"\n\n", 1)
            for l in line.split(b"\n"):
                if l.startswith(b"data: "):
                    payload = l[6:]
                    if payload.strip() == b"[DONE]":
                        return
                    try:
                        yield json.loads(payload.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
