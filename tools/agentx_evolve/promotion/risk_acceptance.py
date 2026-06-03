from __future__ import annotations
from pathlib import Path
from agentx_evolve.models.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    RiskAcceptance, ReleaseCandidate, canonical_json, sha256_dict,
    from_dict, to_dict, write_json_atomic,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


def load_risk_acceptance(path: Path) -> RiskAcceptance | None:
    if not path.exists():
        return None
    import json
    data = json.loads(path.read_text())
    return from_dict(RiskAcceptance, data)


def validate_risk_acceptance(
    risk_acceptance: RiskAcceptance,
    candidate: ReleaseCandidate,
) -> list[str]:
    errors: list[str] = []
    if risk_acceptance.schema_id != "promotion_risk_acceptance.schema.json":
        errors.append(f"schema_id mismatch: {risk_acceptance.schema_id}")
    if risk_acceptance.candidate_id != candidate.candidate_id:
        errors.append(
            f"candidate_id mismatch: {risk_acceptance.candidate_id} != {candidate.candidate_id}"
        )
    if not risk_acceptance.risk_acceptance_hash:
        errors.append("risk_acceptance_hash is empty")
    return errors


def has_blocking_risks(risk_acceptance: RiskAcceptance) -> bool:
    return len(risk_acceptance.blocking_risks) > 0


def has_unaccepted_required_risks(risk_acceptance: RiskAcceptance) -> bool:
    for risk in risk_acceptance.risks:
        risk_id = risk.get("risk_id", risk.get("id", ""))
        if risk.get("required", False) and risk_id not in risk_acceptance.accepted_risks:
            return True
    return False


def write_risk_acceptance(risk_acceptance: RiskAcceptance, repo_root: Path) -> Path:
    path = promotion_runs_dir(repo_root) / "risk_acceptance.json"
    return write_json_atomic(path, to_dict(risk_acceptance))


def compute_risk_acceptance_hash(risk_acceptance: RiskAcceptance) -> str:
    payload: dict = {
        "component_id": risk_acceptance.component_id,
        "candidate_id": risk_acceptance.candidate_id,
        "risks": sorted(
            [canonical_json(r) for r in risk_acceptance.risks]
        ) if risk_acceptance.risks else [],
        "accepted_risks": sorted(risk_acceptance.accepted_risks),
        "blocking_risks": sorted(risk_acceptance.blocking_risks),
        "accepted_by": risk_acceptance.accepted_by,
    }
    return sha256_dict(payload)
