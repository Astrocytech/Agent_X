from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.governance_engine import run_governance_checks
from agentx_initiator.core.evolution_model import (
    EvolutionPlan, EvolutionManifest, EvolutionAudit,
)
from agentx_initiator.core.evolution_rules import build_default_steps


def generate_evolution_plan(
    architecture_report: dict | None = None,
    repository_scan_summary: dict | None = None,
    governance_decision: dict | None = None,
    risk_assessment: dict | None = None,
    validation_report: dict | None = None,
) -> EvolutionPlan:
    plan_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    steps = build_default_steps(architecture_report, validation_report, governance_decision)
    manifest = EvolutionManifest(
        manifest_id=f"manifest-{plan_id}",
        plan_id=plan_id,
        step_count=len(steps),
        completed_count=0,
        total_dependencies=0,
        created_at=now,
        updated_at=now,
    )

    return EvolutionPlan(
        plan_id=plan_id,
        timestamp=now,
        source_component="EvolutionPlanner",
        status="DRAFT",
        steps=steps,
        manifest=manifest.to_dict(),
    )


def generate_evolution_audit(plan_id: str, event_type: str, status: str = "INITIATED") -> EvolutionAudit:
    return EvolutionAudit(
        audit_id=str(uuid4()),
        event_type=event_type,
        plan_id=plan_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_component="EvolutionPlanner",
        status=status,
    )


# --- backward compat ---
_LEGACY_RECOMMENDATIONS = [
    {"priority": 10, "category": "fic", "action": "Create unit-level FIC contracts under L1/fic/", "detail": "Root governance documents exist; implement UNIT-001 through UNIT-014"},
    {"priority": 20, "category": "validation", "action": "Implement validators for L1 governance", "detail": "Bootstrap formal validators for FIC contracts, schemas, and digests"},
    {"priority": 30, "category": "specialization", "action": "Select and develop L2 profile for implementation", "detail": "Most likely first candidate: L2-PROFILE-SR-001 Symbolic Regression Controller"},
]


def generate_plan() -> list[dict]:
    scan = scan_repo()
    checks = run_governance_checks()
    failed = [c for c in checks if not c["passed"]]
    recommendations = []

    if failed:
        recommendations.append({
            "priority": 1,
            "category": "governance",
            "action": "Resolve governance check failures",
            "detail": f"{len(failed)} checks failed: {[c['check'] for c in failed]}",
        })

    if scan.total_files == 0:
        recommendations.append({
            "priority": 2,
            "category": "structure",
            "action": "Investigate empty repository scan",
            "detail": "No files found during scan",
        })

    recommendations.extend(_LEGACY_RECOMMENDATIONS)
    return recommendations
