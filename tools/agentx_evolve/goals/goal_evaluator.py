from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.orchestrator.functional_orchestrator import MvpOrchestrationResult


@dataclass
class MvpGoalResult:
    goal_id: str = ""
    run_id: str = ""
    verdict: str = "UNKNOWN"
    success_criteria: list[str] = field(default_factory=list)
    failure_criteria: list[str] = field(default_factory=list)
    observed_results: list[str] = field(default_factory=list)
    test_results: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    is_complete: bool = False
    action_status: str = ""
    phase: str = ""


class MvpGoalEvaluator:
    def __init__(self, state_store: Any = None, evidence_bridge: Any = None) -> None:
        self._state_store = state_store
        self._evidence_bridge = evidence_bridge

    def evaluate(self, goal_id: str, run_id: str, orchestration_result: dict) -> MvpGoalResult:
        success_criteria = orchestration_result.get("success_criteria", [])
        failure_criteria = orchestration_result.get("failure_criteria", [])
        observed_results = orchestration_result.get("observed_results", [])
        test_results = orchestration_result.get("test_results", [])
        evidence_refs = orchestration_result.get("evidence_refs", [])
        errors: list[str] = []

        for criterion in success_criteria:
            if criterion not in observed_results:
                errors.append(f"Success criterion not met: {criterion}")

        for criterion in failure_criteria:
            if criterion in observed_results:
                errors.append(f"Failure criterion triggered: {criterion}")

        all_success_met = all(c in observed_results for c in success_criteria)
        no_failure_triggered = not any(c in observed_results for c in failure_criteria)
        evidence_exists = len(evidence_refs) > 0
        all_tests_passed = all(r == "PASS" for r in test_results)

        verdict = "PASS" if all_success_met and no_failure_triggered and evidence_exists and all_tests_passed else "FAIL"
        is_complete = verdict == "PASS"

        return MvpGoalResult(
            goal_id=goal_id,
            run_id=run_id,
            verdict=verdict,
            success_criteria=success_criteria,
            failure_criteria=failure_criteria,
            observed_results=observed_results,
            test_results=test_results,
            errors=errors,
            evidence_refs=evidence_refs,
            is_complete=is_complete,
        )

    def from_orchestration_result(
        self,
        goal_id: str,
        run_id: str,
        result: MvpOrchestrationResult,
        success_criteria: list[str] | None = None,
        failure_criteria: list[str] | None = None,
    ) -> MvpGoalResult:
        errors: list[str] = list(result.errors)
        sc = success_criteria or []
        fc = failure_criteria or []

        observed = []
        for art in result.artifacts:
            path = art.get("path", "")
            if path:
                observed.append(f"artifact_created:{path}")
        for ev in result.events:
            et = ev.get("event_type", "")
            if et:
                observed.append(f"event:{et}")

        test_results_list = []
        test_verdict = result.verdict
        if test_verdict == "PASS":
            test_results_list.append("PASS")
        elif test_verdict in ("FAILED", "VALIDATION_FAILED", "SIMULATION_FAILED",
                             "GATE_DENIED_SIMULATE", "GATE_DENIED_EVALUATE", "GATE_DENIED_AUDIT"):
            test_results_list.append("FAIL")

        evidence_ids = []
        for ref in result.evidence_refs:
            if isinstance(ref, dict):
                eid = ref.get("id", ref.get("gate", ""))
                if eid:
                    evidence_ids.append(eid)
            elif isinstance(ref, str):
                evidence_ids.append(ref)

        for criterion in sc:
            if criterion not in observed:
                errors.append(f"Success criterion not met: {criterion}")

        for criterion in fc:
            if criterion in observed:
                errors.append(f"Failure criterion triggered: {criterion}")

        all_success_met = all(c in observed for c in sc)
        no_failure_triggered = not any(c in observed for c in fc)
        evidence_exists = len(evidence_ids) > 0
        all_tests_passed = all(r == "PASS" for r in test_results_list)

        verdict = "PASS" if all_success_met and no_failure_triggered and evidence_exists and all_tests_passed else "FAIL"
        is_complete = verdict == "PASS"

        return MvpGoalResult(
            goal_id=goal_id,
            run_id=run_id,
            verdict=verdict,
            success_criteria=sc,
            failure_criteria=fc,
            observed_results=observed,
            test_results=test_results_list,
            errors=errors,
            evidence_refs=evidence_ids,
            is_complete=is_complete,
            action_status=result.action_status,
            phase="orchestration",
        )

    def can_mark_complete(self, result: MvpGoalResult) -> bool:
        if not result.observed_results:
            return False
        if any(r != "PASS" for r in result.test_results):
            return False
        if not result.evidence_refs:
            return False
        return result.is_complete
