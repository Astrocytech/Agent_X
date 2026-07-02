from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from agentx_evolve.orchestrator.functional_orchestrator import (
    MvpFunctionalOrchestrator,
    MvpOrchestrationResult,
)
from agentx_evolve.goals.goal_evaluator import MvpGoalEvaluator, MvpGoalResult
from agentx_evolve.blackboard.blackboard import MvpBlackboard, MvpBlackboardRecord
from agentx_evolve.checkpoints.checkpoint_manager import MvpCheckpointManager


PHASE_PLAN = "plan"
PHASE_ASSIGN = "assign"
PHASE_EXECUTE = "execute"
PHASE_VALIDATE = "validate"
PHASE_REVIEW = "review"
PHASE_PROMOTE = "promote"
PHASE_REPLAY = "replay"

LOOP_PHASES = [
    PHASE_PLAN,
    PHASE_ASSIGN,
    PHASE_EXECUTE,
    PHASE_VALIDATE,
    PHASE_REVIEW,
    PHASE_PROMOTE,
]


@dataclass
class MvpPhaseResult:
    phase: str
    verdict: str
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)
    artifacts: list[dict] = field(default_factory=list)
    goal_result: MvpGoalResult | None = None
    checkpoint_id: str = ""


@dataclass
class MvpLoopState:
    goal_id: str = ""
    run_id: str = ""
    step_count: int = 0
    max_steps: int = 100
    current_verdict: str = "UNKNOWN"
    is_running: bool = False
    completed: bool = False
    errors: list[str] = field(default_factory=list)
    step_results: list[dict] = field(default_factory=list)
    phase_results: list[MvpPhaseResult] = field(default_factory=list)
    current_phase: str = ""
    plan: dict[str, Any] = field(default_factory=dict)


STOP_GOAL_ACHIEVED = "goal_achieved"
STOP_GOAL_IMPOSSIBLE = "goal_impossible"
STOP_RISK_TOO_HIGH = "risk_too_high"
STOP_TOO_MANY_FAILURES = "too_many_failures"
STOP_BUDGET_EXCEEDED = "budget_exceeded"
STOP_INVARIANT_VIOLATION = "invariant_violation"


