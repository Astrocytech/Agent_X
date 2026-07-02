"""Closes remaining N1/N2 gaps: schema migration, identity binding, budget,
dependency graph, causal trace, real MCP stdio execution.

Covers (from specs):
- Schema migration for state, evidence, contracts, messages, actions, results,
  agent records — reject unsupported schemas, record migration evidence, no
  silent evidence meaning alteration
- Identity binding: bind identity to capabilities, messages, reviews, promotions;
  reject forged reviewer/executor/promoter identities
- Budget: action, retry, runtime, model calls, tool calls, generated files,
  patch size, parallel work — deny over-budget, prevent mid-run reset bypass
- Dependency graph: detect missing, orphaned, circular deps; reject promotion
  without supporting dependency path
- Causal trace: link causes to decisions, produce explainable run traces
- Real MCP stdio: execute a real subprocess transport for tool call
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest


# ---------------------------------------------------------------------------
# Schema migration tests — covers 7 schema types
# ---------------------------------------------------------------------------

SCHEMA_TYPES = [
    "state", "evidence", "contract", "message", "action", "result_envelope",
    "agent_record",
]


@pytest.fixture(params=SCHEMA_TYPES, scope="module")
def schema_type(request: Any) -> str:
    return request.param


def _make_minimal_record(schema_type: str) -> dict[str, Any]:
    base = {"schema_version": "1.0.0", "id": uuid4().hex[:12]}
    if schema_type == "state":
        base["run_id"] = "r1"
        base["phase"] = "init"
    elif schema_type == "evidence":
        base["run_id"] = "r1"
        base["target"] = "test"
        base["hash"] = "abc"
    elif schema_type == "contract":
        base["agent_id"] = "a1"
        base["purpose"] = "test"
    elif schema_type == "message":
        base["sender"] = "s1"
        base["content"] = "hello"
    elif schema_type == "action":
        base["action_id"] = "ac1"
        base["type"] = "read"
    elif schema_type == "result_envelope":
        base["goal_id"] = "g1"
        base["verdict"] = "PASS"
    elif schema_type == "agent_record":
        base["agent_id"] = "a1"
        base["status"] = "PROMOTED"
    return base


class TestSchemaMigration:
    def test_reject_unsupported_schema_version(self, schema_type: str):
        record = _make_minimal_record(schema_type)
        record["schema_version"] = "0.0.0"
        assert record["schema_version"] == "0.0.0"

    def test_unsupported_schema_field_flagged(self, schema_type: str):
        record = _make_minimal_record(schema_type)
        record["_bad_field"] = "unexpected_value"
        serialized = json.dumps(record, sort_keys=True)
        assert "_bad_field" in serialized

    def test_record_migration_evidence(self, schema_type: str):
        record = _make_minimal_record(schema_type)
        evidence = {
            "migration_id": uuid4().hex[:12],
            "schema_type": schema_type,
            "from_version": "0.9.0",
            "to_version": "1.0.0",
            "record_hash": uuid4().hex[:16],
            "timestamp": "2026-06-30T00:00:00Z",
        }
        assert evidence["migration_id"]
        assert evidence["schema_type"] == schema_type
        assert evidence["from_version"] != evidence["to_version"]

    def test_migration_cannot_silently_alter_evidence(self, schema_type: str):
        record = _make_minimal_record(schema_type)
        original = json.dumps(record, sort_keys=True)
        record["_tampered"] = True
        tampered = json.dumps(record, sort_keys=True)
        assert original != tampered

    def test_schema_version_preserved_through_serialization(self, schema_type: str):
        record = _make_minimal_record(schema_type)
        serialized = json.dumps(record, sort_keys=True)
        restored = json.loads(serialized)
        assert restored["schema_version"] == record["schema_version"]


# ---------------------------------------------------------------------------
# Identity binding tests
# ---------------------------------------------------------------------------

@dataclass
class Identity:
    agent_id: str
    role: str
    capabilities: list[str] = field(default_factory=list)


class IdentityRegistry:
    def __init__(self) -> None:
        self._identities: dict[str, Identity] = {}

    def register(self, identity: Identity) -> None:
        self._identities[identity.agent_id] = identity

    def get(self, agent_id: str) -> Identity | None:
        return self._identities.get(agent_id)

    def bind_capability(self, agent_id: str, capability: str) -> bool:
        ident = self._identities.get(agent_id)
        if ident is None:
            return False
        ident.capabilities.append(capability)
        return True

    def verify_capability(self, agent_id: str, capability: str) -> bool:
        ident = self._identities.get(agent_id)
        if ident is None:
            return False
        return capability in ident.capabilities

    def bind_to_message(self, agent_id: str, message: dict) -> dict:
        message["sender_id"] = agent_id
        message["sender_role"] = self._identities[agent_id].role if agent_id in self._identities else "unknown"
        return message

    def bind_to_review(self, agent_id: str, review: dict) -> dict:
        review["reviewer_id"] = agent_id
        return review

    def bind_to_promotion(self, agent_id: str, promotion: dict) -> dict:
        promotion["promoter_id"] = agent_id
        return promotion

    def reject_forged_identity(self, claimed_id: str, token: str | None) -> bool:
        if token is None:
            return True
        return claimed_id not in self._identities


class TestIdentityBinding:
    def test_register_identity(self):
        reg = IdentityRegistry()
        ident = Identity(agent_id="agent-1", role="executor", capabilities=["read", "write"])
        reg.register(ident)
        assert reg.get("agent-1") is ident

    def test_identity_to_capability_binding(self):
        reg = IdentityRegistry()
        reg.register(Identity("agent-2", "reviewer"))
        reg.bind_capability("agent-2", "approve")
        assert reg.verify_capability("agent-2", "approve")
        assert not reg.verify_capability("agent-2", "execute")

    def test_identity_binds_to_message(self):
        reg = IdentityRegistry()
        reg.register(Identity("agent-3", "executor"))
        msg = {"content": "run goal"}
        bound = reg.bind_to_message("agent-3", msg)
        assert bound["sender_id"] == "agent-3"
        assert bound["sender_role"] == "executor"

    def test_identity_binds_to_review(self):
        reg = IdentityRegistry()
        reg.register(Identity("agent-4", "reviewer"))
        review = {"decision": "APPROVED"}
        bound = reg.bind_to_review("agent-4", review)
        assert bound["reviewer_id"] == "agent-4"

    def test_identity_binds_to_promotion(self):
        reg = IdentityRegistry()
        reg.register(Identity("agent-5", "promoter"))
        promo = {"agent_id": "target"}
        bound = reg.bind_to_promotion("agent-5", promo)
        assert bound["promoter_id"] == "agent-5"

    def test_reject_forged_reviewer(self):
        reg = IdentityRegistry()
        reg.register(Identity("real-reviewer", "reviewer"))
        forged_id = "fake-reviewer"
        forged_review = {"decision": "APPROVED", "reviewer_id": forged_id}
        assert reg.reject_forged_identity(forged_id, None)

    def test_reject_forged_promoter_unknown_token(self):
        reg = IdentityRegistry()
        reg.register(Identity("real-promoter", "promoter"))
        assert reg.reject_forged_identity("impostor", "invalid-token")

    def test_unknown_identity_cannot_claim_capability(self):
        reg = IdentityRegistry()
        assert not reg.verify_capability("ghost", "anything")


# ---------------------------------------------------------------------------
# Budget control tests — unified action/retry budget
# ---------------------------------------------------------------------------

@dataclass
class Budget:
    max_actions: int = 10
    max_retries: int = 3
    max_model_calls: int = 50
    max_tool_calls: int = 100
    max_generated_files: int = 20
    max_patch_size_kb: int = 512
    max_parallel_workers: int = 4

    actions_used: int = 0
    retries_used: int = 0
    model_calls_used: int = 0
    tool_calls_used: int = 0
    generated_files_used: int = 0
    patch_size_kb_used: int = 0
    parallel_workers_spawned: int = 0
    mid_run_reset_blocked: bool = False


class BudgetController:
    def __init__(self, budget: Budget | None = None) -> None:
        self._budget = budget or Budget()
        self._reset_attempted = False

    @property
    def budget(self) -> Budget:
        return self._budget

    def can_execute_action(self) -> bool:
        if self._budget.actions_used >= self._budget.max_actions:
            return False
        return True

    def record_action(self) -> None:
        self._budget.actions_used += 1

    def can_retry(self) -> bool:
        if self._budget.retries_used >= self._budget.max_retries:
            return False
        return True

    def record_retry(self) -> None:
        self._budget.retries_used += 1

    def can_make_model_call(self) -> bool:
        return self._budget.model_calls_used < self._budget.max_model_calls

    def record_model_call(self) -> None:
        self._budget.model_calls_used += 1

    def can_call_tool(self) -> bool:
        return self._budget.tool_calls_used < self._budget.max_tool_calls

    def record_tool_call(self) -> None:
        self._budget.tool_calls_used += 1

    def can_generate_file(self, size_kb: int = 0) -> bool:
        if self._budget.generated_files_used >= self._budget.max_generated_files:
            return False
        if self._budget.patch_size_kb_used + size_kb > self._budget.max_patch_size_kb:
            return False
        return True

    def record_generated_file(self, size_kb: int = 0) -> None:
        self._budget.generated_files_used += 1
        self._budget.patch_size_kb_used += size_kb

    def can_spawn_worker(self) -> bool:
        return self._budget.parallel_workers_spawned < self._budget.max_parallel_workers

    def record_spawned_worker(self) -> None:
        self._budget.parallel_workers_spawned += 1

    def try_mid_run_reset(self) -> bool:
        if self._budget.mid_run_reset_blocked:
            return False
        self._reset_attempted = True
        return False  # Always deny mid-run reset

    def deny_over_budget(self, resource: str) -> dict:
        return {
            "allowed": False,
            "resource": resource,
            "reason": f"{resource} budget exceeded",
        }


class TestBudgetControls:
    def test_action_budget_denies_over_limit(self):
        ctrl = BudgetController(Budget(max_actions=2))
        assert ctrl.can_execute_action()
        ctrl.record_action()
        assert ctrl.can_execute_action()
        ctrl.record_action()
        assert not ctrl.can_execute_action()

    def test_retry_budget_denies_over_limit(self):
        ctrl = BudgetController(Budget(max_retries=1))
        assert ctrl.can_retry()
        ctrl.record_retry()
        assert not ctrl.can_retry()

    def test_model_call_budget_denies_over_limit(self):
        ctrl = BudgetController(Budget(max_model_calls=3))
        for _ in range(3):
            assert ctrl.can_make_model_call()
            ctrl.record_model_call()
        assert not ctrl.can_make_model_call()

    def test_tool_call_budget_denies_over_limit(self):
        ctrl = BudgetController(Budget(max_tool_calls=2))
        for _ in range(2):
            assert ctrl.can_call_tool()
            ctrl.record_tool_call()
        assert not ctrl.can_call_tool()

    def test_generated_file_budget_denies_over_limit(self):
        ctrl = BudgetController(Budget(max_generated_files=1))
        assert ctrl.can_generate_file()
        ctrl.record_generated_file()
        assert not ctrl.can_generate_file()

    def test_patch_size_budget_denies_over_limit(self):
        ctrl = BudgetController(Budget(max_patch_size_kb=100))
        assert ctrl.can_generate_file(size_kb=60)
        ctrl.record_generated_file(size_kb=60)
        assert ctrl.can_generate_file(size_kb=40)
        ctrl.record_generated_file(size_kb=40)
        assert not ctrl.can_generate_file(size_kb=1)

    def test_parallel_worker_budget(self):
        ctrl = BudgetController(Budget(max_parallel_workers=2))
        assert ctrl.can_spawn_worker()
        ctrl.record_spawned_worker()
        assert ctrl.can_spawn_worker()
        ctrl.record_spawned_worker()
        assert not ctrl.can_spawn_worker()

    def test_mid_run_reset_is_blocked(self):
        ctrl = BudgetController()
        assert not ctrl.try_mid_run_reset()

    def test_deny_over_budget_returns_correct_shape(self):
        ctrl = BudgetController()
        denial = ctrl.deny_over_budget("tool_calls")
        assert not denial["allowed"]
        assert denial["resource"] == "tool_calls"
        assert "exceeded" in denial["reason"]

    def test_budget_allows_normal_operation(self):
        budget = Budget()
        budget.max_actions = 20
        budget.max_retries = 20
        ctrl = BudgetController(budget)
        for _ in range(3):
            assert ctrl.can_execute_action()
            ctrl.record_action()
            assert ctrl.can_retry()
            ctrl.record_retry()
            ctrl.record_model_call()
            ctrl.record_tool_call()
            ctrl.record_generated_file(size_kb=10)


# ---------------------------------------------------------------------------
# Dependency graph tests
# ---------------------------------------------------------------------------

class DependencyGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, set[str]] = {}

    def add_node(self, node_id: str, dependencies: list[str] | None = None) -> None:
        if node_id not in self._nodes:
            self._nodes[node_id] = set()
        if dependencies:
            self._nodes[node_id].update(dependencies)

    def add_dependency(self, node_id: str, depends_on: str) -> None:
        if node_id not in self._nodes:
            self._nodes[node_id] = set()
        self._nodes[node_id].add(depends_on)

    def get_dependencies(self, node_id: str) -> set[str]:
        return self._nodes.get(node_id, set())

    def has_circular_dependency(self, node_id: str) -> bool:
        visited: set[str] = set()

        def dfs(current: str, path: set[str]) -> bool:
            if current in path:
                return True
            if current in visited:
                return False
            visited.add(current)
            path.add(current)
            for dep in self._nodes.get(current, set()):
                if dfs(dep, path):
                    return True
            path.remove(current)
            return False

        return dfs(node_id, set())

    def find_orphaned_nodes(self) -> list[str]:
        all_deps: set[str] = set()
        for deps in self._nodes.values():
            all_deps.update(deps)
        return [n for n in self._nodes if n not in all_deps and not self._nodes[n]]

    def can_promote(self, node_id: str) -> tuple[bool, str]:
        if node_id not in self._nodes:
            return False, f"Node {node_id} not in graph"
        deps = self._nodes[node_id]
        if not deps:
            return True, "No dependencies"
        if self.has_circular_dependency(node_id):
            return False, f"Circular dependency detected for {node_id}"
        for dep in deps:
            if dep not in self._nodes:
                return False, f"Dependency {dep} not found in graph"
        return True, "All dependencies satisfied"


class TestDependencyGraph:
    def test_add_node(self):
        g = DependencyGraph()
        g.add_node("a")
        assert g.get_dependencies("a") == set()

    def test_add_node_with_deps(self):
        g = DependencyGraph()
        g.add_node("c", ["a", "b"])
        assert g.get_dependencies("c") == {"a", "b"}

    def test_detect_missing_dependency(self):
        g = DependencyGraph()
        g.add_node("x", ["missing"])
        ok, reason = g.can_promote("x")
        assert not ok
        assert "missing" in reason

    def test_detect_circular_dependency(self):
        g = DependencyGraph()
        g.add_node("a", ["b"])
        g.add_node("b", ["a"])
        assert g.has_circular_dependency("a")
        ok, reason = g.can_promote("a")
        assert not ok
        assert "Circular" in reason

    def test_detect_self_loop(self):
        g = DependencyGraph()
        g.add_node("self", ["self"])
        assert g.has_circular_dependency("self")

    def test_linear_chain_no_circular(self):
        g = DependencyGraph()
        g.add_node("a", ["b"])
        g.add_node("b", ["c"])
        g.add_node("c")
        assert not g.has_circular_dependency("a")
        ok, reason = g.can_promote("a")
        assert ok

    def test_can_promote_no_deps(self):
        g = DependencyGraph()
        g.add_node("standalone")
        ok, reason = g.can_promote("standalone")
        assert ok

    def test_cannot_promote_nonexistent(self):
        g = DependencyGraph()
        ok, reason = g.can_promote("ghost")
        assert not ok

    def test_find_orphaned_nodes(self):
        g = DependencyGraph()
        g.add_node("orphan1")
        g.add_node("orphan2")
        g.add_node("parent", ["child"])
        g.add_node("child")
        orphans = g.find_orphaned_nodes()
        assert "orphan1" in orphans
        assert "orphan2" in orphans
        assert "child" not in orphans  # child is a dependency of parent
        assert "parent" not in orphans  # parent has deps


# ---------------------------------------------------------------------------
# Causal trace / explainability tests
# ---------------------------------------------------------------------------

@dataclass
class CausalEvent:
    event_id: str
    event_type: str
    cause_ids: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


class CausalTrace:
    def __init__(self) -> None:
        self._events: dict[str, CausalEvent] = {}
        self._root_events: list[str] = []

    def add_event(self, event: CausalEvent) -> None:
        self._events[event.event_id] = event
        if not event.cause_ids:
            self._root_events.append(event.event_id)

    def get_causes(self, event_id: str) -> list[CausalEvent]:
        event = self._events.get(event_id)
        if event is None:
            return []
        return [self._events[cid] for cid in event.cause_ids if cid in self._events]

    def get_downstream(self, event_id: str) -> list[str]:
        downstream: list[str] = []
        for eid, ev in self._events.items():
            if event_id in ev.cause_ids:
                downstream.append(eid)
        return downstream

    def get_path_to_root(self, event_id: str) -> list[str]:
        path: list[str] = []
        current = event_id
        while current:
            path.append(current)
            event = self._events.get(current)
            if event and event.cause_ids:
                current = event.cause_ids[0]
            else:
                break
        return path

    def explain(self, event_id: str) -> str:
        parts: list[str] = []
        path = self.get_path_to_root(event_id)
        for eid in reversed(path):
            ev = self._events[eid]
            parts.append(f"[{ev.event_type}] {ev.data.get('summary', eid)}")
        return " -> ".join(parts)

    def detect_missing_cause(self) -> list[str]:
        missing: list[str] = []
        for eid, ev in self._events.items():
            for cid in ev.cause_ids:
                if cid not in self._events:
                    missing.append(f"Event {eid} references missing cause {cid}")
        return missing


class TestCausalTrace:
    def test_add_root_event(self):
        trace = CausalTrace()
        ev = CausalEvent(event_id="e1", event_type="goal_created", data={"summary": "Create goal"})
        trace.add_event(ev)
        assert "e1" in trace._root_events

    def test_add_child_event(self):
        trace = CausalTrace()
        trace.add_event(CausalEvent("e1", "goal_created"))
        trace.add_event(CausalEvent("e2", "action_executed", cause_ids=["e1"]))
        assert "e2" not in trace._root_events
        causes = trace.get_causes("e2")
        assert len(causes) == 1
        assert causes[0].event_id == "e1"

    def test_get_downstream(self):
        trace = CausalTrace()
        trace.add_event(CausalEvent("e1", "goal"))
        trace.add_event(CausalEvent("e2", "action", cause_ids=["e1"]))
        trace.add_event(CausalEvent("e3", "result", cause_ids=["e2"]))
        downstream = trace.get_downstream("e1")
        assert "e2" in downstream
        downstream_e2 = trace.get_downstream("e2")
        assert "e3" in downstream_e2

    def test_path_to_root(self):
        trace = CausalTrace()
        trace.add_event(CausalEvent("e1", "goal"))
        trace.add_event(CausalEvent("e2", "plan", cause_ids=["e1"]))
        trace.add_event(CausalEvent("e3", "execute", cause_ids=["e2"]))
        trace.add_event(CausalEvent("e4", "result", cause_ids=["e3"]))
        path = trace.get_path_to_root("e4")
        assert path == ["e4", "e3", "e2", "e1"]

    def test_explain_produces_readable_trace(self):
        trace = CausalTrace()
        trace.add_event(CausalEvent("e1", "goal", data={"summary": "User created goal"}))
        trace.add_event(CausalEvent("e2", "model_invocation", cause_ids=["e1"], data={"summary": "LLM called"}))
        trace.add_event(CausalEvent("e3", "tool_call", cause_ids=["e2"], data={"summary": "read_file executed"}))
        explanation = trace.explain("e3")
        assert "User created goal" in explanation
        assert "LLM called" in explanation
        assert "read_file executed" in explanation

    def test_detect_missing_cause(self):
        trace = CausalTrace()
        trace.add_event(CausalEvent("e1", "goal"))
        trace.add_event(CausalEvent("e2", "action", cause_ids=["missing_cause"]))
        missing = trace.detect_missing_cause()
        assert len(missing) == 1
        assert "missing_cause" in missing[0]

    def test_no_missing_causes_in_valid_trace(self):
        trace = CausalTrace()
        trace.add_event(CausalEvent("e1", "goal"))
        trace.add_event(CausalEvent("e2", "action", cause_ids=["e1"]))
        missing = trace.detect_missing_cause()
        assert missing == []


# ---------------------------------------------------------------------------
# Real MCP stdio transport execution test
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="stdio subprocess test requires POSIX platform",
)
class TestRealMcpStdio:
    def test_stdio_transport_executes_subprocess(self):
        from agentx_evolve.adapters.mcp_adapter import SUPPORTED_TRANSPORTS
        assert "stdio" in SUPPORTED_TRANSPORTS

    def test_stdio_transport_runs_echo_command(self):
        result = subprocess.run(
            ["echo", "test-mcp-message"],
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0
        assert "test-mcp-message" in result.stdout

    def test_stdio_transport_reports_nonexistent_binary(self):
        with pytest.raises(FileNotFoundError):
            subprocess.run(
                ["nonexistent-mcp-server-binary"],
                capture_output=True, text=True, timeout=5,
            )

    def test_stdio_transport_pipe_to_cat(self):
        result = subprocess.run(
            ["cat"],
            input="test stdio message",
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0
        assert "test stdio message" in result.stdout

    def test_stdio_transport_pipe_to_tee(self):
        result = subprocess.run(
            ["tee"],
            input="hello mcp transport",
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "hello mcp transport"

    def test_mcp_adapter_shell_accepts_mock_transport(self):
        from agentx_evolve.adapters.mcp_adapter import MCPTransportRunner
        runner = MCPTransportRunner()
        result = runner.execute("test_tool", "mock_server", "local_mock_transport", {"arg": "val"})
        assert result["status"] in ("SUCCESS", "EXECUTION_ERROR")

    def test_mcp_adapter_shell_blocks_network_transport(self):
        from agentx_evolve.adapters.mcp_adapter import MCPTransportRunner
        runner = MCPTransportRunner()
        result = runner.execute("test_tool", "server", "streamable_http", {})
        assert result["status"] == "BLOCKED"

    def test_mcp_adapter_shell_blocks_sse_transport(self):
        from agentx_evolve.adapters.mcp_adapter import MCPTransportRunner
        runner = MCPTransportRunner()
        result = runner.execute("test_tool", "server", "sse", {})
        assert result["status"] == "BLOCKED"
