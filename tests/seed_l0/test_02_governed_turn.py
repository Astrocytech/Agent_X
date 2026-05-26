"""Test 02: Governed turn — full path: planner, governance, gateway, trace, checkpoint, eval, memory."""

from __future__ import annotations

from core_kernel.models.kernel_requests import KernelTurnRequest
from core_kernel.public.kernel_service import KernelService


def test_governed_turn_returns_answer() -> None:
    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Say hello from the governed seed.",
            session_id="test-session-02",
            profile_id="generalist",
        )
    )
    assert response.answer


def test_governed_turn_records_trace() -> None:
    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Trace test.",
            session_id="test-session-02",
            profile_id="generalist",
        )
    )
    assert response.trace_id


def test_governed_turn_records_checkpoint() -> None:
    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Checkpoint test.",
            session_id="test-session-02",
            profile_id="generalist",
        )
    )
    assert response.checkpoint_id


def test_governed_turn_records_evaluation_verdict() -> None:
    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Evaluation test.",
            session_id="test-session-02",
            profile_id="generalist",
        )
    )
    assert response.evaluation_verdict_id


def test_governed_turn_has_evaluation_score() -> None:
    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Score test.",
            session_id="test-session-02",
            profile_id="generalist",
        )
    )
    assert response.evaluation_score is not None


def test_governed_turn_writes_memory() -> None:
    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Memory test.",
            session_id="test-session-02",
            profile_id="generalist",
        )
    )
    assert isinstance(response.memory_refs, list)
