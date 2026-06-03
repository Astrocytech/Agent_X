import json
from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceDeviation, SEVERITY_BLOCKER
from .artifact_writer import write_json_artifact


def load_deviation_register(repo_root: Path) -> list[FinalAcceptanceDeviation]:
    path = repo_root / ".agentx-init" / "final_acceptance" / "final_acceptance_deviation_register.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [FinalAcceptanceDeviation(**item) for item in data.get("deviations", [])]
    except (json.JSONDecodeError, OSError):
        return []


def validate_deviation_register(deviations: list[FinalAcceptanceDeviation]) -> list[str]:
    errors: list[str] = []
    for dev in deviations:
        if dev.safety_impact == "critical":
            errors.append(
                f"Deviation {dev.deviation_id}: critical safety impact cannot be accepted"
            )
        if dev.safety_impact == "high" and dev.accepted_status not in ("NOT_APPLICABLE", "DEFERRED_SAFELY"):
            errors.append(
                f"Deviation {dev.deviation_id}: high safety impact requires NOT_APPLICABLE or DEFERRED_SAFELY"
            )
    return errors


def write_deviation_register(
    deviations: list[FinalAcceptanceDeviation], repo_root: Path,
) -> Path:
    data: dict[str, Any] = {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_deviation.schema.json",
        "source_component": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "deviations": [
            {
                "deviation_id": d.deviation_id,
                "area": d.area,
                "layer_id": d.layer_id,
                "description": d.description,
                "reason": d.reason,
                "safety_impact": d.safety_impact,
                "compensating_control": d.compensating_control,
                "accepted_status": d.accepted_status,
                "reviewer_decision": d.reviewer_decision,
                "evidence_refs": d.evidence_refs,
                "warnings": d.warnings,
                "errors": d.errors,
            }
            for d in deviations
        ],
        "warnings": [],
        "errors": [],
    }
    return write_json_artifact(repo_root, "final_acceptance_deviation_register.json", data)
