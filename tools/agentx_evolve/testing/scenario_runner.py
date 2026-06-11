from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class MvpScenario:
    name: str = ""
    goal: str = ""
    profile_id: str = ""
    expected_result: str = ""
    steps: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "goal": self.goal,
            "profile_id": self.profile_id,
            "expected_result": self.expected_result,
            "steps": list(self.steps),
        }


@dataclass
class MvpScenarioResult:
    scenario_name: str = ""
    passed: bool = False
    final_verdict: str = ""
    errors: list[str] = field(default_factory=list)
    evidence_refs: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "passed": self.passed,
            "final_verdict": self.final_verdict,
            "errors": list(self.errors),
            "evidence_refs": list(self.evidence_refs),
        }


class MvpScenarioRunner:
    def __init__(self, orchestrator_fn: Callable | None = None) -> None:
        self._orchestrator_fn = orchestrator_fn
        self._results: list[MvpScenarioResult] = []

    def run_scenario(self, scenario: MvpScenario, context: dict[str, Any]) -> MvpScenarioResult:
        if self._orchestrator_fn:
            result = self._orchestrator_fn(scenario, context)
            sr = MvpScenarioResult(
                scenario_name=scenario.name,
                passed=result.get("verdict", "") == scenario.expected_result,
                final_verdict=result.get("verdict", "UNKNOWN"),
                errors=result.get("errors", []),
                evidence_refs=result.get("evidence_refs", []),
            )
        else:
            sr = MvpScenarioResult(
                scenario_name=scenario.name,
                passed=False,
                final_verdict="NOT_RUN",
                errors=["No orchestrator function provided"],
            )
        self._results.append(sr)
        return sr

    def all_passed(self) -> bool:
        return all(r.passed for r in self._results)

    @property
    def results(self) -> list[MvpScenarioResult]:
        return list(self._results)
