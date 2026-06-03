from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    LearningAdapterResult, utc_now_iso,
    DEPENDENCY_AVAILABLE, DEPENDENCY_MISSING, DEPENDENCY_BLOCKED,
)


def build_memory_write_request(candidate: dict, context: dict) -> dict:
    memory_available = context.get("memory_layer_available", False)
    approval_present = context.get("human_approval_id") is not None
    if not memory_available:
        return LearningAdapterResult(
            adapter_name="memory_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_MISSING,
            status="BLOCKED",
            summary="Memory layer unavailable, cannot build write request",
            data={},
            errors=["Memory layer unavailable"],
        ).to_dict()
    if not approval_present:
        return LearningAdapterResult(
            adapter_name="memory_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="NEEDS_APPROVAL",
            summary="Memory write request requires human approval",
            data={"candidate": candidate, "requires_approval": True},
            warnings=["Human approval required before memory write"],
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="memory_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_AVAILABLE,
        status="READY",
        summary="Memory write request ready",
        data={"candidate": candidate, "ready": True},
    ).to_dict()


def check_memory_write_ready(candidate: dict, context: dict) -> dict:
    memory_available = context.get("memory_layer_available", False)
    if not memory_available:
        return LearningAdapterResult(
            adapter_name="memory_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_BLOCKED,
            status="BLOCKED",
            summary="Memory layer unavailable",
            data={"ready": False},
            errors=["Memory layer unavailable"],
        ).to_dict()
    approval_present = context.get("human_approval_id") is not None
    if not approval_present:
        return LearningAdapterResult(
            adapter_name="memory_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="NEEDS_APPROVAL",
            summary="Memory write not ready: needs human approval",
            data={"ready": False, "needs_approval": True},
            warnings=["Human approval required"],
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="memory_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_AVAILABLE,
        status="READY",
        summary="Memory write ready",
        data={"ready": True},
    ).to_dict()
