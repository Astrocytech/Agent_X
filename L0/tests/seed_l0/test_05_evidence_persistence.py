"""Test 05: Evidence persistence — trace, checkpoint, evaluation, memory evidence written."""

from __future__ import annotations

from core_kernel.models.kernel_io import KernelInput

from conftest import (
    SpyCheckpointPort,
    SpyTracePort,
    TestEvalPort,
    TestMemoryPort,
    full_runtime,
)


class TestEvidencePersistence:
    def test_completed_turn_produces_trace_evidence(self) -> None:
        trace = SpyTracePort()
        runtime = full_runtime(trace_port=trace)
        inp = KernelInput(user_goal="test", profile_id="test")
        runtime.run_turn(inp)
        assert len(trace.last_events) > 0
        assert trace.last_run_id != ""

    def test_completed_turn_produces_checkpoint_evidence(self) -> None:
        ckpt = SpyCheckpointPort()
        runtime = full_runtime(checkpoint_port=ckpt)
        inp = KernelInput(user_goal="test", profile_id="test")
        runtime.run_turn(inp)
        assert ckpt.last_run_id != ""
        assert len(ckpt.last_state) > 0

    def test_completed_turn_produces_evaluation_evidence(self) -> None:
        eval_port = TestEvalPort()
        runtime = full_runtime(evaluation_port=eval_port)
        inp = KernelInput(user_goal="test", profile_id="test")
        output = runtime.run_turn(inp)
        assert output.evaluation_score is not None
        assert output.evaluation_score > 0.0

    def test_completed_turn_produces_memory_evidence(self) -> None:
        memory = TestMemoryPort()
        runtime = full_runtime(memory_port=memory)
        inp = KernelInput(user_goal="test", profile_id="test")
        output = runtime.run_turn(inp)
        assert len(output.memory_writes) > 0
