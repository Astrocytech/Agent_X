from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from agentx_evolve.orchestrator.functional_orchestrator import (
    MvpFunctionalOrchestrator,
    MvpOrchestrationResult,
)


@dataclass
class MvpAttackCase:
    attack_id: str = ""
    name: str = ""
    description: str = ""
    expected_result: str = ""
    attack_fn: Callable[[], dict[str, Any]] = field(default=lambda: {})


@dataclass
class MvpAttackResult:
    attack_id: str = ""
    name: str = ""
    blocked: bool = False
    actual_result: str = ""
    details: str = ""
    passed: bool = False


class MvpAdversarialEngine:
    def __init__(
        self,
        attack_suite: list[MvpAttackCase] | None = None,
        orchestrator: MvpFunctionalOrchestrator | None = None,
    ) -> None:
        self._attacks: list[MvpAttackCase] = list(attack_suite) if attack_suite else []
        self._orchestrator = orchestrator or MvpFunctionalOrchestrator()

    def register_attack(self, attack: MvpAttackCase) -> None:
        self._attacks.append(attack)

    def run_all(self) -> list[MvpAttackResult]:
        return [self._run_single(a) for a in self._attacks]

    def run_attack(self, attack_id: str) -> MvpAttackResult | None:
        for attack in self._attacks:
            if attack.attack_id == attack_id:
                return self._run_single(attack)
        return None

    def summary(self) -> dict[str, Any]:
        results = self.run_all()
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "results": results,
        }

    def _run_single(self, attack: MvpAttackCase) -> MvpAttackResult:
        try:
            output = attack.attack_fn()
        except Exception as e:
            return MvpAttackResult(
                attack_id=attack.attack_id,
                name=attack.name,
                blocked=False,
                actual_result="ERROR",
                details=str(e),
                passed=False,
            )

        blocked = output.get("blocked", False)
        actual_result = output.get("result", "UNKNOWN")
        passed = blocked and actual_result == attack.expected_result

        return MvpAttackResult(
            attack_id=attack.attack_id,
            name=attack.name,
            blocked=blocked,
            actual_result=actual_result,
            details=output.get("details", ""),
            passed=passed,
        )

    def probe_orchestrator(self, goal_text: str) -> dict[str, Any]:
        result = self._orchestrator.run_goal(goal_text)
        return {
            "blocked": result.verdict != "PASS",
            "result": result.verdict,
            "details": "; ".join(result.errors) if result.errors else "Orchestrator accepted",
        }

    def probe_bypass_validation(
        self,
        action_type: str = "execute_without_validation",
    ) -> dict[str, Any]:
        result = self._orchestrator.run_goal(
            f"Attempt {action_type}",
            context_overrides={
                "action_type": action_type,
                "bypass_validation": True,
            },
        )
        blocked = result.verdict in ("VALIDATION_FAILED", "GATE_DENIED_EVALUATE")
        return {
            "blocked": blocked,
            "result": result.verdict,
            "details": "; ".join(result.errors) if result.errors else "Not blocked",
        }

    def probe_self_promotion(
        self,
        agent_id: str = "attacker_agent",
    ) -> dict[str, Any]:
        result = self._orchestrator.run_goal(
            "Self-promote without review",
            context_overrides={
                "agent_id": agent_id,
                "action_type": "self_promote",
                "review_decision": "REJECTED",
                "review_reason": "Self-promotion detected",
            },
        )
        blocked = result.verdict in ("DENIED_AND_RECORDED", "FAILED", "GATE_DENIED_EVALUATE")
        return {
            "blocked": blocked,
            "result": "DENIED" if blocked else "PROMOTED",
            "details": "; ".join(result.errors) if result.errors else "Self-promotion blocked",
        }
