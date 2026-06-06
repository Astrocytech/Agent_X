import warnings
from typing import Any

from agentx_evolve.context.model_context_compatibility import (
    check_model_context_compatibility as _check_model_context_compatibility,
)

warnings.warn(
    "Import from agentx_evolve.context.model_context_compatibility directly",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "check_model_context_compatibility",
    "check_model_compatibility",
]


def check_model_context_compatibility(*args, **kwargs) -> dict[str, Any]:
    return _check_model_context_compatibility(*args, **kwargs)


def check_model_compatibility(model_name: str, context: Any) -> bool:
    ...
    return True
