from __future__ import annotations

from typing import Any

from agentx_evolve.human_review.review_api import ReviewAPI

__all__ = [
    "MCPReviewAdapter",
]


class MCPReviewAdapter:
    def __init__(self, api: ReviewAPI | None = None) -> None:
        self._api = api or ReviewAPI()

    def handle_submit_request(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._api.submit_request(
            action=params.get("action", ""),
            reason=params.get("reason", ""),
            metadata=params.get("metadata"),
        )

    def handle_get_decision(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._api.get_decision(request_id=params.get("request_id", ""))

    def handle_list_pending(self, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self._api.list_pending()
