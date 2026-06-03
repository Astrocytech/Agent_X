from __future__ import annotations

from typing import Any

from agentx_evolve.human_review.review_models import (
    HumanReviewRequest,
    new_id,
    utc_now_iso,
)

__all__ = [
    "ReviewAPI",
]


class ReviewAPI:
    def __init__(self) -> None:
        self._pending: dict[str, HumanReviewRequest] = {}
        self._decisions: dict[str, dict[str, Any]] = {}

    def submit_request(
        self,
        action: str,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        request = HumanReviewRequest(
            request_id=new_id("req"),
            created_at=utc_now_iso(),
            requested_action=action,
            reason=reason,
        )
        self._pending[request.request_id] = request
        return request.to_dict()

    def get_decision(self, request_id: str) -> dict[str, Any]:
        decision = self._decisions.get(request_id)
        if decision is None:
            return {"request_id": request_id, "decision": None, "error": "No decision found"}
        return {"request_id": request_id, **decision}

    def list_pending(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self._pending.values()]
