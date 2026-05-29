"""Port protocol definitions for seed runtime."""

from __future__ import annotations

from typing import Any, Protocol

from core_kernel.contracts.governance_contracts import (
    GovernanceContext,
    PortGovernanceAction,
    RiskAssessment,
)
from core_kernel.contracts.kernel_contracts import KernelInput, KernelOutput
from core_kernel.contracts.trace_contracts import EvaluationVerdict
from core_kernel.models.enums.seed_governance_decision import SeedGovernanceDecision
from core_kernel.models.kernel_atoms import Goal, PolicyDecision, Task
from core_kernel.models.kernel_results import SeedTurnResult
from core_kernel.models.planner_decision import PlannerContext, PlannerDecision
from core_kernel.models.tool_objects import ToolRequest, ToolResult
from profiles.agent_profile_schema import Profile


class ProfilePort(Protocol):
    def load(self, profile_id: str) -> Profile:
        ...


class PolicyPort(Protocol):
    def compute(self, profile: Profile, task: Task) -> PolicyDecision:
        ...


class ToolGatewayPort(Protocol):
    """
    Sole tool execution choke point.

    Runtime governance decides whether a planned action may proceed.
    The gateway enforces the approved execution boundary and must not be bypassed.
    Every tool call must route through this port.
    """

    def execute_typed(self, request: ToolRequest) -> ToolResult:
        ...


class MemoryPort(Protocol):
    def write(self, observation: str, ctx: dict) -> list[str]:
        ...


class EvaluationPort(Protocol):
    def evaluate(self, goal: Goal, output: str, **kwargs: Any) -> EvaluationVerdict:
        ...

    def evaluate_turn(self, turn: SeedTurnResult) -> EvaluationVerdict:
        ...


class TracePort(Protocol):
    def write(self, run_id: str, events: list[dict]) -> str:
        ...


class CheckpointPort(Protocol):
    def save(self, run_id: str, state: dict) -> str:
        ...


class GovernancePort(Protocol):
    """
    Runtime action authority.

    This port decides whether a planned action is allowed, denied, or approval-bound
    before the ToolGatewayPort is allowed to execute anything.
    """

    def decide(
        self,
        profile: Profile,
        action: PortGovernanceAction,
        ctx: GovernanceContext,
    ) -> SeedGovernanceDecision:
        ...


class PlannerPort(Protocol):
    """Port for making planning decisions during seed runtime execution."""

    def make_decision(
        self,
        goal: Goal,
        profile: Profile,
        context: PlannerContext,
        problem_model: Any = None,
        memory_refs: list[str] | None = None,
    ) -> PlannerDecision | None:
        ...


class ConfigPort(Protocol):
    def get(self, key: str, default: Any = None) -> Any:
        ...


class PathResolverPort(Protocol):
    def resolve(self, path_type: str, name: str) -> str:
        ...


class RiskPolicyPort(Protocol):
    def assess(
        self,
        tool_name: str,
        args: dict[str, Any],
        context: dict[str, Any],
    ) -> RiskAssessment:
        ...


class EvidenceWriterPort(Protocol):
    def write(self, event_type: str, payload: dict[str, Any]) -> str:
        ...


class KernelRuntimePort(Protocol):
    """Protocol that any runtime must satisfy to be used by KernelService."""

    def run_turn(self, kernel_input: KernelInput) -> KernelOutput:
        ...
