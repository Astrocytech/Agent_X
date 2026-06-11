from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimulationResult:
    simulation_id: str = ""
    action_id: str = ""
    predicted_changes: list[dict] = field(default_factory=list)
    predicted_risks: list[dict] = field(default_factory=list)
    invariants_checked: list[str] = field(default_factory=list)
    rollback_required: bool = False
    rollback_plan_id: str | None = None
    safe_to_execute: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "action_id": self.action_id,
            "predicted_changes": list(self.predicted_changes),
            "predicted_risks": list(self.predicted_risks),
            "invariants_checked": list(self.invariants_checked),
            "rollback_required": self.rollback_required,
            "rollback_plan_id": self.rollback_plan_id,
            "safe_to_execute": self.safe_to_execute,
            "reason": self.reason,
        }


class MvpSimulationEngine:
    def __init__(self) -> None:
        self._results: list[SimulationResult] = []

    def simulate(self, action: Any, context: dict[str, Any]) -> SimulationResult:
        sim_id = context.get("simulation_id", "sim_default")
        action_id = getattr(action, "action_id", "") if action else ""

        predicted = []
        risks = []

        action_type = context.get("action_type", "")
        if action_type == "report_generation":
            target_path = context.get("target_path", "")
            predicted.append({
                "type": "artifact_write",
                "target": target_path,
                "size_estimate": context.get("size_estimate", 1024),
            })
            risks.append({
                "type": "artifact_write",
                "severity": "low",
                "description": f"Write artifact to {target_path}",
            })

        rollback_plan_id = context.get("rollback_plan_id")
        rollback_required = context.get("requires_rollback", False)

        safe = True
        reason = "Simulation passed"
        if rollback_required and not rollback_plan_id:
            safe = False
            reason = "Rollback plan required but missing"

        result = SimulationResult(
            simulation_id=sim_id,
            action_id=action_id,
            predicted_changes=predicted,
            predicted_risks=risks,
            invariants_checked=["no_action_without_validation"],
            rollback_required=rollback_required,
            rollback_plan_id=rollback_plan_id,
            safe_to_execute=safe,
            reason=reason,
        )
        self._results.append(result)
        return result

    def latest(self) -> SimulationResult | None:
        return self._results[-1] if self._results else None

    def clear(self) -> None:
        self._results.clear()
