from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    LearningAdapterResult, utc_now_iso, new_id,
    DEPENDENCY_AVAILABLE, DEPENDENCY_MISSING, DEPENDENCY_CONTEXT_PROVIDED,
)


def load_evaluation_summary(context: dict) -> dict:
    eval_data = context.get("evaluation_summary")
    if eval_data:
        return LearningAdapterResult(
            adapter_name="evaluation_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="AVAILABLE",
            summary="Evaluation summary loaded from context",
            data=eval_data,
            evidence_refs=context.get("evaluation_evidence_refs", []),
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="evaluation_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_MISSING,
        status="MISSING",
        summary="No evaluation summary available",
        data={},
        warnings=["Evaluation Harness not available"],
    ).to_dict()


def has_passing_validation(evaluation_summary: dict) -> bool:
    return evaluation_summary.get("validation_passed", False) if evaluation_summary else False


def has_regression(evaluation_summary: dict) -> bool:
    return evaluation_summary.get("regression_detected", False) if evaluation_summary else False
