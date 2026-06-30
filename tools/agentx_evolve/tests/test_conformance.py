from __future__ import annotations

import pytest
from agentx_evolve.adapters.conformance import AdapterConformance
from agentx_evolve.adapters.replay_policy import ReplayMode


class TestAdapterConformance:
    def test_schema_validation_passes_with_schemas(self):
        issues = AdapterConformance.check_schema_validation("test_adapter", ["schema_v1"])
        assert issues == []

    def test_schema_validation_fails_without_schemas(self):
        issues = AdapterConformance.check_schema_validation("test_adapter", [])
        assert "no schemas declared" in issues[0]

    def test_capability_declaration_passes_with_capabilities(self):
        issues = AdapterConformance.check_capability_declaration("test_adapter", ["read_tools"])
        assert issues == []

    def test_capability_declaration_fails_without_capabilities(self):
        issues = AdapterConformance.check_capability_declaration("test_adapter", [])
        assert "no capabilities declared" in issues[0]

    def test_security_envelope_passes_when_required(self):
        issues = AdapterConformance.check_security_envelope("test_adapter", requires_envelope=True)
        assert issues == []

    def test_security_envelope_fails_when_not_required(self):
        issues = AdapterConformance.check_security_envelope("test_adapter", requires_envelope=False)
        assert "must require security envelope" in issues[0]

    def test_failure_taxonomy_known_class_passes(self):
        issues = AdapterConformance.check_failure_taxonomy("model_timeout")
        assert issues == []

    def test_failure_taxonomy_unknown_class_fails(self):
        issues = AdapterConformance.check_failure_taxonomy("nonexistent_class")
        assert "unknown failure class" in issues[0]

    def test_replay_mode_deterministic_passes(self):
        issues = AdapterConformance.check_replay_mode("test", ReplayMode.DETERMINISTIC)
        assert issues == []

    def test_replay_mode_live_non_replayable_has_warning(self):
        issues = AdapterConformance.check_replay_mode("test", ReplayMode.LIVE_NON_REPLAYABLE)
        assert "recorded_replay fallback" in issues[0]

    def test_run_all_aggregates_issues(self):
        issues = AdapterConformance.run_all(
            adapter_id="bad_adapter",
            capabilities=[], schemas=[],
            requires_envelope=False,
            mode=ReplayMode.LIVE_NON_REPLAYABLE,
        )
        assert len(issues) >= 3
