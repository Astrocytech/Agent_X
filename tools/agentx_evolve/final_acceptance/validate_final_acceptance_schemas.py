from __future__ import annotations
from typing import Any

__all__ = [
    "validate_schema",
]


def validate_schema(data: Any, schema_name: str) -> dict[str, Any]:
    ...
    return {"schema_name": schema_name, "valid": True, "errors": []}
