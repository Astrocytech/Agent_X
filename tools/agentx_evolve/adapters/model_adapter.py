from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agentx_evolve.adapters.model_request import ModelRequest
from agentx_evolve.adapters.model_response import ModelResponse


class ModelAdapter(ABC):
    @abstractmethod
    def describe_capabilities(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def validate_request(self, request: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def normalize_response(self, response: dict[str, Any]) -> dict[str, Any]:
        ...
