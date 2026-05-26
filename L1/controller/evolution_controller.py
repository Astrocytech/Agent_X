from __future__ import annotations

import dataclasses
import typing as _typing

from L1.controller.goal_classifier import (
    GoalRecord,
    classify_goal_text,
)
from L1.controller.unit_planner import (
    UnitPlan,
    plan_from_goal,
)
from L1.controller.fic_generator import (
    FicTemplate,
    generate_fics,
)
from L1.controller.fic_validator import (
    FicValidationResult,
    validate_fics,
)
from L1.controller.handoff_packet_builder import (
    HandoffPacket,
    build_handoff_packets,
)
from L1.controller.proof_check_runner import (
    ProofCheckResult,
    run_proof_checks,
)
from L1.controller.evidence_collector import (
    EvidenceBundle,
    collect_evidence,
)
from L1.controller.completion_record_writer import (
    CompletionRecord,
    write_completion_record,
)
from L1.controller.traceability_updater import (
    TraceabilityGraph,
    build_traceability_graph,
)
from L1.controller.failure_learning_updater import (
    FailureRecord,
    process_failures,
)
from L1.controller.boundary_checker import (
    BoundaryCheckResult,
    check_boundaries,
)

__all__ = [
    "EvolutionResult",
    "EvolutionController",
    "EvolutionControllerError",
    "run_evolution",
]


@dataclasses.dataclass(frozen=True)
class EvolutionResult:
    goal_record: GoalRecord
    unit_plan: UnitPlan
    fic_templates: tuple[FicTemplate, ...]
    validation_result: FicValidationResult
    handoff_packets: tuple[HandoffPacket, ...]
    proof_result: ProofCheckResult
    evidence_bundle: EvidenceBundle
    completion_record: CompletionRecord
    traceability_graph: TraceabilityGraph
    failure_records: tuple[FailureRecord, ...]
    boundary_result: BoundaryCheckResult
    success: bool


class EvolutionControllerError(Exception):
    pass


class EvolutionController:
    def evolve(
        self,
        goal_text: str,
        changed_files: tuple[str, ...],
    ) -> EvolutionResult:
        if not isinstance(goal_text, str):
            raise EvolutionControllerError("goal_text must be a string")
        if not isinstance(changed_files, tuple):
            raise EvolutionControllerError("changed_files must be a tuple")

        goal_record: object = classify_goal_text(goal_text)
        unit_plan: object = plan_from_goal(goal_record)
        templates: object = generate_fics(unit_plan)
        validation_result: object = validate_fics(templates)
        handoff_packets: object = build_handoff_packets(templates, unit_plan)
        proof_result: object = run_proof_checks()
        evidence_bundle: object = collect_evidence(proof_result)
        completion_record = write_completion_record(
            "UNIT-L1-EVOLVE",
            f"Evolution for: {goal_text}",
            evidence_bundle,
        )
        traceability_graph = build_traceability_graph(
            (completion_record,),
            handoff_packets,
        )
        failure_records = process_failures(proof_result)
        boundary_result = check_boundaries(changed_files)

        ok = (
            validation_result.is_valid
            and proof_result.all_passed
            and boundary_result.all_passed
        )

        return EvolutionResult(
            goal_record=goal_record,
            unit_plan=unit_plan,
            fic_templates=templates,
            validation_result=validation_result,
            handoff_packets=handoff_packets,
            proof_result=proof_result,
            evidence_bundle=evidence_bundle,
            completion_record=completion_record,
            traceability_graph=traceability_graph,
            failure_records=failure_records,
            boundary_result=boundary_result,
            success=ok,
        )


def run_evolution(
    goal_text: str,
    changed_files: tuple[str, ...],
) -> EvolutionResult:
    return EvolutionController().evolve(goal_text, changed_files)
