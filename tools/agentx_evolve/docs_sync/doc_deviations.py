from pathlib import Path

from .doc_models import (
    DocumentationSyncDeviation,
    DEVIATION_ACCEPTED_STATUS_NOT_APPLICABLE,
    DEVIATION_ACCEPTED_STATUS_DEFERRED_SAFELY,
    DEVIATION_ACCEPTED_STATUS_NON_BLOCKING_FOLLOWUP,
    DEVIATION_ACCEPTED_STATUS_REJECTED,
    new_id,
    utc_now_iso,
    to_dict,
)

ACCEPTED_STATUSES = frozenset({
    DEVIATION_ACCEPTED_STATUS_NOT_APPLICABLE,
    DEVIATION_ACCEPTED_STATUS_DEFERRED_SAFELY,
    DEVIATION_ACCEPTED_STATUS_NON_BLOCKING_FOLLOWUP,
    DEVIATION_ACCEPTED_STATUS_REJECTED,
})

BLOCKER_DEVIATION_PATTERNS = [
    "BLOCKER finding cannot be accepted as deviation",
    "manual governed document overwrite cannot be accepted as deviation",
    "missing evidence hashes cannot be accepted for DONE",
    "broken generated-index links cannot be accepted for DONE",
]


def create_docs_sync_deviation(
    area: str,
    description: str,
    reason: str,
    safety_impact: str = "",
    compensating_control: str = "",
    accepted_status: str = DEVIATION_ACCEPTED_STATUS_NOT_APPLICABLE,
    reviewer_decision: str = "",
) -> dict:
    if accepted_status not in ACCEPTED_STATUSES:
        return {
            "status": "INVALID",
            "errors": [f"invalid accepted_status: {accepted_status}"],
        }

    deviation = DocumentationSyncDeviation(
        deviation_id=new_id("dev"),
        created_at=utc_now_iso(),
        area=area,
        description=description,
        reason=reason,
        safety_impact=safety_impact,
        compensating_control=compensating_control,
        accepted_status=accepted_status,
        reviewer_decision=reviewer_decision,
    )

    return to_dict(deviation)


def validate_docs_sync_deviation(deviation: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []

    for pattern in BLOCKER_DEVIATION_PATTERNS:
        if pattern in deviation.get("reason", "") or pattern in deviation.get("description", ""):
            errors.append(f"blocker pattern found: {pattern}")

    return len(errors) == 0, errors


def write_docs_sync_deviation_register(
    repo_root: Path,
    deviations: list[dict],
) -> dict:
    import json
    out_dir = repo_root / ".agentx-init" / "docs_sync"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "documentation_sync_deviation_register.json"
    data = {
        "schema_version": "1.0",
        "schema_id": "documentation_sync_deviation.schema.json",
        "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        "created_at": utc_now_iso(),
        "deviations": deviations,
    }
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.replace(path)
    return {"path": str(path), "status": "written"}
