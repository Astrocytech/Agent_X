import warnings
from typing import Any

from agentx_evolve.context.task_pack_builder import (
    build_task_pack as _build_task_pack,
    build_context_items_from_sources as _build_context_items_from_sources,
    inject_schema as _inject_schema,
    list_available_schemas as _list_available_schemas,
)

warnings.warn(
    "Import from agentx_evolve.context.task_pack_builder directly instead of task_packer",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "build_task_pack",
    "build_context_items_from_sources",
    "inject_schema",
    "list_available_schemas",
]


def build_task_pack(*args, **kwargs) -> Any:
    return _build_task_pack(*args, **kwargs)


def build_context_items_from_sources(*args, **kwargs) -> Any:
    return _build_context_items_from_sources(*args, **kwargs)


def inject_schema(*args, **kwargs) -> Any:
    return _inject_schema(*args, **kwargs)


def list_available_schemas(*args, **kwargs) -> Any:
    return _list_available_schemas(*args, **kwargs)
