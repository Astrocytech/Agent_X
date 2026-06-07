from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any

_LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "logs",
)
_MAX_BYTES = 10_485_760


class ConversationLogger:
    def __init__(self) -> None:
        self._logger = logging.getLogger("agentx.conversation")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        self._handler = None
        self._log_path = None
        self._ensure_handler()

    def _ensure_handler(self) -> None:
        if self._handler is not None:
            if os.path.getsize(self._log_path) < _MAX_BYTES:
                return
            self._logger.removeHandler(self._handler)
            self._handler.close()
            self._handler = None
        existing = sorted(
            (f for f in os.listdir(_LOG_DIR) if f.startswith("agent_x_") and f.endswith(".log")),
            key=lambda f: os.path.getmtime(os.path.join(_LOG_DIR, f)),
            reverse=True,
        ) if os.path.isdir(_LOG_DIR) else []
        if existing:
            newest = os.path.join(_LOG_DIR, existing[0])
            if os.path.getsize(newest) < _MAX_BYTES:
                self._log_path = newest
                self._handler = logging.FileHandler(self._log_path, mode="a", encoding="utf-8")
                self._handler.setLevel(logging.DEBUG)
                fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
                self._handler.setFormatter(fmt)
                self._logger.addHandler(self._handler)
                return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(_LOG_DIR, exist_ok=True)
        self._log_path = os.path.join(_LOG_DIR, f"agent_x_{ts}.log")
        self._handler = logging.FileHandler(self._log_path, mode="a", encoding="utf-8")
        self._handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self._handler.setFormatter(fmt)
        self._logger.addHandler(self._handler)

    def _log(self, event: str, provider: str, model: str, data: dict[str, Any]) -> None:
        self._ensure_handler()
        entry = {"event": event, "provider": provider, "model": model, **data}
        msg = "CONVERSATION " + json.dumps(entry, default=str)
        if event == "error":
            self._logger.error(msg)
        else:
            self._logger.info(msg)

    def log_request(self, provider: str, model: str, messages: list[dict], kwargs: dict = None) -> None:
        data = {"messages": messages}
        if kwargs:
            data["kwargs"] = kwargs
        self._log("request", provider, model, data)

    def log_response(self, provider: str, model: str, response: dict, duration_ms: float = 0.0) -> None:
        self._log("response", provider, model, {"duration_ms": round(duration_ms, 1), "response": response})

    def log_error(self, provider: str, model: str, error: str, duration_ms: float = 0.0) -> None:
        self._log("error", provider, model, {"duration_ms": round(duration_ms, 1), "error": error})
