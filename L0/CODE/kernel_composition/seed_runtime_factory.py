"""Seed runtime factory — builds a fully-wired SeedKernelRuntime with all required ports."""

from __future__ import annotations

import logging
from typing import Any

from core_kernel.runtime.seed_runtime import SeedKernelRuntime
from core_kernel.contracts.seed_ports import (
    CheckpointPort,
    ConfigPort,
    EvaluationPort,
    EvidenceWriterPort,
    GovernancePort,
    MemoryPort,
    PathResolverPort,
    PlannerPort,
    PolicyPort,
    ProfilePort,
    RiskPolicyPort,
    ToolGatewayPort,
    TracePort,
)

from kernel_composition.local_seed_ports.local_config_port import LocalConfigPort
from kernel_composition.local_seed_ports.local_path_resolver_port import LocalPathResolverPort
from kernel_composition.local_seed_ports.local_risk_policy_port import LocalRiskPolicyPort
from kernel_composition.local_seed_ports.local_evidence_writer_port import LocalEvidenceWriterPort
from kernel_composition.local_seed_ports.local_profile_port import LocalProfilePort
from kernel_composition.local_seed_ports.local_policy_port import LocalPolicyPort
from kernel_composition.local_seed_ports.local_governance_port import LocalGovernancePort
from kernel_composition.local_seed_ports.tool_gateway_adapter_port import (
    ToolGatewayAdapterPort,
    build_seed_tool_gateway,
)
from kernel_composition.local_seed_ports.local_planner_port import LocalPlannerPort
from kernel_composition.local_seed_ports.local_memory_port import LocalMemoryPort
from kernel_composition.local_seed_ports.local_evaluation_port import LocalEvaluationPort
from kernel_composition.local_seed_ports.local_trace_port import LocalTracePort
from kernel_composition.local_seed_ports.local_checkpoint_port import LocalCheckpointPort

logger = logging.getLogger(__name__)


_FORBIDDEN_FAKE_CLASSES = {
    "FakePlanner",
    "FakeProfileLoader",
    "FakePolicy",
    "FakeToolGateway",
    "FakeMemory",
    "FakeEvaluation",
    "FakeTrace",
    "FakeCheckpoint",
    "FakeGovernance",
}


def _validate_production_ports(*ports: Any) -> None:
    for port in ports:
        class_name = type(port).__name__
        if class_name in _FORBIDDEN_FAKE_CLASSES:
            raise RuntimeError(
                f"Fake port '{class_name}' used in production mode — all ports must be real"
            )
        safety = getattr(port, "runtime_safety_class", None)
        if safety != "production_seed_port":
            raise RuntimeError(
                f"Port '{class_name}' missing runtime_safety_class='production_seed_port' "
                f"— got {safety!r}"
            )


def build_seed_kernel_runtime(
    planner_port: PlannerPort | None = None,
    profile_port: ProfilePort | None = None,
    policy_port: PolicyPort | None = None,
    tool_gateway_port: ToolGatewayPort | None = None,
    memory_port: MemoryPort | None = None,
    evaluation_port: EvaluationPort | None = None,
    trace_port: TracePort | None = None,
    checkpoint_port: CheckpointPort | None = None,
    governance_port: GovernancePort | None = None,
    config_port: ConfigPort | None = None,
    path_resolver_port: PathResolverPort | None = None,
    risk_policy_port: RiskPolicyPort | None = None,
    evidence_writer_port: EvidenceWriterPort | None = None,
) -> SeedKernelRuntime:
    if planner_port is None:
        planner_port = LocalPlannerPort(policy_port=policy_port)
    if profile_port is None:
        profile_port = LocalProfilePort()
    if policy_port is None:
        policy_port = LocalPolicyPort()
    if tool_gateway_port is None:
        tool_gateway_port = ToolGatewayAdapterPort(
            build_seed_tool_gateway(strict_governance=True),
            evidence_writer=evidence_writer_port,
        )
    if memory_port is None:
        memory_port = LocalMemoryPort()
    if evaluation_port is None:
        evaluation_port = LocalEvaluationPort()
    if trace_port is None:
        trace_port = LocalTracePort()
    if checkpoint_port is None:
        checkpoint_port = LocalCheckpointPort()
    if governance_port is None:
        governance_port = LocalGovernancePort()
    if config_port is None:
        config_port = LocalConfigPort()
    if path_resolver_port is None:
        path_resolver_port = LocalPathResolverPort()
    if risk_policy_port is None:
        risk_policy_port = LocalRiskPolicyPort()
    if evidence_writer_port is None:
        evidence_writer_port = LocalEvidenceWriterPort()

    _validate_production_ports(
        planner_port,
        profile_port,
        policy_port,
        tool_gateway_port,
        memory_port,
        evaluation_port,
        trace_port,
        checkpoint_port,
        governance_port,
        config_port,
        path_resolver_port,
        risk_policy_port,
        evidence_writer_port,
    )

    runtime = SeedKernelRuntime(
        planner_port=planner_port,
        profile_port=profile_port,
        policy_port=policy_port,
        tool_gateway_port=tool_gateway_port,
        memory_port=memory_port,
        evaluation_port=evaluation_port,
        trace_port=trace_port,
        checkpoint_port=checkpoint_port,
        governance_port=governance_port,
        config_port=config_port,
        path_resolver_port=path_resolver_port,
        risk_policy_port=risk_policy_port,
        evidence_writer_port=evidence_writer_port,
    )
    logger.info("Built SeedKernelRuntime")
    return runtime
