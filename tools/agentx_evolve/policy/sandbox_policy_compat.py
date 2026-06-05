from __future__ import annotations

from pathlib import Path
from typing import Any


SANDBOX_POLICY_INTEGRATION_FAILED = "SANDBOX_POLICY_INTEGRATION_FAILED"


class SandboxPolicyCompat:
    def __init__(self) -> None:
        self._available = True

    def is_available(self) -> bool:
        return self._available

    def request_sandbox_check(
        self, path: str | Path, operation: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return {
            "success": True,
            "sandbox_required": True,
            "path": str(path),
            "operation": operation,
        }
