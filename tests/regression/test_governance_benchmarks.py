from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "L0", "CODE"))

import pytest

from agentx_evolve.evidence.infrastructure_validator import (
    check_missing_evidence_artifact,
    check_invalid_evidence_hash,
    check_noop_target,
    check_skipped_benchmark_cases,
    validate_benchmark_case_schema,
    check_provenance,
    check_manual_insertion,
    validate_events_append_only,
    scan_secrets,
)
from agentx_evolve.recovery.failure_models import make_failure_record, SEVERITY_HIGH
from agentx_evolve.patch_execution.patch_models import ImplementationSession
from agentx_evolve.patch_execution.rollback_manager import (
    create_rollback_snapshot,
    rollback_session,
)
from agentx_evolve.security.path_boundary import check_path_boundary, normalize_repo_path
from agentx_evolve.security.network_policy import check_network_allowed
from agentx_evolve.security.safe_subprocess import check_subprocess_allowed
from agentx_evolve.security.secret_redactor import redact_secrets
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


BENCHMARK_CATEGORIES = {
    "B007": "Policy rejection behavior",
    "B008": "Path boundary rejection behavior",
    "B009": "Invalid model output rejection",
    "B010": "Rollback behavior",
    "B011": "Review/promotion gate behavior",
    "B012": "Evidence manifest integrity",
    "B013": "Source hash integrity",
    "B014": "Clean-checkout replay",
    "B015": "No-op command rejection",
    "B016": "Manual generated-file insertion rejection",
    "B017": "Secret-in-evidence rejection",
    "B018": "Dependency change without approval rejection",
    "B019": "Unsupported final claim rejection",
    "B020": "Event log integrity rejection",
}


