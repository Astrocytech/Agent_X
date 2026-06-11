from __future__ import annotations

from typing import Any, Protocol


class MvpBaseExecutor(Protocol):
    def execute(self, action: Any, envelope: Any, context: dict[str, Any]) -> dict[str, Any]:
        ...
