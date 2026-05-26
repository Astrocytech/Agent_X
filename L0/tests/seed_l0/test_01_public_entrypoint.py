"""Test 01: Public entrypoint — KernelService.run_turn() is the only external method."""

from __future__ import annotations

from core_kernel.models.kernel_requests import KernelTurnRequest
from core_kernel.public.kernel_service import KernelService


def test_kernel_service_has_run_turn() -> None:
    service = KernelService()
    assert hasattr(service, "run_turn")
    assert callable(service.run_turn)


def test_run_turn_returns_stable_response() -> None:
    service = KernelService()
    response = service.run_turn(
        KernelTurnRequest(
            user_input="Test the entrypoint.",
            session_id="test-session-01",
            profile_id="generalist",
        )
    )
    assert response.run_id
    assert response.profile_id
    assert response.status is not None
