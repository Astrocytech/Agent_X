from __future__ import annotations

import os
import tempfile

from agentx_evolve.loop.operational_loop import (
    MvpOperationalLoop,
    MvpLoopState,
    MvpPhaseResult,
    PHASE_PLAN,
    PHASE_EXECUTE,
    PHASE_VALIDATE,
    PHASE_PROMOTE,
    LOOP_PHASES,
)
from agentx_evolve.orchestrator.functional_orchestrator import (
    MvpFunctionalOrchestrator,
    MvpOrchestrationResult,
)
from agentx_evolve.blackboard.blackboard import MvpBlackboard
from agentx_evolve.checkpoints.checkpoint_manager import MvpCheckpointManager


class TestLoopIntegration:
    def test_loop_runs_all_phases_with_mock(self):
        class PassOrch(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                return MvpOrchestrationResult(
                    run_id="test-run",
                    goal_id="test-goal",
                    verdict="PASS",
                )
        loop = MvpOperationalLoop(orchestrator=PassOrch())
        state = loop.run_goal("test goal")
        assert state.completed
        phase_names = [p.phase for p in state.phase_results]
        assert PHASE_PLAN in phase_names
        assert PHASE_EXECUTE in phase_names
        assert PHASE_VALIDATE in phase_names
        assert PHASE_PROMOTE in phase_names

    def test_loop_with_blackboard_and_checkpoints(self):
        tmpdir = tempfile.mkdtemp()
        bb_path = os.path.join(tmpdir, "blackboard")
        cp_path = os.path.join(tmpdir, "checkpoints")
        bb = MvpBlackboard(base_path=bb_path)
        cp = MvpCheckpointManager(base_path=cp_path)

        class PassOrch(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                return MvpOrchestrationResult(
                    run_id="bb-run", goal_id="bb-goal", verdict="PASS",
                )
        loop = MvpOperationalLoop(
            orchestrator=PassOrch(),
            blackboard=bb,
            checkpoint_manager=cp,
        )
        state = loop.run_goal("persisted goal")
        assert state.completed
        bb_records = bb.list_by_run("bb-run")
        assert len(bb_records) > 0
        run_cps = cp.list_for_run("bb-run")
        assert len(run_cps) > 0
        assert os.path.isdir(bb_path)
        assert os.path.isdir(cp_path)

    def test_loop_fails_and_retries(self):
        call_count = 0

        class FailThenPass(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    return MvpOrchestrationResult(
                        run_id="retry-run", goal_id="retry-goal",
                        verdict="FAILED", errors=["first attempt failed"],
                    )
                return MvpOrchestrationResult(
                    run_id="retry-run", goal_id="retry-goal", verdict="PASS",
                )
        loop = MvpOperationalLoop(orchestrator=FailThenPass(), max_failures=3)
        state = loop.run_goal("retry goal")
        assert state.completed
        assert state.current_verdict == "PASS"
        assert call_count == 2

    def test_loop_replay_restores_state(self):
        tmpdir = tempfile.mkdtemp()
        cp_path = os.path.join(tmpdir, "checkpoints")
        cp = MvpCheckpointManager(base_path=cp_path)

        class PassOrch(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                return MvpOrchestrationResult(
                    run_id="replay-run", goal_id="replay-goal", verdict="PASS",
                )
        loop = MvpOperationalLoop(orchestrator=PassOrch(), checkpoint_manager=cp)
        state = loop.run_goal("replay test")
        assert state.completed
        cps = cp.list_for_run("replay-run")
        assert len(cps) > 0
        snap = cp.restore(cps[0].checkpoint_id)
        assert snap is not None
        assert snap["goal_id"] == "replay-goal"
        assert snap["verdict"] == "PASS"
