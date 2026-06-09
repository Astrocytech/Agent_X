"""aiohttp chat server serving the React SPA with SSE streaming."""

import asyncio
import json
import re
import signal
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path

from typing import Any

from aiohttp import web


_UI_DIST = Path(__file__).resolve().parent.parent.parent.parent / "ui" / "dist"

_CHAT_ROOT = Path(".agentx-chat")


def _chat_dir(session_id: str) -> Path:
    return _CHAT_ROOT / session_id


def _chat_messages_path(session_id: str) -> Path:
    return _chat_dir(session_id) / "messages.jsonl"


def _chat_meta_path(session_id: str) -> Path:
    return _chat_dir(session_id) / "meta.json"


def _join_fragments(fragments: list[str]) -> str:
    """Join text fragments, adding a space after sentence-ending punctuation
    when the next fragment does not start with whitespace."""
    if not fragments:
        return ""
    result = fragments[0]
    for frag in fragments[1:]:
        if frag and result and result[-1] in ".!?" and not frag.startswith((" ", "\t", "\n")):
            result += " " + frag
        else:
            result += frag
    return result


def _save_chat_message(session_id: str, role: str, content: str, reasoning: str = "") -> None:
    """Append a message to the chat session's messages file."""
    d = _chat_dir(session_id)
    d.mkdir(parents=True, exist_ok=True)
    record = {"role": role, "content": content, "timestamp": datetime.utcnow().isoformat() + "Z"}
    if reasoning:
        record["reasoning"] = reasoning
    line = json.dumps(record)
    with open(_chat_messages_path(session_id), "a") as f:
        f.write(line + "\n")


