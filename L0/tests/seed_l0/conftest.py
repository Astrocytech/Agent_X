"""Shared test ports and helpers for the canonical L0 seed proof suite."""

from __future__ import annotations

from core_kernel.contracts.trace_contracts import EvaluationResult
from core_kernel.models.enums.seed_governance_decision import SeedGovernanceDecision
from core_kernel.models.kernel_atoms import PolicyDecision, Goal
from core_kernel.models.kernel_io import KernelInput
from core_kernel.models.planner_decision import PlannerDecision
from core_kernel.runtime.seed_runtime import SeedKernelRuntime


class TestProfilePort:
    def load(self, profile_id: str):
        return type("Profile", (), {"id": profile_id, "role": "test"})()


class TestPolicyPort:
    def compute(self, profile, task) -> PolicyDecision:
        return PolicyDecision(target_id="policy-seed-001", allowed=True, reason="test")


class TestMemoryPort:
    def write(self, observation: str, ctx: dict) -> list[str]:
        return ["mem-ref-1"]


class TestEvalPort:
    def evaluate(self, goal, output, **kwargs) -> EvaluationResult:
        score = 1.0 if output else 0.0
        return EvaluationResult.from_score(score)

    def evaluate_turn(self, turn) -> EvaluationResult:
        return self.evaluate(Goal(text=turn.status), turn.tool_output)


class SpyTracePort:
    def __init__(self):
        self.last_run_id = ""
        self.last_events = []

    def write(self, run_id: str, events: list[dict]) -> str:
        self.last_run_id = run_id
        self.last_events = list(events)
        return f"trace-{run_id}"


class SpyCheckpointPort:
    def __init__(self):
        self.last_run_id = ""
        self.last_state = {}

    def save(self, run_id: str, state: dict) -> str:
        self.last_run_id = run_id
        self.last_state = dict(state)
        return f"ckpt-{run_id}"


class TestPlannerPort:
    def make_decision(self, goal, profile, context) -> PlannerDecision:
        return PlannerDecision(
            task_id="t-1",
            action_type="execute",
            tool_name="seed.emit_answer",
            arguments={"answer": "test answer", "run_id": "test-run"},
            reasoning="test",
        )


class TestGovernancePort:
    def decide(self, profile, action, ctx: dict) -> SeedGovernanceDecision:
        return SeedGovernanceDecision(allowed=True, reason="ok", decision_id="gov-1")


class DenyGovernancePort:
    def decide(self, profile, action, ctx: dict) -> SeedGovernanceDecision:
        return SeedGovernanceDecision(allowed=False, reason="denied", decision_id="gov-deny")


class PassThroughToolGatewayPort:
    def __init__(self):
        self.last_request = None
        self.called = False

    def execute_typed(self, request):
        self.last_request = request
        self.called = True
        return type("Result", (), {
            "tool_name": request.tool_name,
            "status": "success",
            "output": f"gateway:{request.tool_name}",
            "blocked_reason": None,
            "error": None,
            "policy_decision_id": "",
            "trace_id": "",
            "risk_level": "",
        })()


def full_runtime(**overrides) -> SeedKernelRuntime:
    kwargs = dict(
        planner_port=TestPlannerPort(),
        profile_port=TestProfilePort(),
        policy_port=TestPolicyPort(),
        tool_gateway_port=PassThroughToolGatewayPort(),
        memory_port=TestMemoryPort(),
        evaluation_port=TestEvalPort(),
        trace_port=SpyTracePort(),
        checkpoint_port=SpyCheckpointPort(),
        governance_port=TestGovernancePort(),
    )
    kwargs.update(overrides)
    return SeedKernelRuntime(**kwargs)


def make_input(text: str = "seed test") -> KernelInput:
    return KernelInput(user_goal=text, profile_id="test-profile")
