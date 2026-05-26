from pydantic import BaseModel
from datetime import datetime
from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.governance_engine import run_governance_checks
from agentx_initiator.core.risk_engine import classify_risk, is_action_allowed
from agentx_initiator.core.config import load_config


class PatchProposal(BaseModel):
    proposal_id: str
    title: str
    task: str
    risk_level: str
    allowed: bool
    reason: str
    affected_layers: list[str]
    affected_files: list[str]
    description: str
    non_mutating: bool
    generated_at: str


def generate_proposal(task: str) -> PatchProposal:
    config = load_config()
    scan = scan_repo()
    checks = run_governance_checks()
    risk = classify_risk(task)
    allowed, reason = is_action_allowed(task, config)

    affected_layers = []
    for layer in scan.layers:
        if layer.layer in task:
            affected_layers.append(layer.layer)
    if not affected_layers:
        affected_layers = list(set(
            f"L{word[1]}" for word in task.split()
            if word.startswith("L") and len(word) >= 2 and word[1].isdigit()
        ))
    if not affected_layers:
        affected_layers = ["L1"]

    return PatchProposal(
        proposal_id=f"PP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        title=f"Proposal: {task[:60]}",
        task=task,
        risk_level=risk,
        allowed=allowed,
        reason=reason,
        affected_layers=affected_layers,
        affected_files=[str(l.path) for l in scan.layers[:3]],
        description=f"Human-reviewable non-mutating proposal for: {task}",
        non_mutating=True,
        generated_at=datetime.now().isoformat(),
    )
