"""KernelService — single public runtime facade for the universal kernel."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core_kernel.contracts.seed_ports import (
        KernelRuntimePort,
    )

from core_kernel.contracts.kernel_contracts import (
    KernelInput,
    KernelOutput,
    KernelTurnStatus,
)
from core_kernel.models.kernel_errors import KernelError
from core_kernel.models.kernel_requests import KernelTurnRequest
from core_kernel.models.kernel_results import KernelTurnResponse
from core_kernel.public.health import build_health

logger = logging.getLogger(__name__)

__all__ = [
    "KernelService",
    "KernelServiceError",
    "KernelTurnRequest",
    "KernelTurnResponse",
    "KernelTurnStatus",
]


class KernelServiceError(KernelError):
    """Error raised by KernelService."""


class KernelService:
    """Single public runtime facade.

    Usage::

        service = KernelService()
        response = service.run_turn(KernelTurnRequest(
            user_input="Solve this problem",
            session_id="sess-1",
            profile_id="generalist",
        ))
    """

    def __init__(
        self,
        kernel_runtime: KernelRuntimePort | None = None,
        default_profile_id: str | None = None,
        profile_dirs: list[Path] | None = None,
        strict_profile_validation: bool = True,
    ) -> None:
        self._runtime = kernel_runtime
        self._default_profile_id = default_profile_id
        self._profile_dirs = profile_dirs
        self._strict_profile_validation = strict_profile_validation
        self._profile_validated = False

        if self._runtime is None:
            from kernel_composition.seed_runtime_factory import (
                build_seed_kernel_runtime,
            )

            self._runtime = build_seed_kernel_runtime()

        if self._default_profile_id is None:
            self._default_profile_id = "generalist"

        self._validate_profiles()

    def _get_default_profile_id(self) -> str:
        assert self._default_profile_id is not None
        return self._default_profile_id

    def run_turn(self, request: KernelTurnRequest) -> KernelTurnResponse:
        """Execute one kernel turn.

        This is the ONLY method external entrypoints should call.
        """
        if self._runtime is None:
            raise KernelServiceError("KernelService.run_turn called but runtime is None")

        profile_id = request.profile_id or self._get_default_profile_id()

        kernel_input = KernelInput(
            user_goal=request.user_input,
            profile_id=profile_id,
        )

        try:
            output: KernelOutput = self._runtime.run_turn(kernel_input)
        except KernelError as exc:
            logger.error("Kernel turn failed: %s", exc)
            return self._error_response(request, str(exc), profile_id)
        except Exception as exc:
            logger.error("Unexpected kernel error: %s", exc)
            return self._error_response(
                request,
                f"Unexpected error: {exc}",
                profile_id,
            )

        status = self._map_status(output.status)
        return KernelTurnResponse(
            answer=output.primary_result,
            status=status,
            run_id=output.run_id,
            profile_id=output.profile_id,
            trace_id=output.trace_id,
            checkpoint_id=output.checkpoint_id or "",
            policy_decision_id=output.metadata.get(
                "policy_decision_id",
                output.metadata.get("policy_id", ""),
            ),
            governance_decision_id=output.metadata.get("governance_decision_id", ""),
            evaluation_verdict_id=output.verdict_id or "",
            evaluation_score=output.evaluation_score,
            memory_refs=output.memory_writes,
            metadata=dict(output.metadata),
        )

    def _map_status(self, run_state_value: str) -> KernelTurnStatus:
        from core_kernel.models.kernel_results import _get_status_map
        status_map = _get_status_map()
        mapped = status_map.get(run_state_value)
        if mapped is not None:
            return mapped
        raise ValueError(f"Unknown run status: {run_state_value!r}")

    def _error_response(
        self, request: KernelTurnRequest, error: str, default_profile_id: str
    ) -> KernelTurnResponse:
        from core_kernel.models.kernel_results import _generate_id, KernelTurnResponse
        run_id = _generate_id()
        return KernelTurnResponse(
            answer=f"[KernelService Error] {error}",
            status=KernelTurnStatus.ERROR,
            run_id=run_id,
            profile_id=request.profile_id or default_profile_id,
            trace_id="",
            policy_decision_id="",
            evaluation_score=0.0,
            memory_refs=[],
            metadata={
                "error": error,
                "trace_written": False,
                "checkpoint_written": False,
                "evidence_status": "missing_due_to_runtime_error",
            },
        )

    def _validate_profiles(self) -> tuple[bool, list[str]]:
        import importlib
        dirs: list[Path] = (
            self._profile_dirs
            if self._profile_dirs is not None
            else [
                Path(__file__).resolve().parent.parent.parent / "profiles" / "builtin",
            ]
        )
        errors: list[str] = []
        for profiles_dir in dirs:
            if not profiles_dir.exists():
                msg = f"Profile directory does not exist: {profiles_dir}"
                logger.warning(msg)
                errors.append(msg)
                continue
            try:
                profile_loader_mod = importlib.import_module("profiles.profile_loader")
                loader = profile_loader_mod.ProfileLoader(str(profiles_dir))
                for profile_id in loader.list_ids():
                    profile = loader.load(profile_id)
                    errs = loader.validate_profile(profile)
                    if errs:
                        msg = f"Profile '{profile_id}' validation errors: {errs}"
                        logger.warning(msg)
                        errors.append(msg)
            except Exception as exc:
                msg = f"Could not validate profiles in {profiles_dir}: {exc}"
                logger.warning(msg)
                errors.append(msg)
        validated = len(errors) == 0
        if errors and self._strict_profile_validation:
            raise KernelServiceError(
                "Profile validation failed in strict mode:\n  " + "\n  ".join(errors)
            )
        self._profile_validated = validated
        return validated, errors

    def health(self) -> dict[str, Any]:
        """Return a stable, small health report safe for production use.

        Deep diagnostics (authority hashes, platform leakage, boundary checks,
        port implementations) are available via:
            CODE.core_kernel.public.kernel_diagnostics.deep_health()
        """
        active_profile_id = self._default_profile_id or "generalist"
        seed_only = (
            getattr(self._runtime, "_seed_only", True) if self._runtime else True
        )

        result = build_health(
            self._runtime,
            active_profile_id,
            mode="production",
        )

        result["runtime_mode"] = "production"
        result["active_profile_id"] = active_profile_id
        result["active_gateway_type"] = "seed" if seed_only else "platform"
        result["evolution_enabled"] = False
        status_map = {"ok": "healthy", "degraded": "degraded", "fail": "failed"}
        result["runtime_health_status"] = status_map.get(
            result.get("status", ""), "failed"
        )
        from core_kernel.public.release_readiness import get_release_readiness

        readiness = get_release_readiness()
        result["release_readiness_status"] = readiness.status
        result["release_readiness_command"] = "make prove-seed"
        result["release_proof_artifact_found"] = readiness.proof_artifact_found
        result["seed_package_hash_found"] = readiness.seed_package_hash_found
        return result