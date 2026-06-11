from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
PLAN_ID = "INVSCI-PLAN-GOVHANDOFF"
PLAN_DIR = Path(".agentx-init/inverse_science") / PLAN_ID


def _run(*args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(TOOLS_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "agentx_evolve", *args],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
    )


class TestIntegrationGovernedPatchHandoff:
    def setup_method(self):
        if PLAN_DIR.exists():
            shutil.rmtree(str(PLAN_DIR))

    def teardown_method(self):
        if PLAN_DIR.exists():
            shutil.rmtree(str(PLAN_DIR))

    def _write_candidate(self, candidate_id: str, change: str,
                         hc_check: str = "PASS",
                         rollback: str = "git revert",
                         evidence: str = "run tests") -> Path:
        cand_dir = PLAN_DIR / "candidates"
        cand_dir.mkdir(parents=True, exist_ok=True)
        cand = {
            "candidate_id": candidate_id,
            "plan_id": PLAN_ID,
            "schema_version": "1.0.0",
            "candidate_type": "patch",
            "proposed_change": change,
            "primary_variable_changed": "config",
            "rationale": "Integration test for governed patch handoff",
            "score_components": {
                "expected_target_gain": 5, "expected_information_gain": 3,
                "novelty": 2, "reversibility_bonus": 2,
                "constraint_risk": 3, "safety_risk": 2,
                "cost": 2, "complexity_penalty": 1,
            },
            "acquisition_score": 4.0,
            "hard_constraint_check": hc_check,
            "rollback_plan": rollback,
            "evidence_plan": evidence,
            "human_review_required": True,
            "created_at_utc": "2026-06-11T12:00:00Z",
        }
        path = cand_dir / f"{candidate_id}.json"
        path.write_text(json.dumps(cand))
        return path

    def _write_governance_allow_with_limits(self, candidate_id: str,
                                            limits: list[str] = None,
                                            risk: str = "medium") -> Path:
        gov_dir = PLAN_DIR / "governance"
        gov_dir.mkdir(parents=True, exist_ok=True)
        import hashlib
        gov_id = f"INVSCI-GOV-{hashlib.sha256(candidate_id.encode()).hexdigest()[:8].upper()}"
        gov = {
            "decision_id": gov_id,
            "candidate_id": candidate_id,
            "plan_id": PLAN_ID,
            "schema_version": "1.0.0",
            "decision": "allow_with_limits",
            "policy_checks": [
                {"check": "L0 mutation", "result": "PASS"},
                {"check": "governance bypass", "result": "PASS"},
                {"check": "unsupported claims", "result": "PASS"},
            ],
            "capability_checks": ["least_privilege"],
            "path_boundary_checks": ["protected_paths"],
            "risk_level": risk,
            "limits": limits or [
                "Must use governed patch executor",
                "Must run tests after patch",
                "Must obtain human review before promotion",
            ],
            "reason": "Approved with limits due to moderate risk",
            "review_requirement": "standard",
            "created_at_utc": "2026-06-11T12:00:00Z",
        }
        path = gov_dir / f"{gov_id}.json"
        path.write_text(json.dumps(gov))
        return path

    def _validate_governance_schema(self, gov_instance: dict) -> list[str]:
        try:
            import jsonschema
        except ImportError:
            return []
        schema_path = TOOLS_DIR / "agentx_evolve" / "schemas" / "inverse_science_governance_decision.schema.json"
        schema = json.loads(schema_path.read_text())
        validator = jsonschema.Draft7Validator(schema)
        return [str(e) for e in validator.iter_errors(gov_instance)]

    def test_governed_patch_allow_with_limits_propagates_to_report_manual(self):
        # Manual: writes governance file to disk directly, then observe+report.
        r = _run("inverse", "init", "--target", "risky claim test",
                 "--plan-id", PLAN_ID)
        assert r.returncode == 0, f"init failed: {r.stdout} {r.stderr}"
        assert (PLAN_DIR / "plan.json").exists()

        self._write_candidate("INVSCI-CAND-GOVH01",
                              "Risky configuration change")

        r = _run("inverse", "rank", "--plan-id", PLAN_ID)
        assert r.returncode == 0

        expected_limits = [
            "Must use governed patch executor",
            "Must run tests after patch",
            "Must obtain human review before promotion",
        ]
        self._write_governance_allow_with_limits(
            "INVSCI-CAND-GOVH01",
            limits=expected_limits,
            risk="medium",
        )

        r = _run("inverse", "observe", "--plan-id", PLAN_ID,
                 "--candidate-id", "INVSCI-CAND-GOVH01",
                 "--validity", "valid")
        assert r.returncode == 0

        r = _run("inverse", "report", "--plan-id", PLAN_ID)
        assert r.returncode == 0
        assert (PLAN_DIR / "final_report.json").exists()

        report = json.loads((PLAN_DIR / "final_report.json").read_text())
        gov_decision = report.get("governance_decision", {})
        assert gov_decision.get("decision") == "allow_with_limits"
        assert gov_decision.get("limits") == expected_limits

    def test_allow_with_limits_decision_passes_schema_validation(self):
        gov = {
            "decision_id": "INVSCI-GOV-GOVHSCHEMA",
            "candidate_id": "INVSCI-CAND-GOVHSCHEMA",
            "plan_id": PLAN_ID,
            "schema_version": "1.0.0",
            "decision": "allow_with_limits",
            "policy_checks": [
                {"check": "L0 mutation", "result": "PASS"},
            ],
            "capability_checks": ["least_privilege"],
            "path_boundary_checks": ["protected_paths"],
            "risk_level": "medium",
            "limits": ["Must use governed patch executor"],
            "reason": "Conditional approval",
            "review_requirement": "standard",
            "created_at_utc": "2026-06-11T12:00:00Z",
        }
        errors = self._validate_governance_schema(gov)
        assert not errors, f"allow_with_limits decision should be schema-valid: {errors}"

    def test_limits_appear_in_evidence_manifest(self):
        r = _run("inverse", "init", "--target", "limits manifest test",
                 "--plan-id", PLAN_ID)
        assert r.returncode == 0

        self._write_candidate("INVSCI-CAND-GOVH02",
                              "Config change with limits")

        limits = ["Must use governed patch executor", "Requires sign-off"]
        self._write_governance_allow_with_limits(
            "INVSCI-CAND-GOVH02",
            limits=limits,
        )

        r = _run("inverse", "observe", "--plan-id", PLAN_ID,
                 "--candidate-id", "INVSCI-CAND-GOVH02",
                 "--validity", "valid")
        assert r.returncode == 0

        r = _run("inverse", "report", "--plan-id", PLAN_ID)
        assert r.returncode == 0

        manifest = json.loads((PLAN_DIR / "evidence_manifest.json").read_text())
        assert "artifacts" in manifest
        gov_artifact = None
        for art in manifest["artifacts"]:
            if "governance" in art.get("path", ""):
                gov_artifact = art
                break
        assert gov_artifact is not None, "Governance artifact not found in manifest"

    def test_governed_patch_allow_with_limits_creates_review_request(self):
        r = _run("inverse", "init", "--target", "allow with limits review",
                 "--plan-id", PLAN_ID)
        assert r.returncode == 0, f"init failed: {r.stdout} {r.stderr}"
        assert (PLAN_DIR / "plan.json").exists()

        self._write_candidate(
            "INVSCI-CAND-GOVH03",
            "Config change requiring limits",
            rollback="git revert",
            evidence="run tests",
        )

        r = _run("inverse", "rank", "--plan-id", PLAN_ID)
        assert r.returncode == 0

        r = _run("inverse", "govern", "--plan-id", PLAN_ID,
                 "--candidate-id", "INVSCI-CAND-GOVH03",
                 "--allow-with-limits")
        assert r.returncode == 0, f"govern failed: {r.stdout} {r.stderr}"

        gov_files = list((PLAN_DIR / "governance").glob("*.json"))
        assert len(gov_files) == 1, f"Expected 1 governance file, got {len(gov_files)}"

        gov = json.loads(gov_files[0].read_text())
        assert gov.get("decision") == "allow_with_limits"
        assert isinstance(gov.get("limits"), list)
        assert len(gov["limits"]) > 0

    def test_governed_patch_human_review_request_created(self):
        r = _run("inverse", "init", "--target", "human review request test",
                 "--plan-id", PLAN_ID)
        assert r.returncode == 0, f"init failed: {r.stdout} {r.stderr}"
        assert (PLAN_DIR / "plan.json").exists()

        self._write_candidate(
            "INVSCI-CAND-GOVH04",
            "Change requiring human review",
            rollback="git revert",
            evidence="run tests",
        )

        r = _run("inverse", "rank", "--plan-id", PLAN_ID)
        assert r.returncode == 0

        r = _run("inverse", "govern", "--plan-id", PLAN_ID,
                 "--candidate-id", "INVSCI-CAND-GOVH04",
                 "--allow")
        assert r.returncode == 0, f"govern failed: {r.stdout} {r.stderr}"

        hr_dir = REPO_ROOT / ".agentx-init" / "human_review"
        assert hr_dir.exists(), f"Human review directory not found: {hr_dir}"

        latest = hr_dir / "latest_review_request.json"
        assert latest.exists(), f"latest_review_request.json not found in {hr_dir}"

        req = json.loads(latest.read_text())
        assert req.get("requested_by") == "inverse_science_governance"
        assert req.get("requested_action") == "Change requiring human review"
        assert "INVSCI-CAND-GOVH04" in str(req.get("artifact_refs", []))
        assert "INVSCI-GOV-" in str(req.get("scope", {}).get("policy_decision_id", ""))
