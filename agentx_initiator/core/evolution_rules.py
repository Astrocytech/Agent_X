from __future__ import annotations
from agentx_initiator.core.evolution_model import (
    EvolutionPlan, EvolutionStep, EvolutionDependency, EvolutionManifest,
    EvolutionAudit, CATEGORIES, PRIORITIES,
)


def build_default_steps(architecture_report: dict | None, validation_report: dict | None, governance_decision: dict | None) -> list[dict]:
    steps: list[EvolutionStep] = []

    # P0: governance failures first
    if governance_decision and governance_decision.get("decision") == "BLOCK":
        steps.append(EvolutionStep(
            step_id="step-governance-001",
            priority="P0",
            category="GOVERNANCE",
            action="Resolve governance block",
            detail="Governance check blocked; resolve violations before proceeding",
            status="BLOCKED",
        ))

    # P0: schema or validation failures
    if validation_report and validation_report.get("status") == "FAIL":
        steps.append(EvolutionStep(
            step_id="step-validation-001",
            priority="P0",
            category="VALIDATION",
            action="Fix validation failures",
            detail=f"{len(validation_report.get('failures', []))} validation failures found",
        ))

    # P1: architecture gaps
    arch = architecture_report or {}
    missing = arch.get("missing_components", [])
    if missing:
        steps.append(EvolutionStep(
            step_id="step-arch-001",
            priority="P1",
            category="STRUCTURE",
            action="Fill architecture gaps",
            detail=f"Missing components: {', '.join(missing)}",
        ))

    # P1: testing gaps
    steps.append(EvolutionStep(
        step_id="step-testing-001",
        priority="P1",
        category="TESTING",
        action="Increase test coverage",
        detail="Add unit tests for untested components",
    ))

    # P2: schemas
    steps.append(EvolutionStep(
        step_id="step-schemas-001",
        priority="P2",
        category="SCHEMA",
        action="Validate all schemas",
        detail="Ensure every artifact has a corresponding schema",
    ))

    # P2: FIC contracts
    steps.append(EvolutionStep(
        step_id="step-fic-001",
        priority="P2",
        category="GOVERNANCE",
        action="Create FIC contracts",
        detail="Implement UNIT-001 through UNIT-014 under L1/fic/",
    ))

    # P3: specialization profiles
    steps.append(EvolutionStep(
        step_id="step-profile-001",
        priority="P3",
        category="SPECIALIZATION",
        action="Select and develop L2 profile",
        detail="Most likely candidate: L2-PROFILE-SR-001 Symbolic Regression Controller",
    ))

    return [s.to_dict() for s in steps]
