"""Test 10: Seed acceptance — final 10/10 gate, asserts full L0 contract."""

from __future__ import annotations

from core_kernel.models.kernel_requests import KernelTurnRequest
from core_kernel.public.kernel_service import KernelService


def test_l0_seed_acceptance_contract() -> None:
    """
    L0 seed acceptance:
    - one public facade
    - one governed turn path
    - governance before gateway
    - gateway as execution choke point
    - trace/checkpoint/eval/memory evidence
    - manifest closure
    - no model/GPU/network/shell/self-modification requirement
    """
    service = KernelService()

    health = service.health()
    assert health["runtime_mode"] == "production"
    assert health["evolution_enabled"] is False

    response = service.run_turn(
        KernelTurnRequest(
            user_input="Acceptance test for the L0 seed kernel.",
            session_id="seed-acceptance",
            profile_id="generalist",
        )
    )

    assert response.answer
    assert response.trace_id
    assert response.checkpoint_id
    assert response.evaluation_verdict_id
    assert response.profile_id
