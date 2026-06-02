from __future__ import annotations
from agentx_initiator.core.patch_proposal_model import (
    PatchSpec, PatchAction, PatchContext, PatchManifest,
    PatchAudit, PatchValidation, ACTION_TYPES, PATCH_PRIORITIES,
)
from agentx_initiator.core.risk_model import SEVERITIES


def build_default_actions(task: str) -> list[dict]:
    actions: list[PatchAction] = []
    task_lower = task.lower()

    if "read" in task_lower or "inspect" in task_lower or "scan" in task_lower:
        actions.append(PatchAction(
            action_id="act-read-001",
            action_type="NOOP",
            target_path="L1/*",
            description="Read-only inspection — no mutation needed",
            priority="P0",
        ))
    elif "schema" in task_lower or "validate" in task_lower:
        actions.append(PatchAction(
            action_id="act-validate-001",
            action_type="CREATE",
            target_path="L1/schemas/",
            description="Create or update schema validation",
            priority="P1",
        ))
    elif "test" in task_lower:
        actions.append(PatchAction(
            action_id="act-test-001",
            action_type="CREATE",
            target_path="L1/tests/",
            description="Add unit tests",
            priority="P1",
        ))
    elif "fic" in task_lower or "contract" in task_lower:
        actions.append(PatchAction(
            action_id="act-fic-001",
            action_type="CREATE",
            target_path="L1/fic/",
            description="Create FIC contract documents",
            priority="P1",
        ))
    else:
        actions.append(PatchAction(
            action_id="act-default-001",
            action_type="REFACTOR",
            target_path="L1/",
            description="General refactor for task",
            priority="P2",
        ))

    return [a.to_dict() for a in actions]


def compute_proposal_status(actions: list[dict]) -> str:
    if not actions:
        return "DRAFT"
    return "REVIEW"
