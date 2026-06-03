from __future__ import annotations
from typing import Any


class SchemaInjector:
    def inject(self, task_type: str, schemas: dict[str, Any] | None = None) -> dict | None:
        if schemas is None:
            return None
        return schemas.get(task_type)

    def list_available(self, schemas: dict[str, Any]) -> list[str]:
        return list(schemas.keys())
