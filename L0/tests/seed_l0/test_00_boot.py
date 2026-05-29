"""Test 00: Boot — KernelService instantiates, health returns expected fields."""

from __future__ import annotations

from core_kernel.public.kernel_service import KernelService


def test_kernel_service_constructs() -> None:
    service = KernelService()
    assert service is not None
    assert service._runtime is not None


def test_health_returns_dict() -> None:
    service = KernelService()
    health = service.health()
    assert isinstance(health, dict)


def test_health_reports_production_mode() -> None:
    service = KernelService()
    health = service.health()
    assert health["runtime_mode"] == "production"


def test_health_reports_evolution_disabled() -> None:
    service = KernelService()
    health = service.health()
    assert health["evolution_enabled"] is False


def test_health_reports_seed_gateway_type() -> None:
    service = KernelService()
    health = service.health()
    assert health["active_gateway_type"] == "seed"


def test_health_reports_release_readiness_command() -> None:
    service = KernelService()
    health = service.health()
    assert health["release_readiness_status"] == "unknown_without_make_prove"
    assert health["release_readiness_command"] == "make prove-seed"


def test_kernel_service_rejects_raw_dict() -> None:
    service = KernelService()
    try:
        service.run_turn({"user_input": "bad", "session_id": "x"})
    except (TypeError, AttributeError, Exception):
        pass
    else:
        raise AssertionError("KernelService.run_turn must reject raw dict input")
