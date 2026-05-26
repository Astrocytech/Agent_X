"""Test 06: Checkpoint replay — run turn, save checkpoint, verify stable fields."""

from __future__ import annotations

from core_kernel.models.kernel_io import KernelInput

from tests.seed_l0.conftest import (
    SpyCheckpointPort,
    SpyTracePort,
    TestEvalPort,
    TestMemoryPort,
    TestPlannerPort,
    TestPolicyPort,
    TestProfilePort,
    full_runtime,
)


class TestCheckpointReplay:
    def test_run_turn_saves_checkpoint(self) -> None:
        ckpt = SpyCheckpointPort()
        runtime = full_runtime(checkpoint_port=ckpt)
        inp = KernelInput(user_goal="checkpoint replay test", profile_id="test")
        output = runtime.run_turn(inp)
        assert ckpt.last_run_id == output.run_id
        assert ckpt.last_state.get("output_returned") is True

    def test_checkpoint_contains_goal(self) -> None:
        ckpt = SpyCheckpointPort()
        runtime = full_runtime(checkpoint_port=ckpt)
        inp = KernelInput(user_goal="persist this goal", profile_id="test")
        runtime.run_turn(inp)
        events = ckpt.last_state.get("events", [])
        goal_phases = [e for e in events if "goal" in e.get("phase", "")]
        assert len(goal_phases) > 0

    def test_checkpoint_contains_governance_decision(self) -> None:
        ckpt = SpyCheckpointPort()
        runtime = full_runtime(checkpoint_port=ckpt)
        inp = KernelInput(user_goal="test", profile_id="test")
        runtime.run_turn(inp)
        events = ckpt.last_state.get("events", [])
        phases = [e.get("phase") for e in events]
        assert "governance_checked" in phases

    def test_checkpoint_contains_trace_phase_sequence(self) -> None:
        ckpt = SpyCheckpointPort()
        trace = SpyTracePort()
        runtime = full_runtime(checkpoint_port=ckpt, trace_port=trace)
        inp = KernelInput(user_goal="test", profile_id="test")
        output = runtime.run_turn(inp)
        ckpt_phases = [e.get("phase") for e in ckpt.last_state.get("events", [])]
        assert output.run_id == ckpt.last_run_id
        assert "planner_decision_made" in ckpt_phases
        assert "governance_checked" in ckpt_phases
        assert "tool_gateway_called" in ckpt_phases

    def test_phase_recorder_rejects_unknown_phase(self) -> None:
        from core_kernel.runtime.seed_phase_recorder import PhaseRecorder
        recorder = PhaseRecorder()
        try:
            recorder.start_phase("nonexistent_phase")
        except ValueError:
            pass
        else:
            raise AssertionError("PhaseRecorder must reject unknown phase names")

    def test_phase_recorder_requires_goal_before_profile(self) -> None:
        from core_kernel.runtime.seed_phase_recorder import PhaseRecorder
        recorder = PhaseRecorder()
        recorder.start_phase("input_received")
        recorder.end_phase(success=True)
        recorder.start_phase("goal_normalized")
        recorder.end_phase(success=True)
        try:
            recorder.start_phase("profile_loaded")
        except ValueError:
            raise AssertionError(
                "profile_loaded must be allowed after goal_normalized"
            )
        recorder.end_phase(success=True)
        recorder.reset()
        try:
            recorder.start_phase("tool_requested")
        except ValueError:
            pass
        else:
            raise AssertionError(
                "PhaseRecorder must reject tool_requested before governance_checked"
            )

    def test_checkpoint_contains_final_output_status(self) -> None:
        ckpt = SpyCheckpointPort()
        runtime = full_runtime(checkpoint_port=ckpt)
        inp = KernelInput(user_goal="test", profile_id="test")
        output = runtime.run_turn(inp)
        assert ckpt.last_state.get("output_returned") is True
        assert output.status == "completed"
