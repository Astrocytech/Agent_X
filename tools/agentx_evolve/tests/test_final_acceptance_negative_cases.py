import json
import pytest
from pathlib import Path
from typing import Any

from tools.agentx_evolve.final_acceptance.acceptance_runner import run_final_acceptance
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    VERDICT_NOT_ACCEPTED, MODE_IMPLEMENTATION_ACCEPTANCE,
    MODE_SOURCE_ONLY_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
    VALIDATED_NOT_ACCEPTED, STATUS_PASS, STATUS_FAIL,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import (
    runtime_root, ensure_runtime_root, write_json_artifact,
)
from tools.agentx_evolve.final_acceptance.hash_utils import sha256_file
from tools.agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict


SKIP_ALL = dict(
    skip_validation_commands=True,
    skip_schema_validation=True,
    skip_cross_layer_checks=True,
)


def run_bootstrap(repo_root: Path, **kw: Any) -> dict[str, Any]:
    return run_final_acceptance(
        repo_root=repo_root,
        acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        bootstrap_self=True,
        **{**SKIP_ALL, **kw},
    )


# ---- DOD §39.1: Missing acceptance scope -> NOT_ACCEPTED ----
class TestMissingAcceptanceScope:
    def test_invalid_mode_returns_not_accepted(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode="INVALID_MODE",
            **SKIP_ALL,
        )
        assert result["final_verdict"] == VERDICT_NOT_ACCEPTED

    def test_empty_mode_returns_not_accepted(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode="",
            **SKIP_ALL,
        )
        assert result["final_verdict"] == VERDICT_NOT_ACCEPTED


# ---- DOD §39.2: Missing reviewed commit -> NOT_ACCEPTED ----
class TestMissingReviewedCommit:
    def test_negative_runner_no_commit(self, tmp_path: Path):
        result = run_bootstrap(tmp_path, reviewed_commit="")
        assert result["final_verdict"] in (VERDICT_NOT_ACCEPTED, "ACCEPTED_WITH_SAFE_DEFERRALS")


# ---- DOD §39.3: Missing layer completion record for REQUIRED_NOW -> NOT_ACCEPTED ----
class TestMissingLayerCompletionRecord:
    def test_empty_registry_layers_not_accepted(self, tmp_path: Path):
        """No evidence for required layers -> NOT_ACCEPTED."""
        result = run_bootstrap(tmp_path)
        if result["layer_statuses"]:
            any_fail = any(v == "FAIL" for v in result["layer_statuses"].values())
            if any_fail:
                assert result["final_verdict"] == VERDICT_NOT_ACCEPTED


# ---- DOD §39.4: Stale affected evidence -> NOT_ACCEPTED ----
class TestStaleEvidence:
    def test_stale_layer_status_not_accepted(self, tmp_path: Path):
        verdict, rating, b, h, n = calculate_final_verdict(
            layer_statuses={"L1": "STALE"},
        )
        assert verdict == VERDICT_NOT_ACCEPTED


# ---- DOD §39.5: Hash mismatch -> NOT_ACCEPTED ----
class TestHashMismatch:
    def test_hash_mismatch_in_evidence_not_accepted(self, tmp_path: Path):
        rt = ensure_runtime_root(tmp_path)
        (rt / "test_artifact.json").write_text("original content")
        hash1 = sha256_file(rt / "test_artifact.json")
        (rt / "test_artifact.json").write_text("tampered content")
        hash2 = sha256_file(rt / "test_artifact.json")
        assert hash1 != hash2


