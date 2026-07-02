"""Validator-quality negative tests: prove shape-only JSON is rejected.

These tests create temporary directories, write shape-only (minimal/malformed)
JSON artifacts, run validators via subprocess, and verify the validators exit
nonzero. This avoids corrupting real proof artifacts.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

VALIDATOR_DIR = Path("tools/agentx_evolve/final_agentx")

VALIDATORS = {
    "acceptance_matrix": "validate_functional_agentx_acceptance_matrix.py",
    "final_verdict": "validate_functional_agentx_final_verdict.py",
    "ci_evidence": "validate_functional_agentx_ci_evidence.py",
    "evidence_manifest": "validate_functional_agentx_evidence_manifest.py",
    "anti_false_pass": "validate_functional_agentx_anti_false_pass.py",
    "replay": "validate_functional_agentx_replay.py",
    "review_binding": "validate_functional_agentx_review_evidence_binding.py",
    "no_overclaim": "validate_functional_agentx_no_overclaim.py",
    "gap_discovery": "validate_functional_agentx_gap_discovery.py",
    "command_transcript": "validate_functional_agentx_command_transcript.py",
}


def _run_validator(name: str, cwd: Path) -> int:
    vp = VALIDATOR_DIR / VALIDATORS[name]
    result = subprocess.run(
        [os.sys.executable, str(vp)],
        cwd=str(cwd),
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode


def _write_report(base: Path, name: str, data: dict) -> Path:
    p = base / ".agentx-init" / "reports" / "functional-agentx"
    p.mkdir(parents=True, exist_ok=True)
    (p / name).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return p


class TestShapeOnlyJSONRejected:
    def test_shape_only_acceptance_matrix(self) -> None:
        """Reject matrix that lacks schema_version and rows."""
        with tempfile.TemporaryDirectory(prefix="neg_acc_") as td:
            d = Path(td)
            _write_report(d, "acceptance_matrix.json", {"status": "PASS"})
            ec = _run_validator("acceptance_matrix", d)
            assert ec != 0, "acceptance_matrix validator should reject shape-only JSON"

    def test_static_pass_rows(self) -> None:
        """Reject matrix where all rows are PASS with no evidence."""
        with tempfile.TemporaryDirectory(prefix="neg_static_") as td:
            d = Path(td)
            _write_report(d, "acceptance_matrix.json", {
                "schema_version": "1.0",
                "total_rows": 20, "passed": 20, "blocked": 0,
                "rows": [{"id": f"FAKE-{i}", "description": "fake", "status": "PASS"} for i in range(20)],
            })
            ec = _run_validator("acceptance_matrix", d)
            assert ec != 0, "static PASS rows should be rejected"

    def test_final_verdict_missing_gates(self) -> None:
        """Reject verdict claiming PASS without passing gates."""
        with tempfile.TemporaryDirectory(prefix="neg_fv_") as td:
            d = Path(td)
            _write_report(d, "final_verdict.json", {
                "verdict": "PASS",
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
                "mandatory_gates_passed": 0,
                "mandatory_gates_total": 10,
                "run_id": "fa-neg-test-00000000",
            })
            ec = _run_validator("final_verdict", d)
            assert ec != 0, "verdict PASS with no gates passed should be rejected"

    def test_ci_success_no_run_id(self) -> None:
        """Reject CI success without workflow run id."""
        with tempfile.TemporaryDirectory(prefix="neg_ci_") as td:
            d = Path(td)
            _write_report(d, "ci_evidence_report.json", {
                "ci_status": "SUCCESS",
                "workflow_run_id": "",
                "conclusion": "success",
            })
            ec = _run_validator("ci_evidence", d)
            assert ec != 0, "CI success without run id should be rejected"

    def test_evidence_manifest_empty(self) -> None:
        """Reject manifest with no evidence refs."""
        with tempfile.TemporaryDirectory(prefix="neg_evm_") as td:
            d = Path(td)
            _write_report(d, "evidence_manifest.json", {
                "schema_version": "1.0",
                "total_refs": 0, "present": 0, "missing": 0,
                "evidence_refs": [],
            })
            ec = _run_validator("evidence_manifest", d)
            assert ec != 0, "empty evidence manifest should be rejected"

    def test_synthetic_command_transcript(self) -> None:
        """Reject transcript with no_recorder_fallback source."""
        with tempfile.TemporaryDirectory(prefix="neg_ct_") as td:
            d = Path(td)
            _write_report(d, "command_transcript.json", {
                "source": "no_recorder_fallback",
                "entries": [{"command": "fake", "exit_code": 0}],
            })
            _write_report(d, "evidence_manifest.json", {
                "schema_version": "1.0",
                "total_refs": 5, "present": 5, "missing": 0,
                "generated_evidence": [],
                "evidence_refs": [],
            })
            ec = _run_validator("review_binding", d)
            assert ec != 0, "synthetic transcript should be rejected"

    def test_no_attack_results_in_anti_false_pass(self) -> None:
        """Reject anti-false-pass with no attack results."""
        with tempfile.TemporaryDirectory(prefix="neg_afp_") as td:
            d = Path(td)
            _write_report(d, "anti_false_pass_report.json", {
                "schema_version": "1.0",
                "total_attacks": 0,
                "blocked": 0,
                "results": [],
            })
            ec = _run_validator("anti_false_pass", d)
            assert ec != 0, "empty anti-false-pass should be rejected"

    def test_gap_discovery_missing_report(self) -> None:
        """Reject missing gap discovery report."""
        with tempfile.TemporaryDirectory(prefix="neg_gd_") as td:
            d = Path(td)
            ec = _run_validator("gap_discovery", d)
            assert ec != 0, "gap discovery validator should reject missing report"


class TestGapDiscoveryAllowlist:
    """Tests for gap discovery allowlist binding and integrity."""

    def test_new_unallowlisted_overclaim_is_blocking(self) -> None:
        """A new OVERCLAIM_GAP finding in production code without allowlist entry must block."""
        from agentx_evolve.final_agentx.run_gap_discovery import classify_findings
        findings = [
            {"file": "src/core.py", "line": 1, "match": 'return {"status": "PASS"}',
             "description": "Hardcoded PASS", "tag": "OVERCLAIM_GAP"},
        ]
        result = classify_findings(findings)
        assert result[0]["status"] == "BLOCKING_GAP"

    def test_allowlisted_overclaim_is_allowed(self) -> None:
        """An OVERCLAIM_GAP finding matching an allowlist entry must be ALLOWED_WITH_REASON."""
        from agentx_evolve.final_agentx.run_gap_discovery import classify_findings
        # Self_evolution_controller.py with PROMOTED tag matches AL-O11
        findings = [
            {"file": "tools/agentx_evolve/self_evolution/self_evolution_controller.py",
             "line": 14, "match": '"REVIEWED", "PROMOTION_ELIGIBLE", "PROMOTED", "DEPRECATED",', "tag": "OVERCLAIM_GAP"},
        ]
        result = classify_findings(findings)
        assert result[0]["status"] == "ALLOWED_WITH_REASON", \
            f"Expected ALLOWED_WITH_REASON, got {result[0]['status']}"

    def test_non_critical_tag_is_non_critical(self) -> None:
        """A SAFETY_GAP finding without allowlist entry must be NON_CRITICAL (not blocking)."""
        from agentx_evolve.final_agentx.run_gap_discovery import classify_findings
        findings = [
            {"file": "src/unknown.py", "line": 1, "match": "subprocess.run",
             "tag": "SAFETY_GAP"},
        ]
        result = classify_findings(findings)
        assert result[0]["status"] == "NON_CRITICAL"

    def test_allowlist_entry_expiry_rejected(self) -> None:
        """An expired allowlist entry must fail allowlist integrity validation."""
        from agentx_evolve.final_agentx.validate_functional_agentx_gap_discovery import validate_allowlist_integrity
        import tempfile
        import json as j
        from pathlib import Path as P
        tests_dir = P(__file__).resolve().parent
        evolve_root = tests_dir.parent
        orig_path = evolve_root / "final_agentx" / "gap_discovery_allowlist.json"
        orig = j.loads(orig_path.read_text(encoding="utf-8"))
        # Add an expired entry
        orig["entries"].append({
            "id": "AL-EXPIRED",
            "file_glob": "**/*.py",
            "line": None,
            "tag": "OVERCLAIM_GAP",
            "pattern_hash": "0000000000000000000000000000000000000000000000000000000000000000",
            "reason": "Test expired entry",
            "owner": "test",
            "expires": "2020-01-01",
        })
        with tempfile.TemporaryDirectory() as td:
            tmp_path = P(td) / "test_allowlist.json"
            tmp_path.write_text(j.dumps(orig, indent=2), encoding="utf-8")
            import sys
            old_sys_path = list(sys.path)
            sys.path.insert(0, str(evolve_root.parent))
            try:
                from agentx_evolve.final_agentx.validate_functional_agentx_gap_discovery import ALLOWLIST_PATH
                old_alp = str(ALLOWLIST_PATH)
                import agentx_evolve.final_agentx.validate_functional_agentx_gap_discovery as vmod
                vmod.ALLOWLIST_PATH = tmp_path
                errs = validate_allowlist_integrity()
                vmod.ALLOWLIST_PATH = P(old_alp)
            finally:
                sys.path = old_sys_path
            expired_errs = [e for e in errs if "expired" in e.lower()]
            assert len(expired_errs) > 0, f"Expected expired entry error, got: {errs}"

    def test_allowlist_missing_fields_rejected(self) -> None:
        """An allowlist entry missing required fields must fail integrity validation."""
        from agentx_evolve.final_agentx.validate_functional_agentx_gap_discovery import validate_allowlist_integrity
        import tempfile
        import json as j
        from pathlib import Path as P
        import agentx_evolve.final_agentx.validate_functional_agentx_gap_discovery as vmod
        old_alp = str(vmod.ALLOWLIST_PATH)
        with tempfile.TemporaryDirectory() as td:
            bad = {
                "schema_version": "1.0",
                "artifact_type": "gap_discovery_allowlist",
                "entries": [{"id": "AL-BAD", "file_glob": "**/*.py"}],  # missing tag, owner, expires, pattern_hash
            }
            tmp_path = P(td) / "bad_allowlist.json"
            tmp_path.write_text(j.dumps(bad, indent=2), encoding="utf-8")
            vmod.ALLOWLIST_PATH = tmp_path
            errs = validate_allowlist_integrity()
            vmod.ALLOWLIST_PATH = P(old_alp)
            assert len(errs) > 0, f"Expected validation errors for missing fields, got: {errs}"


class TestAdditionalNegativeCases:
    """Additional negative tests for deeper gap closure."""

    def test_evidence_manifest_sha_mismatch(self) -> None:
        """Evidence manifest SHA-256 mismatch between manifest and actual file must fail."""
        with tempfile.TemporaryDirectory(prefix="neg_evm_sha_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)

            # Create an actual file
            actual_file = report_dir / "acceptance_matrix.json"
            actual_file.write_text(json.dumps({"a": 1}), encoding="utf-8")

            # Manifest with wrong SHA
            manifest = {
                "schema_version": "1.0",
                "artifact_type": "evidence_manifest",
                "run_id": "",
                "git_commit": "",
                "evidence_refs": [
                    {
                        "name": "acceptance_matrix.json",
                        "path": str(actual_file),
                        "namespace": "functional-agentx",
                        "producer": "test",
                        "validation_status": "VALIDATED",
                        "canonical_or_alias": "canonical",
                        "exists": True,
                        "required": True,
                        "sha256": "0" * 64,
                    }
                ],
            }
            (report_dir / "evidence_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            ec = _run_validator("evidence_manifest", d)
            assert ec != 0, "SHA-256 mismatch should be rejected"

    def test_evidence_manifest_alias_only_rejected(self) -> None:
        """A canonical file present only as alias must fail validation."""
        with tempfile.TemporaryDirectory(prefix="neg_evm_alias_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)

            actual_file = report_dir / "acceptance_matrix.json"
            actual_file.write_text(json.dumps({"a": 1}), encoding="utf-8")
            real_sha = hashlib.sha256(actual_file.read_bytes()).hexdigest()

            manifest = {
                "schema_version": "1.0",
                "artifact_type": "evidence_manifest",
                "run_id": "",
                "git_commit": "",
                "evidence_refs": [
                    {
                        "name": "acceptance_matrix.json",
                        "path": str(actual_file),
                        "namespace": "functional-agentx",
                        "producer": "test",
                        "validation_status": "VALIDATED",
                        "canonical_or_alias": "alias",
                        "exists": True,
                        "required": True,
                        "sha256": real_sha,
                    }
                ],
            }
            (report_dir / "evidence_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            ec = _run_validator("evidence_manifest", d)
            assert ec != 0, "alias-only canonical file should be rejected"

    def test_final_verdict_dirty_worktree_lowers(self) -> None:
        """Dirty worktree must be rejected by final verdict validator."""
        with tempfile.TemporaryDirectory(prefix="neg_fv_dirty_") as td:
            d = Path(td)
            _write_report(d, "final_verdict.json", {
                "verdict": "PASS",
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
                "dirty_worktree": True,
                "mandatory_gates_passed": 10,
                "mandatory_gates_total": 10,
                "run_id": "fa-neg-test-00000000",
                "stage_statuses": {
                    "AGENTX_REPO_MEMORY_MVP": {"verdict": "PASS"},
                    "AGENTX_GENERATED_AGENT_GIT_PROMOTION": {"verdict": "PASS"},
                },
            })
            _write_report(d, "classification_report.json", {
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
                "verdict": "PASS",
            })
            ec = _run_validator("final_verdict", d)
            assert ec != 0, "dirty worktree with PASS should be rejected"

    def test_authority_chain_legacy_conflict(self) -> None:
        """Legacy PASS artifact without evidence manifest import must fail authority chain."""
        with tempfile.TemporaryDirectory(prefix="neg_auth_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            legacy_dir = d / ".agentx-init" / "reports" / "final-acceptance"
            report_dir.mkdir(parents=True, exist_ok=True)
            legacy_dir.mkdir(parents=True, exist_ok=True)

            # Authoritative verdict
            (report_dir / "final_verdict.json").write_text(json.dumps({
                "verdict": "PASS",
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
                "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_final_verdict.py",
            }), encoding="utf-8")

            (report_dir / "classification_report.json").write_text(json.dumps({
                "verdict": "PASS",
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
            }), encoding="utf-8")

            # Legacy PASS with matching classification but not imported
            (legacy_dir / "final_verdict.json").write_text(json.dumps({
                "verdict": "PASS",
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
            }), encoding="utf-8")

            (report_dir / "evidence_manifest.json").write_text(json.dumps({
                "schema_version": "1.0",
                "artifact_type": "evidence_manifest",
                "evidence_refs": [],
            }), encoding="utf-8")

            import sys as _sys
            result = subprocess.run(
                [_sys.executable, "tools/agentx_evolve/final_agentx/validate_authority_chain.py"],
                cwd=str(d),
                capture_output=True, text=True, timeout=30,
            )
            assert result.returncode != 0, (
                f"Legacy conflict should be rejected, got exit {result.returncode}: "
                f"{result.stdout}{result.stderr}"
            )

    def test_stage_replay_governed_missing_fields(self) -> None:
        """Governed stage replay without agent_identity_hash must fail."""
        with tempfile.TemporaryDirectory(prefix="neg_rp_gov_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "governed-self-evolution"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "replay_report.json").write_text(json.dumps({
                "status": "PASS",
                "original_run_id": "orig-1",
                "replay_run_id": "replay-1",
                # Missing agent_identity_hash, contract_hash, goal_hash, etc.
            }), encoding="utf-8")
            ec = _run_validator("replay", d)
            assert ec != 0, "Governed replay missing fields should be rejected"

    def test_stage_replay_memory_missing_index_hash(self) -> None:
        """RepoMemory stage replay without memory_index_hash must fail."""
        with tempfile.TemporaryDirectory(prefix="neg_rp_mem_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "repo-memory-mvp"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "replay_report.json").write_text(json.dumps({
                "status": "PASS",
                "original_run_id": "orig-1",
                "replay_run_id": "replay-1",
                "artifact_hashes": {"acceptance_matrix.json": "abc", "final_verdict.json": "def"},
                # Missing memory_corpus_hash, memory_index_hash
            }), encoding="utf-8")
            ec = _run_validator("replay", d)
            assert ec != 0, "RepoMemory replay missing index hash should be rejected"

    def test_stage_replay_git_promotion_missing_patch_hash(self) -> None:
        """GitPromotion stage replay without git_patch_hash must fail."""
        with tempfile.TemporaryDirectory(prefix="neg_rp_git_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "generated-agent-git-promotion"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "replay_report.json").write_text(json.dumps({
                "status": "PASS",
                "original_run_id": "orig-1",
                "replay_run_id": "replay-1",
                "artifact_hashes": {"acceptance_matrix.json": "abc", "final_verdict.json": "def"},
                # Missing git_patch_hash, promotion_decision, diff_hash
            }), encoding="utf-8")
            ec = _run_validator("replay", d)
            assert ec != 0, "GitPromotion replay missing patch hash should be rejected"

    def test_afp_validator_crash_not_counted_as_block(self) -> None:
        """AFP attack with validator import/path failure must not be counted as blocked."""
        from agentx_evolve.final_agentx.run_functional_agentx_anti_false_pass_audit import _make_result
        # Simulate validator crash (import error): non-zero exit with Traceback
        crash_result = {"returncode": 1, "stdout": "",
                        "stderr": "Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>\nImportError: No module named 'nonexistent'",
                        "infrastructure_error": True}
        r = _make_result("Test validator crash", crash_result, "expected failure")
        assert not r.get("blocked"), "Validator import crash should not count as blocked"
        assert r.get("failure_reason_matched") is not True, \
            "Validator import crash should not match expected reason"
        assert r.get("infrastructure_error") is True, "Should be flagged as infrastructure error"

    def test_afp_validator_correctly_blocks_real_tamper(self) -> None:
        """AFP attack with genuine validator rejection must be counted as blocked."""
        from agentx_evolve.final_agentx.run_functional_agentx_anti_false_pass_audit import _make_result
        # Simulate real validator rejection: non-zero exit with expected substring in output
        valid_result = {"returncode": 1, "stdout": "",
                        "stderr": "error: missing evidence_refs",
                        "infrastructure_error": False}
        r = _make_result("Test real rejection", valid_result, "missing evidence_refs")
        assert r.get("blocked"), "Genuine validator rejection should count as blocked"
        assert r.get("failure_reason_matched") is True, \
            "Expected reason matched should be True"
        assert r.get("infrastructure_error") is False, "No infrastructure error"

    def test_final_verdict_stale_commit_rejected(self) -> None:
        """final_verdict.json from a different commit must be rejected."""
        from agentx_evolve.final_agentx.validate_functional_agentx_final_verdict import validate
        from agentx_evolve.final_agentx.validate_functional_agentx_final_verdict import REPORT_BASE as RB
        with tempfile.TemporaryDirectory(prefix="neg_fv_stale_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)
            RB.mkdir(parents=True, exist_ok=True)
            (report_dir / "final_verdict.json").write_text(json.dumps({
                "verdict": "PASS",
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
                "git_commit": "0000000000000000000000000000000000000000",
                "mandatory_gates_passed": 10,
                "mandatory_gates_total": 10,
                "run_id": "fa-stale-test",
                "stage_statuses": {
                    "AGENTX_REPO_MEMORY_MVP": {"verdict": "PASS"},
                    "AGENTX_GENERATED_AGENT_GIT_PROMOTION": {"verdict": "PASS"},
                },
            }), encoding="utf-8")
            (report_dir / "classification_report.json").write_text(json.dumps({
                "classification": "FUNCTIONAL_AGENTX_COMPLETE",
                "verdict": "PASS",
                "git_commit": "0000000000000000000000000000000000000000",
            }), encoding="utf-8")
            import sys
            orig_cwd = Path.cwd()
            os.chdir(str(d))
            try:
                errs = validate()
            finally:
                os.chdir(str(orig_cwd))
            stale_errs = [e for e in errs if "stale" in e.lower() or "Stale" in e]
            assert len(stale_errs) > 0, f"Expected stale commit error, got: {errs}"

    def test_ci_success_without_uploaded_artifact_ids(self) -> None:
        """CI evidence with SUCCESS but no uploaded_artifact_ids must fail."""
        with tempfile.TemporaryDirectory(prefix="neg_ci_up_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "ci_evidence_report.json").write_text(json.dumps({
                "ci_status": "SUCCESS",
                "workflow_status": "completed",
                "workflow_conclusion": "success",
                "workflow_run_id": "12345",
                "branch": "main",
                "commit_sha": "abc123",
                "workflow_name": "test",
                "artifact_ids": ["report1.json"],
                "uploaded_artifact_ids": [],
                "artifact_hashes": {},
                "raw_logs_hash_bound": False,
                "matrix": {"python-version": ["3.12"]},
            }), encoding="utf-8")
            ec = _run_validator("ci_evidence", d)
            assert ec != 0, "CI success without uploaded_artifact_ids should be rejected"

    def test_override_unrelated_evidence_file_denied(self) -> None:
        """Override with a valid-looking file for different agent or actor must fail."""
        from agentx_evolve.self_evolution.self_evolution_controller import (
            MvpAgentContract, MvpGeneratedAgentRegistry,
        )
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="target-agent", purpose="test", status="REJECTED")
        registry.register(contract)
        # Override using evidence file that claims to be for a different agent
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            import json
            json.dump({
                "evidence": True,
                "subject_agent_id": "wrong-agent",
                "actor": "test-actor",
                "capability": "override",
            }, f)
            ev_path = f.name
        try:
            ok = registry.override_rejected("target-agent", "DRAFT_OVERRIDE_REQUESTED", ev_path, "actor", "reason")
            assert not ok, "Override with evidence for wrong agent should be denied"
        finally:
            Path(ev_path).unlink(missing_ok=True)

    def test_transcript_zero_commands_rejected(self) -> None:
        """Transcript with zero commands must fail validation."""
        with tempfile.TemporaryDirectory(prefix="neg_ct_zero_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "command_transcript.json").write_text(json.dumps({
                "schema_version": "1.0",
                "artifact_type": "command_transcript",
                "source": "recorded",
                "total_commands": 0,
                "entries": [],
            }), encoding="utf-8")
            ec = _run_validator("command_transcript", d)
            assert ec != 0, "Transcript with zero commands should be rejected"

    def test_evidence_manifest_stale_run_id(self) -> None:
        """Evidence manifest with stale run_id must fail validation."""
        with tempfile.TemporaryDirectory(prefix="neg_evm_run_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)
            actual_file = report_dir / "acceptance_matrix.json"
            actual_file.write_text(json.dumps({"a": 1}), encoding="utf-8")
            real_sha = hashlib.sha256(actual_file.read_bytes()).hexdigest()
            manifest = {
                "schema_version": "1.0",
                "artifact_type": "evidence_manifest",
                "run_id": "fa-stale-0000000000000",
                "git_commit": "0000000000000000000000000000000000000000",
                "evidence_refs": [
                    {
                        "name": "acceptance_matrix.json",
                        "path": str(actual_file),
                        "namespace": "functional-agentx",
                        "producer": "test",
                        "validation_status": "VALIDATED",
                        "canonical_or_alias": "canonical",
                        "exists": True,
                        "required": True,
                        "sha256": real_sha,
                    }
                ],
            }
            (report_dir / "evidence_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            ec = _run_validator("evidence_manifest", d)
            assert ec != 0, "Evidence manifest with stale run_id should be rejected"

    def test_transcript_synthesized_argv_rejected(self) -> None:
        """Transcript with synthesized argv (missing argv field) must fail validation."""
        with tempfile.TemporaryDirectory(prefix="neg_ct_argv_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "command_transcript.json").write_text(json.dumps({
                "schema_version": "1.0",
                "artifact_type": "command_transcript",
                "source": "recorded",
                "total_commands": 1,
                "entries": [
                    {"command": "python3 test.py", "exit_code": 0, "mandatory": True},
                ],
            }), encoding="utf-8")
            (report_dir / "evidence_manifest.json").write_text(json.dumps({
                "schema_version": "1.0",
                "total_refs": 1, "present": 1, "missing": 0,
                "evidence_refs": [],
            }), encoding="utf-8")
            ec = _run_validator("command_transcript", d)
            assert ec != 0, "Transcript missing argv should be rejected"

    def test_transcript_command_string_only_rejected(self) -> None:
        """Transcript with command string but no stdout/stderr hashes must fail."""
        with tempfile.TemporaryDirectory(prefix="neg_ct_hash_") as td:
            d = Path(td)
            report_dir = d / ".agentx-init" / "reports" / "functional-agentx"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "command_transcript.json").write_text(json.dumps({
                "schema_version": "1.0",
                "artifact_type": "command_transcript",
                "source": "recorded",
                "total_commands": 1,
                "entries": [
                    {"command": "python3 test.py", "argv": ["python3", "test.py"],
                     "exit_code": 0, "mandatory": True, "cwd": "/tmp"},
                ],
            }), encoding="utf-8")
            (report_dir / "evidence_manifest.json").write_text(json.dumps({
                "schema_version": "1.0",
                "total_refs": 1, "present": 1, "missing": 0,
                "evidence_refs": [],
            }), encoding="utf-8")
            ec = _run_validator("command_transcript", d)
            assert ec != 0, "Transcript without stdout/stderr hashes should be rejected"
