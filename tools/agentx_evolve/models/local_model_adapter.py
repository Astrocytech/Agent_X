from __future__ import annotations

import warnings as _warnings

__all__ = [
    "LocalProviderAdapter",
]

_warnings.warn(
    "local_model_adapter is deprecated; use local_provider_adapter instead.",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from agentx_evolve.models.local_provider_adapter import (  # noqa: F401
        LocalProviderAdapter,
    )
except ImportError:
    from typing import Any

    class LocalProviderAdapter:  # type: ignore[no-redef]
        def is_available(self, context: dict[str, Any]) -> bool:
            return False

        def run_prompt(self, request: Any, profile: Any, context: Any) -> Any:
            raise NotImplementedError("local_provider_adapter not available")