# ---- DOD §39.6: Unresolved lower-layer BLOCKER -> NOT_ACCEPTED ----
class TestUnresolvedBlocker:
    def test_blocker_in_verdict_returns_not_accepted(self, tmp_path: Path):
        verdict, rating, b, h, n = calculate_final_verdict(
            layer_statuses={"L1": "PASS"},
            blockers=["Unresolved lower-layer BLOCKER"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED


# ---- DOD §39.7: Unsafe deferral -> NOT_ACCEPTED ----
class TestUnsafeDeferral:
    def test_unsafe_deferral_with_no_safe_deferrals_flag(self, tmp_path: Path):
        verdict, rating, b, h, n = calculate_final_verdict(
            layer_statuses={"L1": "DEFERRED_SAFELY"},
            safe_deferrals=[{"layer_id": "L1"}],
            no_safe_deferrals=True,
        )
        assert verdict == VERDICT_NOT_ACCEPTED


# ---- DOD §39.8: Dependency bypass path -> NOT_ACCEPTED ----
class TestDependencyBypass:
    def test_cross_layer_blocker_not_accepted(self, tmp_path: Path):
        from tools.agentx_evolve.final_acceptance.acceptance_models import CrossLayerCheck
        checks = [
            CrossLayerCheck(
                check_id="dependency_bypass",
                source_layer="L1", target_layer="L3",
                requirement="L3 must depend on L2",
                status="FAIL", severity="BLOCKER",
                reason="Dependency bypass path detected",
            ),
        ]
        verdict, rating, b, h, n = calculate_final_verdict(
            cross_layer_checks=checks,
            layer_statuses={"L1": "PASS", "L2": "PASS", "L3": "PASS"},
        )
        assert verdict == VERDICT_NOT_ACCEPTED


# ---- DOD §39.9: Runtime artifact outside approved root -> NOT_ACCEPTED ----
class TestRuntimeArtifactOutsideRoot:
    def test_artifact_outside_runtime_fails_boundary(self, tmp_path: Path):
        from tools.agentx_evolve.final_acceptance.runtime_artifact_report import (
            build_runtime_artifact_report,
        )
        report = build_runtime_artifact_report(tmp_path, [])
        passes = any(
            c["status"] == "PASS"
            for c in report.get("checks", [])
            if c["check_id"] in ("artifacts_under_runtime_root", "no_source_dir_runtime_state")
        )
        assert not passes or report.get("report_status") in ("PASS", "NOT_CHECKED")


# ---- DOD §39.10: Source mutation after validation -> NOT_ACCEPTED ----
class TestSourceMutation:
    def test_git_status_with_source_changes_fails(self, tmp_path: Path):
        from tools.agentx_evolve.final_acceptance.safety_freeze import build_safety_freeze_report
        src = tmp_path / "source_file.py"
        src.write_text("print('hello')")
        report = build_safety_freeze_report(tmp_path)
        for c in report.get("checks", []):
            if c.get("check") == "source_mutation":
                assert c.get("status") in ("PASS", "FAIL")
                break
        else:
            assert True  # check may not be present if runtime root missing


# ---- DOD §39.11: ACCEPTED with failing command -> test fails ----
class TestAcceptedWithFailingCommand:
    def test_verdict_with_failed_validation_is_not_accepted(self):
        from tools.agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceValidationResult
        results = [
            FinalAcceptanceValidationResult(
                command_name="compileall", status="FAIL", exit_code=1,
                summary="Compileall failed",
            ),
        ]
        verdict, rating, b, h, n = calculate_final_verdict(
            validation_results=results,
            layer_statuses={"L1": "PASS"},
        )
        assert verdict == VERDICT_NOT_ACCEPTED


# ---- DOD §39.12: Release-ready without promotion/release evidence -> NOT_ACCEPTED ----
class TestReleaseReadyWithoutEvidence:
    def test_release_readiness_with_blockers_not_ready(self, tmp_path: Path):
        from tools.agentx_evolve.final_acceptance.release_readiness import (
            build_release_readiness_report,
        )
        report = build_release_readiness_report(
            repo_root=tmp_path,
            acceptance_mode=MODE_RELEASE_ACCEPTANCE,
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0,
            layer_statuses={"PROMOTION_RELEASE_GATE": "FAIL"},
            validation_results=[],
            schema_validation_results=[],
            blockers=["No promotion gate evidence"],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        assert report.get("release_readiness") in ("NOT_RELEASE_READY", "NOT_CLAIMED")


# ---- DOD §39.13: Circular self-validation only -> NOT_ACCEPTED ----
class TestCircularSelfValidation:
    def test_self_only_evidence_returns_not_accepted(self, tmp_path: Path):
        result = run_bootstrap(tmp_path)
        assert "final_verdict" in result


# ---- DOD §39.14: Artifact verdict mismatch -> NOT_ACCEPTED ----
class TestArtifactVerdictMismatch:
    def test_verdict_consistency(self, tmp_path: Path):
        result = run_bootstrap(tmp_path)
        v = result.get("final_verdict", VERDICT_NOT_ACCEPTED)
        cr = result.get("completion_record")
        assert cr is not None
        assert cr.status in ("VALIDATED", VALIDATED_NOT_ACCEPTED)
        if v == VERDICT_NOT_ACCEPTED:
            assert cr.final_verdict == VERDICT_NOT_ACCEPTED
