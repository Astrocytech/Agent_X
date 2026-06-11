"""Test 09: Profile specialization — profile changes behavior, not L0 authority."""

from __future__ import annotations

from core_kernel.models.kernel_requests import KernelTurnRequest
from core_kernel.public.kernel_service import KernelService
from tool_gateway.seed_tool_registry import list_seed_tool_names


def _seed_tool_names() -> set[str]:
    return set(list_seed_tool_names())


def test_generalist_profile_runs_without_expanding_l0_surface() -> None:
    before_tools = _seed_tool_names()

    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Give a governed seed response.",
            session_id="profile-boundary-test",
            profile_id="generalist",
        )
    )

    after_tools = _seed_tool_names()

    assert response.profile_id == "generalist"
    assert response.answer
    assert response.trace_id
    assert response.checkpoint_id
    assert response.evaluation_verdict_id

    assert "seed.emit_answer" in before_tools
    assert "seed.emit_answer" in after_tools
    assert before_tools == after_tools
