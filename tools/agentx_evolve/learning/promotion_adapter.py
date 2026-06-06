from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    LearningAdapterResult, utc_now_iso,
    DEPENDENCY_AVAILABLE, DEPENDENCY_MISSING,
)


def load_promotion_decision(context: dict) -> dict:
    promo_data = context.get("promotion_decision")
    if promo_data:
        return LearningAdapterResult(
            adapter_name="promotion_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="AVAILABLE",
            summary="Promotion decision loaded from context",
            data=promo_data,
            evidence_refs=context.get("promotion_evidence_refs", []),
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="promotion_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_MISSING,
        status="MISSING",
        summary="No promotion decision available",
        data={},
        warnings=["Promotion Gate not available"],
    ).to_dict()


def promotion_allows_learning(promotion_decision: dict) -> bool:
    return promotion_decision.get("allows_learning", False) if promotion_decision else False


def promotion_rejected(promotion_decision: dict) -> bool:
    return promotion_decision.get("rejected", False) if promotion_decision else False
