import warnings
from typing import Any

from agentx_evolve.context.tool_context_compatibility import (
    check_tool_context_compatibility as _check_tool_context_compatibility,
)

warnings.warn(
    "Import from agentx_evolve.context.tool_context_compatibility directly",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "check_tool_context_compatibility",
    "check_tool_compatibility",
]


def check_tool_context_compatibility(*args, **kwargs) -> dict[str, Any]:
    return _check_tool_context_compatibility(*args, **kwargs)


def check_tool_compatibility(tool_name: str, context: Any) -> bool:
    ...
    return True
