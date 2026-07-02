from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from agentx_evolve.final_agentx import (
    REPORT_BASE,
    atomic_write_json,
    compute_sha256,
    ensure_report_dir,
    get_git_commit,
    get_run_id,
    load_json,
)


class TestHelpers:
    def test_get_run_id_format(self) -> None:
        rid = get_run_id()
        assert rid.startswith("fa-")
        parts = rid.split("-")
        assert len(parts) >= 3

    def test_get_git_commit(self) -> None:
        commit = get_git_commit()
        assert commit != "UNKNOWN"
        assert len(commit) == 40

    def test_compute_sha256(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(b'{"a": 1}')
            p = Path(f.name)
        try:
            h = compute_sha256(p)
            assert len(h) == 64
        finally:
            p.unlink(missing_ok=True)

    def test_atomic_write_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "test.json"
            atomic_write_json(p, {"key": "value"})
            assert p.exists()
            data = json.loads(p.read_text(encoding="utf-8"))
            assert data["key"] == "value"

    def test_load_json_valid(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({"ok": True}, f)
            p = Path(f.name)
        try:
            data = load_json(p)
            assert data is not None
            assert data["ok"] is True
        finally:
            p.unlink(missing_ok=True)

    def test_load_json_invalid(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("not json")
            p = Path(f.name)
        try:
            data = load_json(p)
            assert data is None
        finally:
            p.unlink(missing_ok=True)

    def test_ensure_report_dir(self) -> None:
        original = str(REPORT_BASE)
        test_base = Path(tempfile.mkdtemp()) / "reports"
        from agentx_evolve.final_agentx import REPORT_BASE as RB
        try:
            import agentx_evolve.final_agentx as fa
            fa.REPORT_BASE = test_base
            result = fa.ensure_report_dir()
            assert result.exists()
            assert result.is_dir()
            assert str(result) == str(test_base)
        finally:
            fa.REPORT_BASE = Path(original)


class TestGenerators:
    def test_acceptance_matrix_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_acceptance_matrix import generate_matrix
        result = generate_matrix()
        assert result["schema_version"] == "1.0"
        assert result["artifact_type"] == "acceptance_matrix"
        assert result["total_rows"] > 0
        assert "rows" in result
        for row in result["rows"]:
            assert "id" in row
            assert "description" in row
            assert "required" in row
            assert "status" in row
            assert "evidence_refs" in row

    def test_acceptance_matrix_validator(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_acceptance_matrix import validate
        errs = validate()
        assert isinstance(errs, list)

    def test_evidence_manifest_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_evidence_manifest import collect_evidence
        manifest = collect_evidence()
        assert manifest["schema_version"] == "1.0"
        assert manifest["artifact_type"] == "evidence_manifest"
        assert "evidence_refs" in manifest

    def test_ci_evidence_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_ci_evidence import generate
        report = generate()
        assert report["schema_version"] == "1.0"
        assert report["artifact_type"] == "ci_evidence"
        assert "commit_sha" in report
        assert "workflow_name" in report

    def test_no_overclaim_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_no_overclaim import scan_reports
        findings = scan_reports()
        assert isinstance(findings, list)
        if findings:
            for f in findings:
                assert "file" in f
                assert "pattern" in f

    def test_anti_false_pass_audit(self) -> None:
        from agentx_evolve.final_agentx.run_functional_agentx_anti_false_pass_audit import run_audit
        results = run_audit()
        assert isinstance(results, list)
        if results:
            for r in results:
                assert "attack" in r
                assert "detected" in r

    def test_observability_trace(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_observability_trace import collect_trace
        report = collect_trace()
        assert report["schema_version"] == "1.0"
        assert report["artifact_type"] == "observability_trace_report"
        assert report["total_stages"] > 0

    def test_command_transcript_generator(self) -> None:
        import tempfile
        import shutil
        from unittest.mock import patch
        from agentx_evolve.final_agentx.generate_functional_agentx_command_transcript import generate_transcript
        # Use a temp transcript path so we don't corrupt the real proof run
        tmp = Path(tempfile.mkdtemp(prefix="cmd_transcript_test_"))
        try:
            tmp_transcript = tmp / "functional_runtime_mvp_command_transcript.json"
            tmp_transcript.parent.mkdir(parents=True, exist_ok=True)
            tmp_transcript.write_text(json.dumps([
                {"command": "python3 test.py", "exit_code": 0, "stdout_hash": "a" * 64, "stderr_hash": "b" * 64}
            ]), encoding="utf-8")
            with patch("agentx_evolve.final_agentx.generate_functional_agentx_command_transcript.RECORDER_TRANSCRIPT", tmp_transcript):
                transcript = generate_transcript()
                assert transcript["schema_version"] == "1.0"
                assert transcript["artifact_type"] == "command_transcript"
                assert transcript["total_commands"] > 0
                for entry in transcript["entries"]:
                    assert "command" in entry
                    assert "argv" in entry
                    assert "exit_code" in entry
                    assert "mandatory" in entry
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_dependency_evidence_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_dependency_evidence import generate_report
        report = generate_report()
        assert report["schema_version"] == "1.0"
        assert report["artifact_type"] == "dependency_evidence_report"
        assert "python_version" in report

    def test_policy_precedence_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_policy_precedence import generate_report
        report = generate_report()
        assert report["schema_version"] == "1.0"
        assert report["artifact_type"] == "policy_precedence_report"
        assert report["total_checks"] > 0

    def test_budget_enforcement_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_budget_enforcement import generate_report
        report = generate_report()
        assert report["schema_version"] == "1.0"
        assert report["artifact_type"] == "budget_enforcement_report"
        assert report["total_categories"] > 0

    def test_side_effect_classification_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_side_effect_classification import generate_report
        report = generate_report()
        assert report["schema_version"] == "1.0"
        assert report["artifact_type"] == "side_effect_classification_report"
        assert report["total_adapters"] > 0

    def test_mcp_boundary_validation(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_mcp_boundaries import validate_mcp_source
        results = validate_mcp_source()
        assert isinstance(results, list)
        if results:
            for r in results:
                assert "attack" in r
                assert "blocked" in r

    def test_alias_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_aliases import generate_aliases
        aliases = generate_aliases()
        assert isinstance(aliases, list)
        for a in aliases:
            assert "alias" in a
            assert "canonical" in a
            assert "status" in a

    def test_stage_acceptance_matrix_repo_memory(self) -> None:
        from agentx_evolve.final_agentx.generate_stage_acceptance_matrix import STAGE_CONFIGS
        config = STAGE_CONFIGS["repo-memory"]
        assert len(config["rows"]) >= 8

    def test_stage_acceptance_matrix_git_promotion(self) -> None:
        from agentx_evolve.final_agentx.generate_stage_acceptance_matrix import STAGE_CONFIGS
        config = STAGE_CONFIGS["git-promotion"]
        assert len(config["rows"]) >= 10

    def test_replay_report_generator(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_replay_report import generate_replay_report
        report = generate_replay_report()
        assert report["schema_version"] == "1.0"
        assert report["artifact_type"] == "replay_report"
        assert report["total_stages"] >= 7
        assert "stages" in report

    def test_final_verdict_generator_has_classification(self) -> None:
        from agentx_evolve.final_agentx.generate_functional_agentx_final_verdict import generate_verdict, generate_classification_report
        verdict = generate_verdict()
        assert "run_id" in verdict
        assert "classification" in verdict
        assert "dirty_worktree" in verdict
        assert "cannot_claim" in verdict
        assert "final_artifacts" in verdict
        assert verdict.get("mandatory_gates_total", 0) >= 7

        class_report = generate_classification_report(verdict)
        assert class_report["artifact_type"] == "classification_report"
        assert class_report["classification"] == verdict["classification"]
        assert class_report["verdict"] == verdict["verdict"]
        assert "classification_ladder" in class_report

    def test_get_repo_root(self) -> None:
        from agentx_evolve.final_agentx import get_repo_root
        root = get_repo_root()
        assert root.exists()
        assert (root / ".git").exists()
        assert root.name == "Agent_X"

    def test_get_canonical_artifact_map(self) -> None:
        from agentx_evolve.final_agentx import get_canonical_artifact_map
        amap = get_canonical_artifact_map()
        assert "functional-agentx" in amap
        assert "agent-evolution-alpha" in amap
        assert "agent-evolution-beta" in amap
        assert "governed-self-evolution" in amap
        assert "repo-memory-mvp" in amap
        assert "generated-agent-git-promotion" in amap
        fa = amap["functional-agentx"]
        for required in ("acceptance_matrix.json", "ACCEPTANCE_REVIEW.md", "final_verdict.json",
                          "classification_report.json", "evidence_manifest.json", "replay_report.json",
                          "command_transcript.json", "gap_discovery_report.json"):
            assert required in fa, f"Missing required artifact: {required}"

    def test_final_verdict_validator_classification_list(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_final_verdict import VALID_CLASSIFICATIONS
        assert "AGENTX_REPO_MEMORY_MVP" in VALID_CLASSIFICATIONS
        assert "AGENTX_GENERATED_AGENT_GIT_PROMOTION" in VALID_CLASSIFICATIONS
        assert "FUNCTIONAL_AGENTX_COMPLETE" in VALID_CLASSIFICATIONS


class TestValidatorNegativeCases:
    """Validator-quality tests: prove shape-only JSON is rejected."""

    def test_shape_only_acceptance_matrix_rejected(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_acceptance_matrix import validate
        from agentx_evolve.final_agentx.validate_functional_agentx_acceptance_matrix import REPORT_DIR as RD
        # Missing required fields like schema_version, ev_manifest verdict status
        shape = {"status": "PASS", "total_rows": 100, "passed": 100, "blocked": 0}
        RD.mkdir(parents=True, exist_ok=True)
        (RD / "acceptance_matrix.json").write_text(json.dumps(shape), encoding="utf-8")
        errs = validate()
        assert len(errs) > 0

    def test_static_pass_rows_rejected(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_acceptance_matrix import validate
        from agentx_evolve.final_agentx.validate_functional_agentx_acceptance_matrix import REPORT_DIR as RD
        shape = {
            "schema_version": "1.0",
            "total_rows": 20,
            "passed": 20,
            "blocked": 0,
            "rows": [{"id": f"FAKE-{i}", "description": "fake", "status": "PASS"} for i in range(20)],
        }
        RD.mkdir(parents=True, exist_ok=True)
        (RD / "acceptance_matrix.json").write_text(json.dumps(shape), encoding="utf-8")
        errs = validate()
        assert len(errs) > 0

    def test_final_verdict_missing_gates_rejected(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_final_verdict import validate
        from agentx_evolve.final_agentx.validate_functional_agentx_final_verdict import REPORT_BASE as RB
        shape = {
            "verdict": "PASS",
            "classification": "FUNCTIONAL_AGENTX_COMPLETE",
            "mandatory_gates_passed": 0,
            "mandatory_gates_total": 10,
            "run_id": "fa-test-00000000",
        }
        RB.mkdir(parents=True, exist_ok=True)
        (RB / "final_verdict.json").write_text(json.dumps(shape), encoding="utf-8")
        errs = validate()
        assert len(errs) > 0

    def test_ci_success_no_run_id_rejected(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_ci_evidence import validate
        from agentx_evolve.final_agentx.validate_functional_agentx_ci_evidence import REPORT_DIR as RD
        shape = {
            "ci_status": "SUCCESS",
            "workflow_conclusion": "success",
            "workflow_run_id": "",
            "artifact_ids": [],
        }
        RD.mkdir(parents=True, exist_ok=True)
        (RD / "ci_evidence_report.json").write_text(json.dumps(shape), encoding="utf-8")
        errs = validate()
        assert len(errs) > 0

    def test_evidence_manifest_empty_refs_rejected(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_evidence_manifest import validate
        from agentx_evolve.final_agentx.validate_functional_agentx_evidence_manifest import REPORT_DIR as RD
        shape = {
            "schema_version": "1.0",
            "total_refs": 0,
            "present": 0,
            "missing": 0,
            "evidence_refs": [],
        }
        RD.mkdir(parents=True, exist_ok=True)
        (RD / "evidence_manifest.json").write_text(json.dumps(shape), encoding="utf-8")
        errs = validate()
        assert len(errs) > 0

    def test_synthetic_command_transcript_rejected(self) -> None:
        from agentx_evolve.final_agentx.validate_functional_agentx_review_evidence_binding import validate_binding
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            orig_cwd = os.getcwd()
            try:
                os.chdir(td)
                report_dir = Path(td) / ".agentx-init" / "reports" / "functional-agentx"
                report_dir.mkdir(parents=True, exist_ok=True)
                ct = {
                    "source": "no_recorder_fallback",
                    "entries": [{"command": "fake", "exit_code": 0}],
                }
                (report_dir / "command_transcript.json").write_text(json.dumps(ct), encoding="utf-8")
                evm = {"generated_evidence": []}
                (report_dir / "evidence_manifest.json").write_text(json.dumps(evm), encoding="utf-8")
                errs = validate_binding()
                assert len(errs) > 0
            finally:
                os.chdir(orig_cwd)
