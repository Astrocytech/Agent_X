from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    LearningAdapterResult, utc_now_iso,
    DEPENDENCY_AVAILABLE, DEPENDENCY_MISSING,
)


def load_monitoring_observations(context: dict) -> dict:
    monitoring_data = context.get("monitoring_observations")
    if monitoring_data:
        return LearningAdapterResult(
            adapter_name="monitoring_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="AVAILABLE",
            summary="Monitoring observations loaded from context",
            data=monitoring_data,
            evidence_refs=context.get("monitoring_evidence_refs", []),
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="monitoring_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_MISSING,
        status="MISSING",
        summary="No monitoring observations available",
        data={},
        warnings=["Monitoring/Observability not available"],
    ).to_dict()


def detect_runtime_degradation(observations: dict) -> dict:
    if not observations:
        return {"degradation_detected": False, "details": "no observations"}
    return {
        "degradation_detected": observations.get("degradation_detected", False),
        "details": observations.get("details", ""),
        "affected_components": observations.get("affected_components", []),
    }
