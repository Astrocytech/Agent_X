from __future__ import annotations

from typing import Any

__all__ = [
    "ContextBuilderClient",
]


class ContextBuilderClient:
    def build_context(self, task_pack: dict[str, Any]) -> dict[str, Any]:
        return {
            "context_id": "",
            "task_pack_id": task_pack.get("task_pack_id", ""),
            "summary": task_pack.get("summary", ""),
            "files": task_pack.get("files", []),
            "status": "built",
        }
