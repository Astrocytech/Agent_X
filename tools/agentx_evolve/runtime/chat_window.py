"""aiohttp chat server serving the React SPA with SSE streaming."""

import asyncio
import json
import signal
import sys
import threading
import traceback
import webbrowser
from datetime import datetime
from pathlib import Path

from aiohttp import web


_UI_DIST = Path(__file__).resolve().parent.parent.parent.parent / "ui" / "dist"

_CHAT_ROOT = Path(".agentx-chat")


def _chat_dir(session_id: str) -> Path:
    return _CHAT_ROOT / session_id


def _chat_messages_path(session_id: str) -> Path:
    return _chat_dir(session_id) / "messages.jsonl"


def _chat_meta_path(session_id: str) -> Path:
    return _chat_dir(session_id) / "meta.json"


def _save_chat_message(session_id: str, role: str, content: str) -> None:
    """Append a message to the chat session's messages file."""
    d = _chat_dir(session_id)
    d.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"role": role, "content": content})
    with open(_chat_messages_path(session_id), "a") as f:
        f.write(line + "\n")


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
    p.write_text(json.dumps(existing, indent=2))


def _list_sessions(provider=None):
    sessions = []
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Current provider session (always shown)
    if provider and hasattr(provider, "session_id"):
        sid = provider.session_id
        if sid:
            short_id = (sid[:20] + "...") if len(sid) > 20 else sid
            sessions.append({
                "run_id": sid,
                "command": "chat (current)",
                "date": now,
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
            opencode_sid = meta.get("metadata", {}).get("opencode_session_id", "")
            short_id = (opencode_sid[:20] + "...") if len(opencode_sid) > 20 else opencode_sid
            sessions.append({
                "run_id": entry.name,
                "command": command,
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
            date_str = meta.get("created_at", "")
            short_id = (run_id[:20] + "...") if len(run_id) > 20 else run_id
            sessions.append({
                "run_id": run_id,
                "command": "chat",
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
                        msgs.append({"role": role, "text": content})
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
                        msgs.append({"role": role, "text": content})
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


async def handle_chat(request: web.Request) -> web.StreamResponse:
    try:
        raw = await request.read()
        print(f"[chat] body={raw!r}", file=sys.stderr)
        body = json.loads(raw)
        message = body.get("message", "").strip()
        if not message:
            raise web.HTTPBadRequest(text="missing message")

        provider = request.app.get("provider")
        if provider is None:
            raise RuntimeError("no provider in app")

        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        resp = web.StreamResponse()
        resp.headers["Content-Type"] = "text/event-stream"
        resp.headers["Cache-Control"] = "no-cache"
        resp.headers["X-Accel-Buffering"] = "no"
        await resp.prepare(request)

        started = threading.Event()
        accumulated: list[str] = []

        def _feed_queue():
            try:
                gen = provider.complete_streaming([{"role": "user", "content": message}])
                started.set()
                for event in gen:
                    if event.get("type") == "text" and event.get("author") == "assistant":
                        text = event.get("text", "")
                        if text:
                            accumulated.append(text)
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

        # Persist messages after successful streaming
        try:
            sid = provider.session_id if hasattr(provider, "session_id") else ""
            if sid:
                _save_chat_message(sid, "user", message)
                assistant_text = "".join(accumulated)
                if assistant_text:
                    _save_chat_message(sid, "assistant", assistant_text)
                _save_chat_meta(sid, session_id=sid)
        except Exception as e:
            print(f"[chat] failed to persist messages: {e}", file=sys.stderr)

        return resp
    except Exception as e:
        traceback.print_exc()
        return web.Response(status=500, text=f"{type(e).__name__}: {e}")


def _make_app(provider) -> web.Application:
    app = web.Application()

    app["provider"] = provider

    app.router.add_get("/api/ping", lambda r: web.Response(text="pong"))
    app.router.add_get("/api/sessions", handle_sessions)
    app.router.add_delete("/api/sessions", handle_clear_sessions)
    app.router.add_get("/api/status", handle_status)
    app.router.add_get("/api/sessions/{run_id}/messages", handle_session_messages)
    app.router.add_delete("/api/sessions/{run_id}", handle_delete_session)
    app.router.add_post("/api/chat", handle_chat)

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
    return web.json_response({
        "model": request.app.get("model", ""),
        "session_id": sid,
        "provider": pname,
    })


def run_chat_window(provider, session_id="", model="") -> int:
    app = _make_app(provider)
    app["session_id"] = session_id
    app["model"] = model
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
