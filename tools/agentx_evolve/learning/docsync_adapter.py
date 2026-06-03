from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    LearningAdapterResult, utc_now_iso,
    DEPENDENCY_AVAILABLE, DEPENDENCY_MISSING,
)


def load_docsync_evidence(context: dict) -> dict:
    docsync_data = context.get("docsync_evidence")
    if docsync_data:
        return LearningAdapterResult(
            adapter_name="docsync_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="AVAILABLE",
            summary="Documentation sync evidence loaded from context",
            data=docsync_data,
            evidence_refs=context.get("docsync_evidence_refs", []),
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="docsync_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_MISSING,
        status="MISSING",
        summary="No documentation sync evidence available",
        data={},
        warnings=["Documentation Sync not available"],
    ).to_dict()


def detect_documentation_drift(docsync_evidence: dict) -> dict:
    if not docsync_evidence:
        return {"drift_detected": False, "details": "no evidence"}
    return {
        "drift_detected": docsync_evidence.get("drift_detected", False),
        "details": docsync_evidence.get("details", ""),
        "affected_paths": docsync_evidence.get("affected_paths", []),
    }
