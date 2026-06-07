from __future__ import annotations
from typing import Any

MOCK_RESPONSE_CATALOG: dict[str, dict[str, Any]] = {
    "Say READY": {
        "role": "assistant",
        "content": "READY — deterministic Agent_X mock provider response.",
        "tool_calls": [],
        "finish_reason": "stop",
    },
}


class MockProvider:
    def __init__(self, model: str = "mock/deterministic"):
        self.model = model

    def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        user_msg = self._last_user_message(messages)
        return self._lookup_response(user_msg)

    def complete_structured(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        return {
            "schema_version": "agentx.structured_plan.v1",
            "summary": "mock plan for testing",
            "actions": [
                {
                    "type": "noop",
                    "description": "mock safe action",
                    "target": "",
                    "safety_notes": ["mock safety pass"],
                }
            ],
            "patches": [],
            "validation_commands": ["python -m compileall tools/agentx_evolve"],
        }

    @staticmethod
    def _last_user_message(messages: list[dict[str, Any]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""

    def _lookup_response(self, message: str) -> dict[str, Any]:
        for key, response in MOCK_RESPONSE_CATALOG.items():
            if key in message:
                return dict(response)
        return {
            "role": "assistant",
            "content": f"Mock response to: {message[:80]}",
            "tool_calls": [],
            "finish_reason": "stop",
        }
