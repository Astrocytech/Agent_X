"""SeedKernelRuntime — production seed runtime with canonical phase groups."""

from __future__ import annotations

import uuid
from typing import Any

from core_kernel.runtime.phase_result import PhaseResult, REQUIRED_PHASE_OUTPUT
from core_kernel.runtime.seed_phase_recorder import PhaseRecorder
from core_kernel.contracts.seed_phase_order import REQUIRED_SEED_PORTS
from core_kernel.runtime.failure_taxonomy import FAILURE_CATEGORIES
from core_kernel.models.kernel_io import KernelOutput
from core_kernel.runtime.phases.decision import (
    run_approval_continuation_phase,
    run_governance_phase,
    run_planning_phase,
)
from core_kernel.runtime.phases.execution import run_tool_phase
from core_kernel.runtime.phases.finale import run_output_phase
from core_kernel.runtime.phases.prelude import (
    run_goal_phase,
    run_input_phase,
    run_policy_phase,
    run_profile_phase,
    run_task_phase,
)
from core_kernel.runtime.phases.record import (
    run_checkpoint_phase,
    run_evaluation_phase,
    run_memory_phase,
    run_trace_phase,
)
from core_kernel.memory.seed_memory_facade import SeedMemoryFacade
from core_kernel.runtime.seed_turn_record import _RunContext
class SeedKernelRuntime:
    def __init__(
        self,
        planner_port=None,
        profile_port=None,
        policy_port=None,
        tool_gateway_port=None,
        memory_port=None,
        evaluation_port=None,
        trace_port=None,
        checkpoint_port=None,
        governance_port=None,
        seed_only=True,
        unsafe_allow_l1_imports=False,
        config_port=None,
        path_resolver_port=None,
        risk_policy_port=None,
        evidence_writer_port=None,
    ) -> None:
        self._planner_port = planner_port
        self._profile_port = profile_port
        self._policy_port = policy_port
        self._tool_gateway_port = tool_gateway_port
        self._memory_port = memory_port
        self._memory_facade = SeedMemoryFacade(memory_port) if memory_port else None
        self._evaluation_port = evaluation_port
        self._trace_port = trace_port
        self._checkpoint_port = checkpoint_port
        self._governance_port = governance_port
        self._config_port = config_port
        self._path_resolver_port = path_resolver_port
        self._risk_policy_port = risk_policy_port
        self._evidence_writer_port = evidence_writer_port
        self._seed_only = seed_only
        if not seed_only and not unsafe_allow_l1_imports:
            self._seed_only = True
        self._phase_recorder = PhaseRecorder()

    def _ports(self) -> dict[str, Any]:
        return {
            "planner_port": self._planner_port,
            "profile_port": self._profile_port,
            "policy_port": self._policy_port,
            "tool_gateway_port": self._tool_gateway_port,
            "memory_port": self._memory_port,
            "memory_facade": self._memory_facade,
            "evaluation_port": self._evaluation_port,
            "trace_port": self._trace_port,
            "checkpoint_port": self._checkpoint_port,
            "governance_port": self._governance_port,
            "config_port": self._config_port,
            "path_resolver_port": self._path_resolver_port,
            "risk_policy_port": self._risk_policy_port,
            "evidence_writer_port": self._evidence_writer_port,
            "phase_recorder": self._phase_recorder,
        }

    def port_health(self) -> dict[str, bool]:
        required = {
            "planner": self._planner_port,
            "profile": self._profile_port,
            "policy": self._policy_port,
            "tool_gateway": self._tool_gateway_port,
            "memory": self._memory_port,
            "evaluation": self._evaluation_port,
            "trace": self._trace_port,
            "checkpoint": self._checkpoint_port,
            "governance": self._governance_port,
        }
        return {name: port is not None for name, port in required.items()}

    def _require_port(self, port, name):
        if port is None:
            raise RuntimeError(f"SeedKernelRuntime missing required port: {name}.")

    def run_turn(self, kernel_input):
        return self._run_turn_impl(kernel_input)

    def _prepare_context(self, kernel_input):
        return _RunContext(run_id=uuid.uuid4().hex[:12])

    def _run_planning_phase(self, ctx, kernel_input, emit, ports):
        run_planning_phase(ctx, kernel_input, emit, ports)

    def _run_governance_phase(self, ctx, kernel_input, emit, ports):
        run_governance_phase(ctx, kernel_input, emit, ports)

    def _run_approval_continuation_phase(self, ctx, kernel_input, emit, ports):
        run_approval_continuation_phase(ctx, kernel_input, emit, ports)

    def _run_gateway_phase(self, ctx, kernel_input, emit, ports):
        run_tool_phase(ctx, kernel_input, emit, ports)

    def _run_recording_phase(self, ctx, kernel_input, emit, ports):
        run_trace_phase(ctx, kernel_input, emit, ports)
        run_evaluation_phase(ctx, kernel_input, emit, ports)
        run_memory_phase(ctx, kernel_input, emit, ports)
        run_checkpoint_phase(ctx, kernel_input, emit, ports)

    def _build_response(self, ctx, kernel_input, emit, ports):
        return run_output_phase(ctx, kernel_input, emit, ports)

    def _handle_failure(self, ctx, kernel_input, error):
        from core_kernel.models.enums.seed_failure_reason import SeedFailureReason

        trace_id = "trace_not_written"
        checkpoint_id = "checkpoint_not_written"
        memory_writes: list[str] = []

        if self._trace_port is not None:
            try:
                trace_id = self._trace_port.write(ctx.run_id, list(ctx.events))
            except Exception:
                trace_id = "trace_write_failed"
        if self._checkpoint_port is not None:
            try:
                checkpoint_id = self._checkpoint_port.save(
                    ctx.run_id, {"status": "failed", "error": str(error)}
                )
            except Exception:
                checkpoint_id = "checkpoint_write_failed"
        if self._memory_port is not None:
            try:
                memory_writes = self._memory_port.write(
                    str(error), {"run_id": ctx.run_id, "status": "failed"}
                )
            except Exception:
                memory_writes = []

        failed_phase = getattr(ctx, "current_phase", "unknown")
        failure_category = FAILURE_CATEGORIES.get(
            failed_phase + "_failure",
            FAILURE_CATEGORIES.get("seed_boundary_violation", {}),
        )
        return KernelOutput(
            run_id=ctx.run_id,
            profile_id=kernel_input.profile_id,
            status=failure_category.get("user_visible_status", "error"),
            primary_result=str(error) or SeedFailureReason.RUNTIME_ERROR.value,
            trace_id=trace_id,
            checkpoint_id=checkpoint_id,
            memory_writes=memory_writes,
            metadata={
                "runtime_authority": "seed",
                "error": str(error),
                "error_type": type(error).__name__,
                "failure_reason": SeedFailureReason.UNKNOWN.value,
                "failure_category": failed_phase,
                "retry_allowed": failure_category.get("retry_allowed", False),
                "fallback_phase": failure_category.get("fallback_phase", ""),
                "failed_phase": failed_phase,
                "recoverable": failure_category.get("retry_allowed", False),
                "events": list(ctx.events),
            },
        )

    def _run_turn_impl(self, kernel_input):
        for port_name in REQUIRED_SEED_PORTS:
            self._require_port(getattr(self, f"_{port_name}"), port_name)

        self._phase_recorder.reset()
        ctx = self._prepare_context(kernel_input)
        ports = self._ports()
        phase_results: list[PhaseResult] = []

        def emit(phase, **extra):
            self._phase_recorder.start_phase(phase)
            ctx.events.append({"phase": phase, **extra})
            self._phase_recorder.end_phase(success=True)

        def record_phase_result(name: str, success: bool = True, failure_reason: str = ""):
            pr = PhaseResult(
                phase_name=name,
                success=success,
                failure_reason=failure_reason,
                events=[e for e in ctx.events if e.get("phase") == name],
            )
            for field in REQUIRED_PHASE_OUTPUT.get(name, []):
                obj, attr = field.split(".", 1)
                if obj == "ctx" and hasattr(ctx, attr):
                    val = getattr(ctx, attr, None)
                    if val:
                        pr.produced_fields[field] = val
            phase_results.append(pr)

        try:
            run_input_phase(ctx, kernel_input, emit, ports)
            record_phase_result("input_received", success=not ctx.invalid_input)
            run_goal_phase(ctx, kernel_input, emit, ports)
            record_phase_result("goal_normalized", success=bool(ctx.goal))
            run_profile_phase(ctx, kernel_input, emit, ports)
            record_phase_result("profile_loaded", success=not ctx.profile_error)
            run_task_phase(ctx, kernel_input, emit, ports)
            record_phase_result("task_created", success=bool(ctx.task))
            run_policy_phase(ctx, kernel_input, emit, ports)
            record_phase_result("policy_computed", success=not ctx.policy_error)

            self._run_planning_phase(ctx, kernel_input, emit, ports)
            record_phase_result("capability_selected", success=not ctx.memory_error)
            record_phase_result("planner_decision_made", success=not ctx.planner_error)

            self._run_governance_phase(ctx, kernel_input, emit, ports)
            record_phase_result("governance_checked", success=not ctx.governance_error)

            self._run_approval_continuation_phase(ctx, kernel_input, emit, ports)
            if ctx.approval_continuation_denied:
                record_phase_result("approval_continuation_failed", success=False, failure_reason="denied")
            else:
                record_phase_result(
                    "approval_continuation_resolved",
                    success=True,
                )

            self._run_gateway_phase(ctx, kernel_input, emit, ports)
            record_phase_result("tool_requested", success=bool(ctx.tool_output))

            self._run_recording_phase(ctx, kernel_input, emit, ports)
            record_phase_result("trace_write_completed", success=bool(ctx.trace_id))
            record_phase_result("evaluation_completed", success=ctx.evaluation_status != "failed")
            record_phase_result("memory_written_or_skipped_with_reason", success=not ctx.memory_write_error)
            record_phase_result("checkpoint_write_completed", success=bool(ctx.checkpoint_id))

            output = self._build_response(ctx, kernel_input, emit, ports)
            record_phase_result("output_returned", success=bool(output))
            ctx.phase_results = phase_results
            return output
        except Exception as e:
            ctx.phase_results = phase_results
            return self._handle_failure(ctx, kernel_input, e)
