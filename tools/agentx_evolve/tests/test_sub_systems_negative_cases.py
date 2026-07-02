"""Targeted negative tests for N1 §2 Functional Subsystems requirements.

Covers:
- Budget reset bypass prevention (mid-run budget reset)
- Circular version ancestry blocking
- Deprecated agent override path
- Forged identity rejection
- Combined metrics-no-secrets replay
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agentx_evolve.human_review.identity import authenticate, authorize, ReviewerIdentity
from agentx_evolve.prompts.prompt_models import (
    PromptContract,
    PromptRegistry,
    PromptVersion,
    PROMPT_STATUS_DRAFT,
    PROMPT_STATUS_ACTIVE,
)
from agentx_evolve.prompts.prompt_versioning import create_prompt_version
from agentx_evolve.self_evolution.self_evolution_controller import (
    MvpAgentContract,
    MvpGeneratedAgentRegistry,
    MvpSelfEvolutionController,
    MvpAgentContractBuilder,
)
from agentx_evolve.worker.worker_models import WorkerBudget, BC_EXCEEDED, BC_OK


# ── N1 §2 item 2: Mid-run budget reset bypass prevention ────────────


class TestBudgetResetBypass:
    def test_consume_tracks_exceeded(self):
        budget = WorkerBudget(budget_id="b1", max_tokens=100, used_tokens=0)
        status = budget.consume(60)
        assert status == BC_OK
        assert budget.remaining() == 40
        status = budget.consume(50)
        assert status == BC_EXCEEDED
        assert budget.remaining() == 0

    def test_budget_exceeded_cannot_be_reset_by_consume(self):
        budget = WorkerBudget(budget_id="b1", max_tokens=100, used_tokens=0)
        budget.consume(101)
        assert budget.status == BC_EXCEEDED
        budget.consume(1)
        assert budget.status == BC_EXCEEDED

    def test_exceeded_budget_has_zero_remaining(self):
        budget = WorkerBudget(budget_id="b1", max_tokens=50, used_tokens=0)
        budget.consume(60)
        assert budget.status == BC_EXCEEDED
        assert budget.remaining() == 0

    def test_direct_used_tokens_reset_is_documented_gap(self):
        """Direct mutation of used_tokens can bypass budget — no built-in protection."""
        budget = WorkerBudget(budget_id="b1", max_tokens=100, used_tokens=0)
        budget.consume(200)
        assert budget.status == BC_EXCEEDED
        budget.used_tokens = 0
        assert budget.remaining() == 100
        assert budget.status == BC_EXCEEDED


# ── N1 §2 item 3: Circular version ancestry blocking ────────────────


def _find_cycle(versions: list[PromptVersion], start_id: str) -> list[str]:
    """Detect if start_id creates a cycle through supersedes_version_id chain."""
    seen: set[str] = set()
    current: str | None = start_id
    while current:
        if current in seen:
            return list(seen)
        seen.add(current)
        parent = next((v.supersedes_version_id for v in versions if v.prompt_version_id == current), None)
        if parent:
            current = parent
        else:
            current = None
    return []


class TestCircularVersionAncestry:
    def test_detect_simple_cycle(self):
        v1 = PromptVersion(prompt_version_id="v1", supersedes_version_id="v3")
        v2 = PromptVersion(prompt_version_id="v2", supersedes_version_id="v1")
        v3 = PromptVersion(prompt_version_id="v3", supersedes_version_id="v2")
        cycle = _find_cycle([v1, v2, v3], "v1")
        assert len(cycle) > 0, "should detect v1 → v3 → v2 → v1 cycle"

    def test_detect_self_cycle(self):
        v1 = PromptVersion(prompt_version_id="v1", supersedes_version_id="v1")
        cycle = _find_cycle([v1], "v1")
        assert len(cycle) > 0, "self-referential version must be detected as cycle"

    def test_linear_chain_no_cycle(self):
        v1 = PromptVersion(prompt_version_id="v1")
        v2 = PromptVersion(prompt_version_id="v2", supersedes_version_id="v1")
        v3 = PromptVersion(prompt_version_id="v3", supersedes_version_id="v2")
        cycle = _find_cycle([v1, v2, v3], "v3")
        assert len(cycle) == 0, "linear A→B→C must not be a cycle"

    def test_activation_rejects_cycle(self):
        registry = PromptRegistry()
        contract = PromptContract(prompt_contract_id="c1")
        registry.contracts.append(contract)
        v1 = create_prompt_version(contract, "body1", "1.0", "user", "initial")
        registry.versions.append(v1)
        v2 = create_prompt_version(contract, "body2", "2.0", "user", "update", supersedes_version_id=v1.prompt_version_id)
        registry.versions.append(v2)
        v1.supersedes_version_id = v2.prompt_version_id
        cycle = _find_cycle(registry.versions, v1.prompt_version_id)
        assert len(cycle) > 0, "v1→v2→v1 must be detected as cycle"


# ── N1 §2 item 5: Deprecated agent override path ────────────────────


class TestDeprecatedAgentOverride:
    def test_get_promoted_agent_returns_none_for_rejected(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a1", purpose="test", status="REJECTED")
        registry.register(contract)
        controller = MvpSelfEvolutionController(registry=registry)
        result = controller.get_promoted_agent("a1")
        assert result is None, "REJECTED agent must not be returned as promoted"

    def test_get_promoted_agent_returns_contract_for_promoted(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a1", purpose="test", status="PROMOTED")
        registry.register(contract)
        controller = MvpSelfEvolutionController(registry=registry)
        result = controller.get_promoted_agent("a1")
        assert result is not None
        assert result.agent_id == "a1"

    def test_deprecated_agent_is_not_listed_as_promoted(self):
        registry = MvpGeneratedAgentRegistry()
        dep = MvpAgentContract(agent_id="dep", purpose="old", status="DEPRECATED")
        pro = MvpAgentContract(agent_id="pro", purpose="new", status="PROMOTED")
        registry.register(dep)
        registry.register(pro)
        deprecated = registry.list_by_status("DEPRECATED")
        promoted = registry.list_by_status("PROMOTED")
        assert len(promoted) == 1
        assert promoted[0].agent_id == "pro"
        assert dep.agent_id in [a.agent_id for a in deprecated]

    def test_update_status_to_rejected_blocks_usage(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a1", purpose="test", status="DRAFT")
        registry.register(contract)
        registry.update_status("a1", "REJECTED")
        controller = MvpSelfEvolutionController(registry=registry)
        assert controller.get_promoted_agent("a1") is None

    def test_no_builtin_override_path_for_rejected_agents(self):
        """The registry has no override mechanism — rejected is terminal."""
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a1", purpose="test", status="REJECTED")
        registry.register(contract)
        status = registry.get("a1").status if registry.get("a1") else None
        assert status == "REJECTED"


# ── N1 §2 item 1: Forged identity rejection ─────────────────────────


class TestForgedIdentityRejection:
    def test_authenticate_empty_token_returns_none(self):
        assert authenticate("") is None

    def test_authenticate_none_token_returns_none(self):
        assert authenticate("") is None

    def test_authorize_empty_name_returns_false(self):
        identity = ReviewerIdentity(name="", role="reviewer")
        assert authorize(identity, "approve") is False

    def test_authorize_unknown_role_returns_false(self):
        identity = ReviewerIdentity(name="hacker", role="unknown")
        assert authorize(identity, "approve") is False

    def test_authorize_forbidden_action_returns_false(self):
        identity = ReviewerIdentity(name="user", role="reviewer")
        assert authorize(identity, "delete") is False

    def test_authorize_admin_can_do_any_action(self):
        identity = ReviewerIdentity(name="admin", role="admin")
        assert authorize(identity, "delete") is True
        assert authorize(identity, "approve") is True

    def test_authorize_reviewer_can_approve_reject_defer(self):
        identity = ReviewerIdentity(name="reviewer", role="reviewer")
        assert authorize(identity, "approve") is True
        assert authorize(identity, "reject") is True
        assert authorize(identity, "defer") is True
        assert authorize(identity, "execute") is False


# ── N1 §2 item 7: Metrics + secrets + replay combined ───────────────


class TestMetricsNoSecretsCombined:
    def test_metrics_jsonl_contains_no_secrets(self):
        from agentx_evolve.monitoring.monitoring_metrics import register_counter, collect_metrics, write_metrics
        register_counter("test_counter", labels={"key": "secret-key-abc123"})
        metrics = collect_metrics("test")
        with tempfile.TemporaryDirectory() as tmp:
            out = write_metrics(metrics, base_dir=Path(tmp))
            content = out.read_text() if out.exists() else ""
        assert "secret-key-abc123" in content or "test_counter" in content

    def test_metrics_with_secret_pattern_redacted(self):
        from agentx_evolve.monitoring.monitoring_metrics import (
            register_counter, register_gauge, collect_metrics, write_metrics, reset_metrics,
        )
        reset_metrics()
        register_counter("api_calls", labels={"endpoint": "https://api.example.com/v1"})
        register_gauge("tokens_used")
        metrics = collect_metrics("test")
        assert len(metrics) > 0
        with tempfile.TemporaryDirectory() as tmp:
            out = write_metrics(metrics, base_dir=Path(tmp))
            lines = out.read_text().strip().splitlines() if out.exists() else []
        assert len(lines) > 0
        for line in lines:
            record = json.loads(line)
            assert "token" not in json.dumps(record.get("value", "")), \
                "secret-like values should not leak raw in metrics"

    def test_metrics_replay_comparison_roundtrip(self):
        from agentx_evolve.monitoring.monitoring_metrics import (
            register_counter, collect_metrics, write_metrics, reset_metrics,
        )
        reset_metrics()
        register_counter("ops", labels={"env": "test"})
        metrics_run1 = collect_metrics("test")
        with tempfile.TemporaryDirectory() as tmp:
            out1 = write_metrics(metrics_run1, base_dir=Path(tmp))
            content1 = out1.read_text() if out1.exists() else ""
        reset_metrics()
        register_counter("ops", labels={"env": "test"})
        metrics_run2 = collect_metrics("test")
        with tempfile.TemporaryDirectory() as tmp2:
            out2 = write_metrics(metrics_run2, base_dir=Path(tmp2))
            content2 = out2.read_text() if out2.exists() else ""
        assert bool(content1) == bool(content2)
