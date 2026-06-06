from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    LearningAdapterResult, utc_now_iso,
    DEPENDENCY_AVAILABLE, DEPENDENCY_MISSING,
)


def check_durable_learning_allowed(candidate: dict, context: dict) -> dict:
    policy_data = context.get("policy_registry_decision")
    if policy_data:
        return LearningAdapterResult(
            adapter_name="policy_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="CHECKED",
            summary=f"Policy decision: {policy_data.get('decision', 'UNKNOWN')}",
            data=policy_data,
            evidence_refs=context.get("policy_evidence_refs", []),
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="policy_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_MISSING,
        status="BLOCKED",
        summary="Policy registry unavailable, durable learning blocked",
        data={"decision": "BLOCKED"},
        errors=["Policy/Capability Registry unavailable"],
    ).to_dict()


def check_follow_up_task_allowed(proposal: dict, context: dict) -> dict:
    policy_data = context.get("policy_registry_decision")
    if policy_data:
        allowed = policy_data.get("follow_up_tasks_allowed", True)
        return LearningAdapterResult(
            adapter_name="policy_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="ALLOWED" if allowed else "BLOCKED",
            summary="Follow-up tasks allowed" if allowed else "Follow-up tasks blocked",
            data={"allowed": allowed},
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="policy_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_MISSING,
        status="BLOCKED",
        summary="Policy registry unavailable, follow-up tasks blocked",
        data={"allowed": False},
        errors=["Policy/Capability Registry unavailable"],
    ).to_dict()


def check_report_write_allowed(report: dict, context: dict) -> dict:
    policy_data = context.get("policy_registry_decision")
    if policy_data:
        allowed = policy_data.get("report_write_allowed", True)
        return LearningAdapterResult(
            adapter_name="policy_adapter",
            created_at=utc_now_iso(),
            dependency_status=DEPENDENCY_AVAILABLE,
            status="ALLOWED" if allowed else "BLOCKED",
            summary="Report write allowed" if allowed else "Report write blocked",
            data={"allowed": allowed},
        ).to_dict()
    return LearningAdapterResult(
        adapter_name="policy_adapter",
        created_at=utc_now_iso(),
        dependency_status=DEPENDENCY_MISSING,
        status="ALLOWED",
        summary="Policy registry unavailable, report write allowed in restricted mode",
        data={"allowed": True},
        warnings=["Report write allowed in restricted mode"],
    ).to_dict()
