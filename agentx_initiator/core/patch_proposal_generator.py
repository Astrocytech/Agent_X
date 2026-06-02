from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel
from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.governance_engine import run_governance_checks
from agentx_initiator.core.risk_engine import classify_risk, is_action_allowed
from agentx_initiator.core.config import load_config
from agentx_initiator.core.patch_proposal_model import (
    PatchSpec, PatchManifest, PatchAudit,
)
from agentx_initiator.core.patch_proposal_rules import (
    build_default_actions, compute_proposal_status,
)


def generate_patch_proposal(
    task: str,
    governance_decision: dict | None = None,
    risk_assessment: dict | None = None,
    evolution_plan: dict | None = None,
) -> PatchSpec:
    spec_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    actions = build_default_actions(task)
    status = compute_proposal_status(actions)

    manifest = PatchManifest(
        manifest_id=f"manifest-{spec_id}",
        proposal_id=spec_id,
        action_count=len(actions),
        applied_count=0,
        total_dependencies=0,
        created_at=now,
        updated_at=now,
    )

    return PatchSpec(
        spec_id=spec_id,
        proposal_id=spec_id,
        title=f"Patch proposal for: {task[:60]}",
        task=task,
        risk_level="MEDIUM",
        description=f"Non-mutating patch proposal for: {task}",
        actions=actions,
        manifest=manifest.to_dict(),
    )


def generate_patch_audit(proposal_id: str, event_type: str, status: str = "INITIATED") -> PatchAudit:
    return PatchAudit(
        audit_id=str(uuid4()),
        event_type=event_type,
        proposal_id=proposal_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_component="PatchProposalGenerator",
        status=status,
    )


# --- backward compat ---
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
