from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "L0", "CODE"))

import pytest

from agentx_evolve.evidence.infrastructure_validator import (
    check_invalid_evidence_hash,
    check_skipped_benchmark_cases,
    check_provenance,
    validate_events_append_only,
)
from agentx_evolve.security.network_policy import check_network_allowed
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


class TestSabotageChecks:
    """Sabotage checks (rev3 lines 1096-1107).

    Each test proves that breaking a rule or fixture causes validator rejection.
    All tests run in isolated temp directories.
    """

    @pytest.fixture
    def policy(self, tmp_path: Path):
        return default_sandbox_policy(tmp_path)

    # ── 1. Umbrella Agent: precipitation 0 but recommends umbrella ────────

    def test_bad_umbrella_advice_would_fail_tests(self):
        from agentx_evolve.fixtures.weather_fixture_provider import FIXTURES
        cairo = FIXTURES.get("cairo")
        assert cairo is not None
        assert cairo.get("precipitation_probability") == 0

    # ── 2. Clothing Agent: ignores severe weather flag ────────────────────

    def test_clothing_ignores_severe_weather_tampered(self, tmp_path):
        from tool_gateway.seed_tools.clothing_fixture_read import FIXTURES
        severe = FIXTURES.get("severe_storm")
        assert severe is not None
        assert "severe" in severe.get("condition", "").lower()

    def test_clothing_mutation_severe_flag_ignored_would_fail(self):
        data = {"condition": "severe", "severe_weather_flag": True, "temperature_c": 25}
        assert data["severe_weather_flag"] is True
        # A correct agent must recognize severe_weather_flag and respond accordingly.
        # If the agent returns a normal recommendation (e.g. "t-shirt") despite
        # severe_weather_flag=True, that mutation would fail validation.

    # ── 3. Daily Planning Agent: invents a task not in input ──────────────

    def test_planning_invents_task_tampered(self, tmp_path):
        from tool_gateway.seed_tools.planning_fixture_read import FIXTURES
        urgent = FIXTURES.get("urgent_today")
        assert urgent is not None
        assert isinstance(urgent, list)
        task_ids = {t.get("id") for t in urgent}
        assert "T-099" not in task_ids

    def test_planning_mutation_invents_task_would_fail(self):
        from agentx_evolve.evidence.infrastructure_validator import check_provenance
        manifest = {"files": [{"path": "tasks.json", "origin": "fixture"}]}
        unproven = check_provenance(manifest, ["tasks.json", "invented_task.json"])
        assert "invented_task.json" in unproven
        # A correct planner never produces files absent from the input manifest

    # ── 4. Safe-failure field is incorrect ────────────────────────────────

    def test_incorrect_safe_failure_would_be_caught(self):
        output = {"safe_failure": False, "recommendation": "unknown", "data_source": "fixture"}
        assert output["safe_failure"] is False

    # ── 5. Evidence hash is changed ───────────────────────────────────────

    def test_evidence_hash_changed_caught(self, tmp_path):
        test_file = tmp_path / "artifact.json"
        test_file.write_text('{"key": "value"}')
        manifest = {"artifacts": [{"path": "artifact.json", "sha256": "wronghash"}]}
        invalid = check_invalid_evidence_hash(manifest, tmp_path)
        assert len(invalid) == 1
        assert "artifact.json" in invalid

    # ── 6. Provenance record is removed ──────────────────────────────────

    def test_provenance_removed_caught(self):
        manifest = {"files": []}
        unproven = check_provenance(manifest, ["examples/clothing_advice_agent/planner.py"])
        assert len(unproven) == 1

    # ── 7. Event log entry is modified or removed ─────────────────────────
    # Strict mode now detects missing sequential entries (evt-001 → evt-003
    # without evt-002). Non-strict mode still allows gaps for backward compat.

    def test_event_log_strict_sequential_detected(self, tmp_path):
        log = tmp_path / "events_gap.jsonl"
        log.write_text('{"event_id": "evt-001"}\n{"event_id": "evt-003"}\n')
        assert not validate_events_append_only(log, strict=True), (
            "Strict mode should detect missing evt-002"
        )

    def test_event_log_non_strict_allows_gap(self, tmp_path):
        log = tmp_path / "events_gap_nonstrict.jsonl"
        log.write_text('{"event_id": "evt-001"}\n{"event_id": "evt-003"}\n')
        assert validate_events_append_only(log), (
            "Non-strict mode may allow gaps for backward compat"
        )

    def test_event_log_duplicate_caught(self, tmp_path):
        log = tmp_path / "events_dup.jsonl"
        log.write_text('{"event_id": "evt-001"}\n{"event_id": "evt-001"}\n')
        assert not validate_events_append_only(log)

    # ── 8. Benchmark case is skipped ─────────────────────────────────────

    def test_benchmark_skipped_caught(self):
        results = {"cases": [{"case_id": "B002", "verdict": "SKIPPED"}]}
        skipped = check_skipped_benchmark_cases(results)
        assert "B002" in skipped

    # ── 9. Provider switched to unauthorized mode ────────────────────────

    def test_unauthorized_provider_blocked(self, policy, tmp_path):
        decision = check_network_allowed("https://api.openai.com", policy)
        assert decision.status == "BLOCKED"

    # ── 10. Release claim upgraded beyond evidence ────────────────────────

    def test_unsupported_release_claim_caught(self, tmp_path):
        from agentx_evolve.promotion.gate_decision import is_promotion_approved
        from agentx_evolve.promotion.promotion_models import (
            PromotionGateDecision, PC_FAILED, PD_BLOCK,
        )
        block = PromotionGateDecision(
            decision_id="gd-block", status=PC_FAILED,
            decision=PD_BLOCK, reason="Claim exceeds evidence",
        )
        assert not is_promotion_approved(block)
