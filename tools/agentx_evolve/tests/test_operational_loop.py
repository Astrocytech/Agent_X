from agentx_evolve.loop.operational_loop import (
    MvpLoopState,
    MvpOperationalLoop,
    STOP_GOAL_ACHIEVED,
    STOP_GOAL_IMPOSSIBLE,
    STOP_RISK_TOO_HIGH,
    STOP_TOO_MANY_FAILURES,
    STOP_BUDGET_EXCEEDED,
    STOP_INVARIANT_VIOLATION,
)
from agentx_evolve.orchestrator.functional_orchestrator import (
    MvpFunctionalOrchestrator,
    MvpOrchestrationResult,
)


class TestMvpLoopState:
    def test_loop_state_defaults(self):
        state = MvpLoopState()
        assert state.goal_id == ""
        assert state.run_id == ""
        assert state.step_count == 0
        assert state.max_steps == 100
        assert state.current_verdict == "UNKNOWN"
        assert state.is_running is False
        assert state.completed is False
        assert state.errors == []
        assert state.step_results == []


class TestMvpOperationalLoop:
    def test_loop_completes_simple_goal(self):
        class PassOrchestrator(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> MvpOrchestrationResult:
                return MvpOrchestrationResult(
                    run_id="pass-run",
                    goal_id="pass-goal",
                    verdict="PASS",
                )

        loop = MvpOperationalLoop(orchestrator=PassOrchestrator())
        state = loop.run_goal("simple goal")
        assert state.completed is True
        assert state.is_running is False
        assert state.current_verdict == "PASS"
        assert state.step_count == 1
        assert STOP_GOAL_ACHIEVED in state.errors[-1]

    def test_loop_stops_on_repeated_failure(self):
        class FailOrchestrator(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> MvpOrchestrationResult:
                return MvpOrchestrationResult(
                    run_id="fail-run",
                    goal_id="fail-goal",
                    verdict="FAILED",
                    errors=["something went wrong"],
                )

        loop = MvpOperationalLoop(orchestrator=FailOrchestrator(), max_failures=3)
        state = loop.run_goal("failing goal")
        assert state.completed is True
        assert len(state.errors) >= 1
        assert STOP_TOO_MANY_FAILURES in state.errors[-1]

    def test_loop_stop_conditions_list(self):
        loop = MvpOperationalLoop(max_steps=50, max_failures=3)
        conditions = loop.stop_conditions()
        assert isinstance(conditions, list)
        assert len(conditions) == 6
        assert any(STOP_GOAL_ACHIEVED in c for c in conditions)
        assert any(STOP_GOAL_IMPOSSIBLE in c for c in conditions)
        assert any(STOP_RISK_TOO_HIGH in c for c in conditions)
        assert any(STOP_TOO_MANY_FAILURES in c for c in conditions)
        assert any(STOP_BUDGET_EXCEEDED in c for c in conditions)
        assert any(STOP_INVARIANT_VIOLATION in c for c in conditions)

    def test_loop_max_steps_enforced(self):
        class SlowOrchestrator(MvpFunctionalOrchestrator):
            def __init__(self):
                super().__init__()
                self._call_count = 0

            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> MvpOrchestrationResult:
                self._call_count += 1
                return MvpOrchestrationResult(
                    run_id="slow-run",
                    goal_id="slow-goal",
                    verdict="WORKING",
                )

        orch = SlowOrchestrator()
        loop = MvpOperationalLoop(orchestrator=orch, max_steps=3, max_failures=10)
        state = loop.run_goal("slow goal")
        assert state.completed is True
        assert state.step_count == 3
        assert STOP_BUDGET_EXCEEDED in state.errors[-1]
