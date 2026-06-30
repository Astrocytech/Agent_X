from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ToolAdapter(ABC):
    @abstractmethod
    def describe_capabilities(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def validate_call(self, call: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def simulate_call(self, call: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def execute_call(self, call: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def normalize_result(self, result: dict[str, Any]) -> dict[str, Any]:
        ...