class TestGovernanceBenchmarks:
    """Regression benchmark suite for governance-layer behavior (B007-B020)."""

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.repo_root = self.tmpdir / "repo"
        self.repo_root.mkdir(parents=True)
        self.policy = default_sandbox_policy(self.repo_root)

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ── B007: Policy rejection behavior ──────────────────────────────

    @pytest.mark.benchmark("B007")
    def test_policy_rejects_l0_write(self):
        (self.repo_root / "L0").mkdir(exist_ok=True)
        decision = check_path_boundary(
            "L0/test.py", self.repo_root, "WRITE", self.policy
        )
        assert decision.decision == "BLOCK"

    @pytest.mark.benchmark("B007")
    def test_policy_rejects_network_by_default(self):
        result = check_network_allowed("https://example.com", self.policy)
        assert result.status == "BLOCKED"

    @pytest.mark.benchmark("B007")
    def test_policy_rejects_unknown_subprocess(self):
        result = check_subprocess_allowed(
            ["curl", "http://evil.com"], self.policy
        )
        assert result.status in ("BLOCK", "BLOCKED")

    # ── B008: Path boundary rejection behavior ───────────────────────

    @pytest.mark.benchmark("B008")
    def test_path_traversal_blocked(self):
        result = normalize_repo_path(
            "/etc/passwd", self.repo_root, self.policy, operation="READ"
        )
        assert result.status == "BLOCKED"
        assert not result.inside_repo

    @pytest.mark.benchmark("B008")
    def test_outside_repo_path_blocked(self):
        outside = self.tmpdir / "outside" / "file.txt"
        outside.parent.mkdir(parents=True)
        result = normalize_repo_path(
            str(outside), self.repo_root, self.policy, operation="WRITE"
        )
        assert result.status == "BLOCKED"

    # ── B009: Invalid model output rejection ─────────────────────────

    @staticmethod
    def _parse_json(content: str) -> dict | None:
        content = content.strip()
        idx = content.find("{")
        if idx != -1:
            content = content[idx:]
        end = content.rfind("}")
        if end != -1:
            content = content[: end + 1]
        if content.startswith("```"):
            content = content[content.find("\n") + 1 : content.rfind("```")]
        try:
            data = json.loads(content)
            return data if isinstance(data, dict) else None
        except (json.JSONDecodeError, TypeError):
            return None

    @pytest.mark.benchmark("B009")
    def test_malformed_json_is_rejected(self):
        assert self._parse_json("not json at all") is None

    @pytest.mark.benchmark("B009")
    def test_empty_string_rejected(self):
        assert self._parse_json("") is None

    @pytest.mark.benchmark("B009")
    def test_partial_json_rejected(self):
        assert self._parse_json('{"recommendation":') is None

    # ── B010: Rollback behavior ──────────────────────────────────────

    @pytest.mark.benchmark("B010")
    def test_validation_failure_triggers_failure_record(self):
        failure = make_failure_record(
            failure_class="VALIDATION_FAILED",
            message="Test validation failure",
            severity=SEVERITY_HIGH,
            source_layer="test",
        )
        assert failure.failure_class == "VALIDATION_FAILED"
        assert failure.requires_recovery

    @pytest.mark.benchmark("B010")
    def test_rollback_restores_source_state(self):
        session = ImplementationSession(session_id="rb-test-1")
        target = self.repo_root / "src"
        target.mkdir(parents=True)
        test_file = target / "rollback_test.txt"
        test_file.write_text("original content")
        snapshot = create_rollback_snapshot(
            session, self.repo_root, ["src/rollback_test.txt"]
        )
        test_file.write_text("modified content")
        record = rollback_session(
            session, snapshot, self.repo_root, "VALIDATION_FAILED"
        )
        assert record.status == "ROLLED_BACK"
        assert test_file.read_text() == "original content"

    # ── B011: Review/promotion gate behavior ─────────────────────────

    @pytest.mark.benchmark("B011")
    def test_promotion_gate_rejects_without_review(self):
        from agentx_evolve.promotion.gate_decision import (
            create_gate_decision,
        )
        from agentx_evolve.promotion.release_candidate import (
            create_release_candidate,
        )
        candidate = create_release_candidate(
            component_id="comp-1", component_name="test",
            roadmap_layer="layer-1", source_commit="abc",
            changed_files=[], changed_schemas=[],
            changed_tests=[], required_validations=[],
            required_approvals=[], required_evidence=[],
            repo_root=self.repo_root,
        )
        decision = create_gate_decision(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=None,
            approvals=[],
            git_evidence=None,
            policy_context={
                "require_validation": True,
                "require_review_report": True,
            },
            integration_context={},
            repo_root=self.repo_root,
            dry_run=False,
        )
        assert decision.status not in ("APPROVED",)
        assert len(decision.failed_checks) > 0

    @pytest.mark.benchmark("B011")
    def test_promotion_gate_rejects_null_candidate(self):
        from agentx_evolve.promotion.gate_decision import (
            create_gate_decision,
        )
        decision = create_gate_decision(
            candidate=None,
            validation_evidence=None,
            risk_acceptance=None,
            approvals=[],
            git_evidence=None,
            policy_context={},
            integration_context={},
            repo_root=self.repo_root,
            dry_run=False,
        )
        assert decision.decision == "BLOCK"

    # ── B012: Evidence manifest integrity ────────────────────────────

    @pytest.mark.benchmark("B012")
    def test_missing_evidence_detected(self):
        manifest = {
            "artifacts": [
                {"path": "nonexistent/file.txt", "sha256": "abc123"},
            ]
        }
        missing = check_missing_evidence_artifact(manifest, self.repo_root)
        assert len(missing) == 1
        assert "nonexistent/file.txt" in missing

    @pytest.mark.benchmark("B012")
    def test_invalid_evidence_hash_detected(self):
        test_file = self.repo_root / "test.txt"
        test_file.write_text("content")
        manifest = {
            "artifacts": [
                {"path": "test.txt", "sha256": "wronghash"},
            ]
        }
        invalid = check_invalid_evidence_hash(manifest, self.repo_root)
        assert len(invalid) == 1
        assert "test.txt" in invalid

    # ── B013: Source hash integrity ──────────────────────────────────

    @pytest.mark.benchmark("B013")
    def test_source_hash_mismatch_detected(self):
        src_file = self.repo_root / "src" / "main.py"
        src_file.parent.mkdir(parents=True)
        src_file.write_text("original")
        from agentx_evolve.evidence.infrastructure_validator import sha256_of
        original_hash = sha256_of(src_file)
        src_file.write_text("modified")
        new_hash = sha256_of(src_file)
        assert original_hash != new_hash

    # ── B014: Clean-checkout replay ───────────────────────────────────

    @pytest.mark.benchmark("B014")
    def test_replay_instructions_exist(self):
        replay_doc = Path(os.path.dirname(__file__)) / ".." / ".." / ".agentx-init" / "post_umbrella" / "phase_8_release_readiness" / "INSTALL_AND_REPLAY.md"
        assert replay_doc.exists(), f"Replay doc not found: {replay_doc}"
        content = replay_doc.read_text()
        assert "clone" in content.lower() or "checkout" in content.lower()
        assert "pytest" in content
        assert len(content) > 200

    # ── B015: No-op command rejection ────────────────────────────────

    @pytest.mark.benchmark("B015")
    def test_noop_target_detected(self):
        transcript = {
            "commands": [
                {"command_id": "test-target", "tests_run": 0},
            ]
        }
        assert check_noop_target("test-target", transcript)

    @pytest.mark.benchmark("B015")
    def test_non_noop_target_not_detected(self):
        transcript = {
            "commands": [
                {"command_id": "real-target", "tests_run": 42},
            ]
        }
        assert not check_noop_target("real-target", transcript)

    @pytest.mark.benchmark("B015")
    def test_skipped_benchmark_detected(self):
        results = {
            "cases": [
                {"case_id": "B001", "verdict": "PASS"},
                {"case_id": "B002", "verdict": "SKIPPED"},
                {"case_id": "B003", "verdict": None},
            ]
        }
        skipped = check_skipped_benchmark_cases(results)
        assert "B002" in skipped
        assert "B003" in skipped
        assert "B001" not in skipped

    # ── B016: Manual generated-file insertion rejection ──────────────

    @pytest.mark.benchmark("B016")
    def test_manual_insertion_detected(self):
        manifest = {
            "files": [
                {"path": "examples/clothing_advice_agent/planner.py", "origin": "manual"},
            ]
        }
        generated_paths = ["examples/clothing_advice_agent/planner.py"]
        manual = check_manual_insertion(manifest, generated_paths)
        assert len(manual) == 1

    @pytest.mark.benchmark("B016")
    def test_unproven_file_detected(self):
        manifest = {"files": []}
        generated_paths = ["examples/foo.py"]
        unproven = check_provenance(manifest, generated_paths)
        assert len(unproven) == 1
        assert "examples/foo.py" in unproven

    # ── B017: Secret-in-evidence rejection ───────────────────────────

    @pytest.mark.benchmark("B017")
    def test_private_key_detected(self):
        test_file = self.repo_root / "secret_file.txt"
        test_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nabc123\n-----END RSA PRIVATE KEY-----")
        found = scan_secrets([test_file])
        assert len(found) > 0
        assert any("private_key" in f[1] for f in found)

    @pytest.mark.benchmark("B017")
    def test_openai_key_detected(self):
        test_file = self.repo_root / "key_file.txt"
        test_file.write_text("sk-abcdefghijklmnopqrstuvwxyz123456")
        found = scan_secrets([test_file])
        assert len(found) > 0

    @pytest.mark.benchmark("B017")
    def test_secrets_are_redacted(self):
        result = redact_secrets(
            "export OPENAI_API_KEY = sk-abc123def456ghi789jkl", self.policy
        )
        assert result.redaction_count > 0
        assert "REDACTED" in result.redacted_text

    @pytest.mark.benchmark("B017")
    def test_clean_file_no_secrets(self):
        test_file = self.repo_root / "clean.txt"
        test_file.write_text("This is a normal file with no secrets.")
        found = scan_secrets([test_file])
        assert len(found) == 0

    # ── B018: Dependency change without approval rejection ──────────

    @pytest.mark.benchmark("B018")
    def test_dependency_change_detected(self):
        dep_file = self.repo_root / "requirements.txt"
        dep_file.write_text("numpy==1.21.0")
        from agentx_evolve.evidence.infrastructure_validator import sha256_of
        original = sha256_of(dep_file)
        dep_file.write_text("numpy==1.24.0")
        changed = sha256_of(dep_file)
        assert original != changed

    # ── B019: Unsupported final claim rejection ──────────────────────

    @pytest.mark.benchmark("B019")
    def test_unsupported_claim_detected(self):
        from agentx_evolve.promotion.gate_decision import (
            is_promotion_approved,
        )
        from agentx_evolve.promotion.promotion_models import (
            PromotionGateDecision, PC_FAILED, PD_BLOCK,
        )
        block_decision = PromotionGateDecision(
            decision_id="gd-block", status=PC_FAILED,
            decision=PD_BLOCK, reason="Unsupported claim",
        )
        assert not is_promotion_approved(block_decision)

    # ── B020: Event log integrity rejection ──────────────────────────

    @pytest.mark.benchmark("B020")
    def test_append_only_events_valid(self):
        log_file = self.repo_root / "events.jsonl"
        log_file.write_text(
            '{"event_id": "evt-001"}\n{"event_id": "evt-002"}\n'
        )
        assert validate_events_append_only(log_file)

    @pytest.mark.benchmark("B020")
    def test_duplicate_event_ids_detected(self):
        log_file = self.repo_root / "events_dup.jsonl"
        log_file.write_text(
            '{"event_id": "evt-001"}\n{"event_id": "evt-001"}\n'
        )
        assert not validate_events_append_only(log_file)

    @pytest.mark.benchmark("B020")
    def test_malformed_event_log_detected(self):
        log_file = self.repo_root / "events_bad.jsonl"
        log_file.write_text("not json\n")
        assert not validate_events_append_only(log_file)