class MvpOperationalLoop:
    def __init__(
        self,
        orchestrator: MvpFunctionalOrchestrator | None = None,
        goal_evaluator: MvpGoalEvaluator | None = None,
        blackboard: MvpBlackboard | None = None,
        checkpoint_manager: MvpCheckpointManager | None = None,
        max_steps: int = 100,
        max_failures: int = 5,
    ) -> None:
        self._orchestrator = orchestrator or MvpFunctionalOrchestrator()
        self._goal_evaluator = goal_evaluator or MvpGoalEvaluator()
        self._blackboard = blackboard or MvpBlackboard()
        self._checkpoints = checkpoint_manager or MvpCheckpointManager()
        self._max_steps = max_steps
        self._max_failures = max_failures
        self._success_criteria: list[str] = []
        self._failure_criteria: list[str] = []

    # -- Phase execution methods, overridable by subclasses --

    def run_plan_phase(
        self,
        goal_text: str,
        state: MvpLoopState,
        ctx: dict[str, Any],
    ) -> MvpPhaseResult:
        plan = {
            "goal_text": goal_text,
            "phases": list(LOOP_PHASES),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "estimated_steps": len(LOOP_PHASES),
        }
        state.plan = plan
        self._blackboard.write(MvpBlackboardRecord(
            record_id=f"plan-{state.run_id}",
            record_type="plan_draft",
            owner="loop",
            run_id=state.run_id,
            data=plan,
        ))
        return MvpPhaseResult(
            phase=PHASE_PLAN,
            verdict="PASS",
            artifacts=[{"type": "plan", "data": plan}],
        )

    def run_assign_phase(
        self,
        goal_text: str,
        state: MvpLoopState,
        ctx: dict[str, Any],
    ) -> MvpPhaseResult:
        agents = ctx.get("agents", ["default_agent"])
        assignments = []
        for i, agent_id in enumerate(agents):
            assignments.append({
                "agent_id": agent_id,
                "phase": LOOP_PHASES[i] if i < len(LOOP_PHASES) else LOOP_PHASES[-1],
                "goal": goal_text,
            })
        self._blackboard.write(MvpBlackboardRecord(
            record_id=f"assign-{state.run_id}",
            record_type="candidate_action",
            owner="loop",
            run_id=state.run_id,
            data={"assignments": assignments},
        ))
        return MvpPhaseResult(
            phase=PHASE_ASSIGN,
            verdict="PASS",
            artifacts=[{"type": "assignments", "data": assignments}],
        )

    def run_execute_phase(
        self,
        goal_text: str,
        state: MvpLoopState,
        ctx: dict[str, Any],
    ) -> MvpPhaseResult:
        result = self._orchestrator.run_goal(
            goal_text,
            profile_id=ctx.get("profile_id", "STRICT"),
            context_overrides=ctx.get("context_overrides"),
        )
        if result.run_id and not state.run_id:
            state.run_id = result.run_id
        if result.goal_id and not state.goal_id:
            state.goal_id = result.goal_id
        state.current_verdict = result.verdict
        self._blackboard.write(MvpBlackboardRecord(
            record_id=f"exec-{state.run_id}-{state.step_count}",
            record_type="observation",
            owner="loop",
            run_id=state.run_id,
            data={"verdict": result.verdict, "errors": list(result.errors)},
        ))
        return MvpPhaseResult(
            phase=PHASE_EXECUTE,
            verdict=result.verdict,
            artifacts=list(result.artifacts),
            errors=list(result.errors),
        )

    def run_validate_phase(
        self,
        goal_text: str,
        state: MvpLoopState,
        ctx: dict[str, Any],
    ) -> MvpPhaseResult:
        if self._success_criteria or self._failure_criteria:
            success_criteria = list(self._success_criteria)
            failure_criteria = list(self._failure_criteria)
            test_results_list = ["PASS"] if state.current_verdict == "PASS" else ["FAIL"]
            evidence = []
        elif state.current_verdict == "PASS":
            success_criteria = ["goal_executed"]
            failure_criteria = []
            test_results_list = ["PASS"]
            evidence = ["auto-validated"]
        else:
            success_criteria = ["goal_executed"]
            failure_criteria = []
            test_results_list = ["FAIL"]
            evidence = ["auto-validated"]

        orch_dict = {
            "success_criteria": success_criteria,
            "failure_criteria": failure_criteria,
            "observed_results": ["goal_executed"],
            "test_results": test_results_list,
            "evidence_refs": evidence,
        }
        goal_result = self._goal_evaluator.evaluate(
            state.goal_id, state.run_id, orch_dict,
        )
        state.current_verdict = goal_result.verdict
        self._blackboard.write(MvpBlackboardRecord(
            record_id=f"valid-{state.run_id}-{state.step_count}",
            record_type="validation_result",
            owner="loop",
            run_id=state.run_id,
            data={"verdict": goal_result.verdict, "errors": list(goal_result.errors)},
        ))
        return MvpPhaseResult(
            phase=PHASE_VALIDATE,
            verdict=goal_result.verdict,
            errors=list(goal_result.errors),
            goal_result=goal_result,
        )

    def run_review_phase(
        self,
        goal_text: str,
        state: MvpLoopState,
        ctx: dict[str, Any],
    ) -> MvpPhaseResult:
        errors: list[str] = []
        promote_ctx: dict[str, Any] = {
            "run_id": state.run_id,
            "agent_id": ctx.get("agent_id", "default_agent"),
        }
        review_decision = ctx.get("review_decision", "APPROVED")
        review_reason = ctx.get("review_reason", "Auto-approved")

        self._blackboard.write(MvpBlackboardRecord(
            record_id=f"review-{state.run_id}-{state.step_count}",
            record_type="critique",
            owner="loop",
            run_id=state.run_id,
            data={"decision": review_decision, "reason": review_reason},
        ))
        return MvpPhaseResult(
            phase=PHASE_REVIEW,
            verdict="PASS" if review_decision == "APPROVED" else "REJECTED",
            errors=errors,
        )

    def run_promote_phase(
        self,
        goal_text: str,
        state: MvpLoopState,
        ctx: dict[str, Any],
    ) -> MvpPhaseResult:
        errors: list[str] = []
        self._blackboard.write(MvpBlackboardRecord(
            record_id=f"promote-{state.run_id}-{state.step_count}",
            record_type="goal_state",
            owner="loop",
            run_id=state.run_id,
            data={"verdict": state.current_verdict, "completed": state.completed},
        ))
        cp = self._checkpoints.create_checkpoint(
            run_id=state.run_id,
            state_snapshot={
                "goal_id": state.goal_id,
                "run_id": state.run_id,
                "step_count": state.step_count,
                "verdict": state.current_verdict,
                "phase_results": [
                    {"phase": pr.phase, "verdict": pr.verdict} for pr in state.phase_results
                ],
            },
            description=f"End of loop for {state.goal_id}",
        )
        return MvpPhaseResult(
            phase=PHASE_PROMOTE,
            verdict=state.current_verdict,
            errors=errors,
            checkpoint_id=cp.checkpoint_id,
        )

    # -- Main loop logic --

    def set_criteria(self, success_criteria: list[str], failure_criteria: list[str]) -> None:
        self._success_criteria = list(success_criteria)
        self._failure_criteria = list(failure_criteria)

    def run_goal(self, goal_text: str) -> MvpLoopState:
        state = MvpLoopState(max_steps=self._max_steps, is_running=True)
        failure_count = 0

        while state.step_count < self._max_steps:
            state.step_count += 1

            for phase in LOOP_PHASES:
                if state.completed:
                    break
                state.current_phase = phase
                phase_ctx: dict[str, Any] = {}

                phase_methods = {
                    PHASE_PLAN: self.run_plan_phase,
                    PHASE_ASSIGN: self.run_assign_phase,
                    PHASE_EXECUTE: self.run_execute_phase,
                    PHASE_VALIDATE: self.run_validate_phase,
                    PHASE_REVIEW: self.run_review_phase,
                    PHASE_PROMOTE: self.run_promote_phase,
                }
                method = phase_methods.get(phase)
                if method is None:
                    continue

                phase_result = method(goal_text, state, phase_ctx)
                state.phase_results.append(phase_result)

                if not state.goal_id and hasattr(phase_result, "goal_snapshot"):
                    pass

                if phase_result.errors:
                    state.errors.extend(phase_result.errors)
                    if phase == PHASE_EXECUTE:
                        failure_count += 1

                if phase == PHASE_EXECUTE:
                    state.current_verdict = phase_result.verdict

                if phase == PHASE_PROMOTE and phase_result.verdict == "PASS":
                    state.completed = True

                state.step_results.append({
                    "step": state.step_count,
                    "phase": phase,
                    "verdict": phase_result.verdict,
                    "errors": list(phase_result.errors),
                })

            stop_reason = self._should_stop(state, failure_count)
            if stop_reason is not None or state.completed:
                if not state.completed:
                    state.completed = True
                stop_label = stop_reason or "completed"
                state.errors.append(f"Stop: {stop_label}")
                state.is_running = False
                return state

        state.completed = True
        state.is_running = False
        return state

    def replay_goal(
        self,
        goal_text: str,
        checkpoint_id: str,
        context: Any = None,
    ) -> MvpLoopState:
        snapshot = self._checkpoints.restore(checkpoint_id)
        state = MvpLoopState(is_running=True, max_steps=self._max_steps)
        if snapshot:
            state.goal_id = snapshot.get("goal_id", "")
            state.run_id = snapshot.get("run_id", "")
            state.step_count = snapshot.get("step_count", 0)
            state.current_verdict = snapshot.get("verdict", "UNKNOWN")

        if context is not None:
            replay_result = self._orchestrator.replay_run(state.run_id, context)
            state.current_verdict = replay_result.verdict
            state.errors.extend(replay_result.errors)

        state.completed = True
        state.is_running = False
        return state

    def _should_stop(
        self, state: MvpLoopState, failure_count: int
    ) -> str | None:
        if state.current_verdict == "PASS":
            return STOP_GOAL_ACHIEVED
        if state.current_verdict in ("VALIDATION_FAILED", "SIMULATION_FAILED"):
            return STOP_GOAL_IMPOSSIBLE
        if state.current_verdict.startswith("GATE_DENIED_"):
            return STOP_RISK_TOO_HIGH
        if failure_count >= self._max_failures:
            return STOP_TOO_MANY_FAILURES
        if state.step_count >= self._max_steps:
            return STOP_BUDGET_EXCEEDED
        if state.current_verdict == "INVARIANT_VIOLATION":
            return STOP_INVARIANT_VIOLATION
        return None

    def stop_conditions(self) -> list[str]:
        return [
            f"{STOP_GOAL_ACHIEVED}: Goal was completed successfully (verdict PASS)",
            f"{STOP_GOAL_IMPOSSIBLE}: Validation or simulation failure indicates goal cannot be completed",
            f"{STOP_RISK_TOO_HIGH}: Decision gate denied the action due to risk",
            f"{STOP_TOO_MANY_FAILURES}: Exceeded {self._max_failures} consecutive failures",
            f"{STOP_BUDGET_EXCEEDED}: Exceeded {self._max_steps} maximum steps",
            f"{STOP_INVARIANT_VIOLATION}: Invariant check failed",
        ]