def _default_session_name(session_id: str) -> str:
    """Generate a default session name."""
    d = _chat_dir(session_id)
    meta = {}
    p = _chat_meta_path(session_id)
    if p.exists():
        meta = json.loads(p.read_text())
    created = meta.get("created_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    return f"Chat {created}"


def _save_chat_meta(session_id: str, **kw) -> None:
    """Write metadata for a chat session."""
    d = _chat_dir(session_id)
    d.mkdir(parents=True, exist_ok=True)
    existing = {}
    p = _chat_meta_path(session_id)
    if p.exists():
        existing = json.loads(p.read_text())
    existing.update(kw)
    existing.setdefault("created_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    existing.setdefault("session_name", _default_session_name(session_id))
    p.write_text(json.dumps(existing, indent=2))


def _list_sessions(provider=None):
    sessions = []
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Current provider session (always shown)
    if provider and hasattr(provider, "session_id"):
        sid = provider.session_id
        if sid:
            short_id = (sid[:20] + "...") if len(sid) > 20 else sid
            meta = {}
            mp = _chat_meta_path(sid)
            if mp.exists():
                meta = json.loads(mp.read_text())
            session_name = meta.get("session_name", "Current session")
            sessions.append({
                "run_id": sid,
                "session_name": session_name,
                "date": meta.get("created_at", now),
                "short_id": short_id,
            })

    # CLI task runs
    run_root = Path(".agentx-init/runs")
    if run_root.exists():
        for entry in sorted(run_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not entry.is_dir():
                continue
            meta_path = entry / "run_metadata.json"
            meta = {}
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
            command = meta.get("command", "unknown")
            ts_part = entry.name.split("-")[0]
            try:
                dt = datetime.strptime(ts_part, "%Y%m%dT%H%M%SZ")
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                date_str = ts_part
            sess_id = meta.get("metadata", {}).get("opencode_session_id", "") or entry.name
            short_id = (sess_id[:20] + "...") if len(sess_id) > 20 else sess_id
            sessions.append({
                "run_id": entry.name,
                "session_name": command,
                "date": date_str,
                "short_id": short_id,
            })

    # Saved chat sessions
    if _CHAT_ROOT.exists():
        for entry in sorted(_CHAT_ROOT.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not entry.is_dir():
                continue
            meta = {}
            mp = entry / "meta.json"
            if mp.exists():
                meta = json.loads(mp.read_text())
            run_id = entry.name
            # Fall back to directory mtime when meta.json is missing
            date_str = meta.get("created_at", "")
            if not date_str:
                date_str = datetime.fromtimestamp(entry.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            short_id = (run_id[:20] + "...") if len(run_id) > 20 else run_id
            session_name = meta.get("session_name", "Chat")
            sessions.append({
                "run_id": run_id,
                "session_name": session_name,
                "date": date_str,
                "short_id": short_id,
            })

    # Deduplicate by run_id (current session may duplicate a saved one)
    seen = set()
    deduped = []
    for s in sessions:
        if s["run_id"] not in seen:
            seen.add(s["run_id"])
            deduped.append(s)

    deduped.sort(key=lambda s: s["date"], reverse=True)
    return deduped


def _load_session_messages(run_id: str):
    # Try CLI task run directory first
    cli_path = Path(".agentx-init/runs") / run_id / "model_messages.jsonl"
    if cli_path.exists():
        msgs = []
        with open(cli_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    role = data.get("role", "")
                    content = data.get("content", "")
                    if content:
                        msgs.append({"role": role, "text": content, "timestamp": data.get("timestamp", ""), "reasoning": data.get("reasoning", "")})
        return msgs

    # Try chat session directory
    chat_path = _chat_messages_path(run_id)
    if chat_path.exists():
        msgs = []
        with open(chat_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    role = data.get("role", "")
                    content = data.get("content", "")
                    if content:
                        msgs.append({"role": role, "text": content, "timestamp": data.get("timestamp", ""), "reasoning": data.get("reasoning", "")})
        return msgs

    return []


async def handle_static(request: web.Request) -> web.FileResponse:
    path = request.match_info.get("path", "")
    if not path:
        path = "index.html"
    filepath = _UI_DIST / path
    if not filepath.exists() or not filepath.is_file():
        filepath = _UI_DIST / "index.html"
    resp = web.FileResponse(filepath)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


async def handle_sessions(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    return web.json_response(_list_sessions(provider=provider))


async def handle_delete_session(request: web.Request) -> web.Response:
    run_id = request.match_info["run_id"]
    import shutil
    run_dir = Path(".agentx-init/runs") / run_id
    if run_dir.exists() and run_dir.is_dir():
        shutil.rmtree(run_dir)
        return web.json_response({"ok": True})
    chat_dir = _chat_dir(run_id)
    if chat_dir.exists() and chat_dir.is_dir():
        shutil.rmtree(chat_dir)
        return web.json_response({"ok": True})
    return web.json_response({"error": "not found"}, status=404)


async def handle_clear_sessions(request: web.Request) -> web.Response:
    import shutil
    run_root = Path(".agentx-init/runs")
    if run_root.exists():
        for entry in run_root.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry)
    if _CHAT_ROOT.exists():
        for entry in _CHAT_ROOT.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry)
    return web.json_response({"ok": True})


async def handle_session_messages(request: web.Request) -> web.Response:
    run_id = request.match_info["run_id"]
    msgs = _load_session_messages(run_id)
    return web.json_response(msgs)


async def handle_rename_session(request: web.Request) -> web.Response:
    run_id = request.match_info["run_id"]
    try:
        body = json.loads(await request.read())
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)
    name = (body.get("session_name") or "").strip()
    if not name:
        return web.json_response({"error": "session_name required"}, status=400)
    _save_chat_meta(run_id, session_name=name)
    return web.json_response({"ok": True, "session_name": name})


async def handle_chat(request: web.Request) -> web.StreamResponse:
    try:
        raw = await request.read()
        print(f"[chat] body={raw!r}", file=sys.stderr)
        body = json.loads(raw)
        message = body.get("message", "").strip()
        if not message:
            raise web.HTTPBadRequest(text="missing message")

        mode = (body.get("mode") or "build").strip()
        provider = request.app.get("provider")
        if provider is None:
            raise RuntimeError("no provider in app")

        # Build messages list with mode-aware system prompts
        messages_list: list[dict] = []
        if mode == "plan":
            messages_list.append({
                "role": "system",
                "content": (
                    "You are in PLAN mode. You are in a read-only phase. "
                    "You MUST NOT make any edits, run any non-readonly shell commands, "
                    "or make any changes to the system. "
                    "You can analyze code, ask clarifying questions, and provide plans, "
                    "architecture recommendations, and thorough analysis. "
                    "When you are ready to proceed to implementation, the user will "
                    "switch to BUILD mode."
                ),
            })
        else:
            messages_list.append({
                "role": "system",
                "content": (
                    "You are in BUILD mode. You have full tool access and can make "
                    "file edits, run shell commands, and use all available tools "
                    "to implement the user's requests."
                ),
            })
        messages_list.append({"role": "user", "content": message})

        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        resp = web.StreamResponse()
        resp.headers["Content-Type"] = "text/event-stream"
        resp.headers["Cache-Control"] = "no-cache"
        resp.headers["X-Accel-Buffering"] = "no"
        await resp.prepare(request)

        sid = provider.session_id if hasattr(provider, "session_id") else ""

        # Persist user message and meta.json before streaming starts
        # so the session is never empty on reload if streaming fails.
        if sid:
            try:
                _save_chat_message(sid, "user", message)
                # Ensure meta.json exists (session_name defaults to first message)
                meta = {}
                mp = _chat_meta_path(sid)
                if mp.exists():
                    meta = json.loads(mp.read_text())
                if "session_name" not in meta:
                    _save_chat_meta(
                        sid,
                        session_id=sid,
                        session_name=message[:50] + ("..." if len(message) > 50 else ""),
                    )
            except Exception as e:
                print(f"[chat] failed to persist user message: {e}", file=sys.stderr)

        started = threading.Event()
        accumulated: list[str] = []
        accumulated_reasoning: list[str] = []

        def _feed_queue():
            try:
                gen = provider.complete_streaming(messages_list)
                started.set()
                for event in gen:
                    if event.get("type") == "text" and event.get("author") == "assistant":
                        text = event.get("text", "")
                        if text:
                            accumulated.append(text)
                    if event.get("type") == "reasoning" and event.get("author") == "assistant":
                        rtext = event.get("text", "")
                        if rtext:
                            accumulated_reasoning.append(rtext)
                    fut = asyncio.run_coroutine_threadsafe(queue.put(event), loop)
                    fut.result()
            except StopIteration:
                pass
            except Exception as e:
                print(f"[feed_queue] error: {type(e).__name__}: {e}", file=sys.stderr)
                traceback.print_exc()
                err = {"type": "error", "text": f"{type(e).__name__}: {e}"}
                try:
                    fut = asyncio.run_coroutine_threadsafe(queue.put(err), loop)
                    fut.result(timeout=5)
                except Exception:
                    pass
            finally:
                try:
                    asyncio.run_coroutine_threadsafe(queue.put(None), loop).result(timeout=5)
                except Exception:
                    pass

        thread = threading.Thread(target=_feed_queue, daemon=True)
        thread.start()

        if not started.wait(timeout=10):
            print("[chat] provider did not start streaming within 10s", file=sys.stderr)
            await resp.write(b"data: {\"type\":\"error\",\"text\":\"Provider did not respond within 10s\"}\n\n")
            await resp.write(b"data: [DONE]\n\n")
            return resp

        while True:
            event = await queue.get()
            if event is None:
                break
            if event.get("type") == "text" and event.get("author") == "user":
                continue
            data = json.dumps(event)
            try:
                await resp.write(f"data: {data}\n\n".encode())
            except ConnectionResetError:
                break

        try:
            await resp.write(b"data: [DONE]\n\n")
        except (ConnectionResetError, ConnectionError):
            pass

        # Persist whatever assistant text was accumulated (even on interrupt)
        if sid and accumulated:
            try:
                reasoning_text = _join_fragments(accumulated_reasoning) if accumulated_reasoning else ""
                _save_chat_message(sid, "assistant", _join_fragments(accumulated), reasoning=reasoning_text)
            except Exception as e:
                print(f"[chat] failed to persist assistant message: {e}", file=sys.stderr)

        return resp
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"{type(e).__name__}: {e}")


async def handle_import_session(request: web.Request) -> web.Response:
    try:
        body = json.loads(await request.read())
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)

    messages = body.get("messages", [])
    if not isinstance(messages, list) or not messages:
        return web.json_response({"error": "messages array required"}, status=400)

    session_name = (body.get("session_name") or "").strip() or "Imported Session"
    import uuid
    session_id = str(uuid.uuid4())

    _save_chat_meta(session_id, session_name=session_name)
    for msg in messages:
        role = msg.get("role", "")
        text = msg.get("text", "")
        if role and text:
            _save_chat_message(session_id, role, text)

    return web.json_response({"ok": True, "session_id": session_id, "session_name": session_name})


async def handle_revert_session(request: web.Request) -> web.Response:
    session_id = request.match_info["session_id"]
    try:
        body = json.loads(await request.read())
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)
    message_index = body.get("message_index")
    if not isinstance(message_index, int) or message_index < 0:
        return web.json_response({"error": "message_index required"}, status=400)
    chat_path = _chat_messages_path(session_id)
    if not chat_path.exists():
        return web.json_response({"error": "session not found"}, status=404)
    try:
        lines = chat_path.read_text().strip().split("\n")
        if message_index >= len(lines):
            return web.json_response({"error": "message_index out of range"}, status=400)
        kept = lines[:message_index]
        chat_path.write_text("\n".join(kept) + ("\n" if kept else ""))
        return web.json_response({"ok": True, "message_count": len(kept)})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_model_switch(request: web.Request) -> web.Response:
    try:
        body = json.loads(await request.read())
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)
    model = (body.get("model") or "").strip()
    if not model:
        return web.json_response({"error": "model required"}, status=400)
    new_provider_name = (body.get("provider") or "").strip()
    provider = request.app.get("provider")
    if provider is None:
        return web.json_response({"error": "no provider"}, status=400)
    current_provider_name = getattr(provider, "_provider_id", "")

    try:
        if new_provider_name and new_provider_name != current_provider_name:
            config = request.app.get("config")
            if config is None:
                return web.json_response({"error": "config not available for provider switch"}, status=400)
            from agentx_evolve.providers.provider_router import ProviderRouter
            old_config_provider = config.provider
            config.provider = new_provider_name
            config.model = model
            new_provider = ProviderRouter(config).get_provider()
            config.provider = old_config_provider
            request.app["provider"] = new_provider
            request.app["model"] = model
            return web.json_response({"ok": True, "model": model, "provider": new_provider_name})
        provider.model = model
        request.app["model"] = model
        return web.json_response({"ok": True, "model": model})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_models(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    models: list[dict[str, Any]] = []
    # Fetch from current provider
    if provider is not None and hasattr(provider, "get_models"):
        try:
            models.extend(provider.get_models())
        except Exception:
            pass
    # Also try fetching from opencode server; start it if not running
    opencode_base = request.app.get("opencode_base_url", "http://127.0.0.1:14096")
    _ensure_opencode_server(opencode_base)
    try:
        req = urllib.request.Request(f"{opencode_base}/config/providers", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for prov in data.get("providers", []):
                pid = prov.get("id", "")
                for mid, minfo in (prov.get("models") or {}).items():
                    model_entry = {
                        "id": mid,
                        "name": minfo.get("name", mid) if isinstance(minfo, dict) else mid,
                        "provider": pid,
                    }
                    if model_entry not in models:
                        models.append(model_entry)
    except Exception:
        pass
    return web.json_response({"models": models})


def _ensure_opencode_server(base_url: str) -> None:
    """Start the opencode server if it's not already running."""
    try:
        hr = urllib.request.Request(f"{base_url}/global/health")
        urllib.request.urlopen(hr, timeout=2)
        return
    except Exception:
        pass
    port_match = re.search(r":(\d+)$", base_url)
    port = port_match.group(1) if port_match else "14096"
    try:
        proc = subprocess.Popen(
            ["opencode", "serve", "--port", port],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(30):
            try:
                hr = urllib.request.Request(f"{base_url}/global/health")
                urllib.request.urlopen(hr, timeout=2)
                return
            except Exception:
                time.sleep(1)
    except FileNotFoundError:
        pass


async def handle_subagents(request: web.Request) -> web.Response:
    session_id = request.match_info["session_id"]
    provider = request.app.get("provider")
    if provider and hasattr(provider, "get_subagent_sessions"):
        subs = provider.get_subagent_sessions(session_id)
        return web.json_response(subs)
    return web.json_response([])


async def handle_subagent_messages(request: web.Request) -> web.Response:
    session_id = request.match_info["session_id"]
    provider = request.app.get("provider")
    if provider and hasattr(provider, "get_session_messages"):
        try:
            msgs = provider.get_session_messages(session_id)
            return web.json_response(msgs)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    return web.json_response({"error": "no provider"}, status=400)


async def handle_new_session(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    if provider is None or not hasattr(provider, "reset_session"):
        return web.json_response({"error": "provider does not support new sessions"}, status=400)
    try:
        new_sid = provider.reset_session()
        return web.json_response({"session_id": new_sid})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_question_reply(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    if provider is None or not hasattr(provider, "reply_question"):
        return web.json_response({"error": "provider does not support questions"}, status=400)
    request_id = request.match_info["request_id"]
    try:
        body = json.loads(await request.read())
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)
    answers = body.get("answers", [])
    try:
        provider.reply_question(request_id, answers)
        return web.json_response({"ok": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_question_reject(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    if provider is None or not hasattr(provider, "reject_question"):
        return web.json_response({"error": "provider does not support questions"}, status=400)
    request_id = request.match_info["request_id"]
    try:
        provider.reject_question(request_id)
        return web.json_response({"ok": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_permission_reply(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    if provider is None or not hasattr(provider, "reply_permission"):
        return web.json_response({"error": "provider does not support permissions"}, status=400)
    request_id = request.match_info["request_id"]
    try:
        body = json.loads(await request.read())
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)
    reply = body.get("reply", "reject")
    message = body.get("message", "")
    try:
        provider.reply_permission(request_id, reply, message)
        return web.json_response({"ok": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_todos(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    if provider is None or not hasattr(provider, "get_todos"):
        return web.json_response([])
    session_id = getattr(provider, "session_id", "")
    if not session_id:
        return web.json_response([])
    try:
        todos = provider.get_todos(session_id)
        return web.json_response(todos)
    except Exception:
        return web.json_response([])


async def handle_agent_mode(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    if provider and hasattr(provider, "get_governance_info"):
        return web.json_response(provider.get_governance_info())
    return web.json_response({
        "agent_mode": "general",
        "fic_document": "",
        "ceiling": "P9_EXTERNAL_SIDE_EFFECT",
        "allowed_tools": [],
        "forbidden_tools": [],
        "phase_0_active": False,
    })


async def handle_set_agent_mode(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    if provider is None or not hasattr(provider, "set_agent_mode"):
        return web.json_response({"error": "provider does not support agent mode"}, status=400)
    try:
        body = json.loads(await request.read())
    except Exception:
        return web.json_response({"error": "invalid JSON"}, status=400)
    mode = body.get("agent_mode", "general")
    fic_doc = body.get("fic_document", "")
    provider.set_agent_mode(mode, fic_doc)
    return web.json_response(provider.get_governance_info())


async def handle_fic_documents(request: web.Request) -> web.Response:
    docs: list[dict[str, str]] = []
    l1_docs = Path("L1/docs")
    if l1_docs.exists():
        for f in sorted(l1_docs.iterdir()):
            if f.suffix in (".md", ".yaml", ".yml"):
                title = f.stem.replace("_", " ").replace("-", " ").title()
                docs.append({"path": str(f), "name": title})
    return web.json_response(docs)


def _make_app(provider) -> web.Application:
    app = web.Application()

    app["provider"] = provider

    app.router.add_get("/api/ping", lambda r: web.Response(text="pong"))
    app.router.add_get("/api/sessions", handle_sessions)
    app.router.add_delete("/api/sessions", handle_clear_sessions)
    app.router.add_get("/api/status", handle_status)
    app.router.add_get("/api/sessions/{session_id}/subagents", handle_subagents)
    app.router.add_get("/api/sessions/{session_id}/subagent-messages", handle_subagent_messages)
    app.router.add_get("/api/sessions/{run_id}/messages", handle_session_messages)
    app.router.add_patch("/api/sessions/{run_id}", handle_rename_session)
    app.router.add_delete("/api/sessions/{run_id}", handle_delete_session)
    app.router.add_post("/api/chat", handle_chat)
    app.router.add_post("/api/session/new", handle_new_session)
    app.router.add_post("/api/sessions/import", handle_import_session)
    app.router.add_get("/api/models", handle_models)
    app.router.add_post("/api/sessions/{session_id}/revert", handle_revert_session)
    app.router.add_post("/api/model/switch", handle_model_switch)
    app.router.add_post("/api/questions/{request_id}/reply", handle_question_reply)
    app.router.add_post("/api/questions/{request_id}/reject", handle_question_reject)
    app.router.add_post("/api/permissions/{request_id}/reply", handle_permission_reply)
    app.router.add_get("/api/todos", handle_todos)
    app.router.add_get("/api/agent-mode", handle_agent_mode)
    app.router.add_post("/api/agent-mode", handle_set_agent_mode)
    app.router.add_get("/api/fic-documents", handle_fic_documents)

    ui_exists = _UI_DIST.exists() and (_UI_DIST / "index.html").exists()
    if ui_exists:
        app.router.add_get("/", handle_static)
        app.router.add_get("/{path:.*}", handle_static)
    else:
        async def build_hint(request):
            return web.Response(
                text="React UI not built. Run: cd ui && npm run build",
                content_type="text/plain",
                status=500,
            )
        app.router.add_get("/", build_hint)
        app.router.add_get("/{path:.*}", build_hint)

    return app


async def handle_status(request: web.Request) -> web.Response:
    provider = request.app.get("provider")
    sid = provider.session_id if provider and hasattr(provider, "session_id") else ""
    pname = getattr(provider, "_provider_id", "") if provider else ""
    session_name = ""
    if sid:
        mp = _chat_meta_path(sid)
        if mp.exists():
            session_name = json.loads(mp.read_text()).get("session_name", "")
    p_model = getattr(provider, "model", "") if provider else ""
    gov_info = provider.get_governance_info() if provider and hasattr(provider, "get_governance_info") else {}
    return web.json_response({
        "model": p_model or request.app.get("model", ""),
        "session_id": sid,
        "provider": pname,
        "session_name": session_name,
        "agent_mode": gov_info.get("agent_mode", "general"),
        "fic_document": gov_info.get("fic_document", ""),
        "ceiling": gov_info.get("ceiling", "P9_EXTERNAL_SIDE_EFFECT"),
    })


def run_chat_window(provider, session_id="", model="", config=None) -> int:
    app = _make_app(provider)
    app["session_id"] = session_id
    app["model"] = model
    if config is not None:
        app["config"] = config
        app["opencode_base_url"] = getattr(config, "opencode_base_url", "http://127.0.0.1:14096")
    runner = web.AppRunner(app)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(runner.setup())

    site = web.TCPSite(runner, "127.0.0.1", 0)
    loop.run_until_complete(site.start())

    port = site._server.sockets[0].getsockname()[1]

    url = f"http://127.0.0.1:{port}"
    print(f"Chat UI: {url}", file=sys.stderr)
    webbrowser.open(url)

    # ensure the provider has an opencode session before serving
    if hasattr(provider, "_ensure_session"):
        provider._ensure_session()

    def shutdown():
        print("\nShutting down...", file=sys.stderr)
        loop.call_soon_threadsafe(lambda: loop.stop())

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()

    return 0
