from __future__ import annotations

import logging

from agentx_evolve.human_review.review_cli import (
    run_review_cli,
    parse_review_decision,
)

logger = logging.getLogger(__name__)

__all__ = [
    "run_review_cli",
    "parse_review_decision",
    "HumanReviewCLI",
]


class HumanReviewCLI:
    def __init__(self, reviewer_id: str = ""):
        self.reviewer_id = reviewer_id
        self.logger = logger

    def run(self, request_id: str, context: dict | None = None) -> dict:
        return run_review_cli(request_id, self.reviewer_id, context or {})

    def parse_decision(self, raw: str) -> str:
        return parse_review_decision(raw)
