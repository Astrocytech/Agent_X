from __future__ import annotations

from typing import Any

__all__ = [
    "ModelClient",
]


class ModelClient:
    def invoke_model(self, prompt: str, model: str) -> dict[str, Any]:
        return {
            "model": model,
            "prompt_length": len(prompt),
            "response": "",
            "status": "simulated",
        }
