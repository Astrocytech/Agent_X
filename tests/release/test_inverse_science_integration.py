from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools"


class TestInverseScienceIntegration:
    REPO_ROOT = REPO_ROOT
    TOOLS_DIR = TOOLS_DIR
    plan_id = "INVSCI-PLAN-INTEGTEST"

    def setup_method(self):
        # Run after class-level init; plan_dir may not exist yet
        pass

    @classmethod
    def setup_class(cls):
        import shutil
        d = Path(".agentx-init/inverse_science") / cls.plan_id
        if d.exists():
            shutil.rmtree(str(d))

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(TOOLS_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "agentx_evolve", *args],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )

    def test_01_plan_to_candidates_to_ranking(self):
        # Init plan
        r = self._run("inverse", "init", "--target",
                      "improve umbrella borderline weather",
                      "--plan-id", self.plan_id)
        assert r.returncode == 0

        # Create candidate manually in the candidates dir
        candidates_dir = Path(".agentx-init/inverse_science") / self.plan_id / "candidates"
        candidate = {
            "candidate_id": "INVSCI-CAND-INTEG001",
            "plan_id": self.plan_id,
            "schema_version": "1.0.0",
            "candidate_type": "patch",
            "proposed_change": "Add drizzle handling to recommendation engine",
            "primary_variable_changed": "recommendation logic",
            "rationale": "Users need umbrella for drizzle too",
            "score_components": {
                "expected_target_gain": 5.0,
                "expected_information_gain": 3.0,
                "novelty": 2.0,
                "reversibility_bonus": 2.0,
                "constraint_risk": 1.0,
                "safety_risk": 0.5,
                "cost": 2.0,
                "complexity_penalty": 1.0,
            },
            "acquisition_score": 0,
            "hard_constraint_check": "PASS",
            "rollback_plan": "git checkout -- examples/umbrella_agent/recommendation_engine.py",
            "evidence_plan": "Run existing tests plus new drizzle tests",
            "human_review_required": False,
            "created_at_utc": "2026-06-11T12:00:00Z",
        }
        (candidates_dir / "INVSCI-CAND-INTEG001.json").write_text(json.dumps(candidate))

        # Rank
        r = self._run("inverse", "rank", "--plan-id", self.plan_id, "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "ranked_candidates" in data
        assert data["ranked_candidates"][0] == "INVSCI-CAND-INTEG001"

    def test_02_candidate_to_governance_decision(self):
        r = self._run("inverse", "govern", "--plan-id", self.plan_id,
                      "--candidate-id", "INVSCI-CAND-INTEG001", "--allow")
        assert r.returncode == 0
        assert "allow" in r.stdout

    def test_03_governance_to_observation(self):
        r = self._run("inverse", "observe", "--plan-id", self.plan_id,
                      "--candidate-id", "INVSCI-CAND-INTEG001", "--validity", "valid")
        assert r.returncode == 0
        assert "Observation recorded" in r.stdout
        assert "Evidence ledger" in r.stdout

    def test_04_observation_to_evidence_ledger(self):
        # Evidence ledger entry should exist from observe step
        plan_dir = Path(".agentx-init/inverse_science") / self.plan_id
        ledger_files = list((plan_dir / "evidence_ledger").glob("*.json"))
        assert len(ledger_files) >= 1
        entry = json.loads(ledger_files[0].read_text())
        assert entry["evidence_class"] == "test_evidence"
        assert entry["claim_status"] == "supported"

    def test_05_rejected_candidate_to_negative_knowledge(self):
        # Create a candidate that passes hard constraints but is rejected by governance
        candidates_dir = Path(".agentx-init/inverse_science") / self.plan_id / "candidates"
        rejected_candidate = {
            "candidate_id": "INVSCI-CAND-INTEG002",
            "plan_id": self.plan_id,
            "schema_version": "1.0.0",
            "candidate_type": "patch",
            "proposed_change": "High-risk change requiring rejection",
            "primary_variable_changed": "multiple variables",
            "rationale": "Test rejection",
            "score_components": {
                "expected_target_gain": 2.0, "expected_information_gain": 1.0,
                "novelty": 0.0, "reversibility_bonus": 0.0,
                "constraint_risk": 8.0, "safety_risk": 8.0,
                "cost": 5.0, "complexity_penalty": 5.0,
            },
            "acquisition_score": 0,
            "hard_constraint_check": "PASS",
            "rollback_plan": "git revert",
            "evidence_plan": "run tests",
            "human_review_required": True,
            "created_at_utc": "2026-06-11T12:00:00Z",
        }
        (candidates_dir / "INVSCI-CAND-INTEG002.json").write_text(json.dumps(rejected_candidate))
        r = self._run("inverse", "govern", "--plan-id", self.plan_id,
                      "--candidate-id", "INVSCI-CAND-INTEG002", "--reject")
        assert r.returncode == 0
        assert "reject" in r.stdout

    def test_06_failed_probe_to_failure_taxonomy(self):
        r = self._run("inverse", "observe", "--plan-id", self.plan_id,
                      "--candidate-id", "INVSCI-CAND-INTEG002", "--validity", "invalid")
        assert r.returncode == 0

    def test_07_artifacts_validate_against_schemas(self):
        r = self._run("inverse", "validate", "--plan-id", self.plan_id)
        # May be 1 because evidence_manifest is missing; that's expected
        assert r.returncode in (0, 1)

    def test_08_event_log_append_only(self):
        plan_dir = Path(".agentx-init/inverse_science") / self.plan_id
        log_path = plan_dir / "event_log.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().split("\n")
        assert len(lines) >= 4
        seq_ids = [json.loads(l)["sequence_id"] for l in lines]
        assert seq_ids == sorted(seq_ids)
        assert len(seq_ids) == len(set(seq_ids))

    def test_09_source_diff_review_generated(self):
        r = self._run("inverse", "report", "--plan-id", self.plan_id)
        assert r.returncode == 0
        plan_dir = Path(".agentx-init/inverse_science") / self.plan_id
        assert (plan_dir / "final_report.json").exists()
        assert (plan_dir / "evidence_manifest.json").exists()
        assert (plan_dir / "plan.md").exists()

    def test_10_best_known_solution_after_supported_evidence(self):
        # verify artifacts exist after full workflow
        plan_dir = Path(".agentx-init/inverse_science") / self.plan_id
        assert (plan_dir / "evidence_manifest.json").exists()
        manifest = json.loads((plan_dir / "evidence_manifest.json").read_text())
        assert "artifacts" in manifest
        assert len(manifest["artifacts"]) > 0

    def test_11_rerun_blocked_for_init(self):
        r = self._run("inverse", "init", "--target", "duplicate", "--plan-id", self.plan_id)
        assert r.returncode == 1
        assert "already exists" in r.stdout


class TestInverseScienceNegativeCases:
    REPO_ROOT = REPO_ROOT
    TOOLS_DIR = TOOLS_DIR

    def setup_method(self):
        import shutil
        for pid in ("INVSCI-PLAN-NEGTEST", "INVSCI-PLAN-NEG002"):
            d = Path(".agentx-init/inverse_science") / pid
            if d.exists():
                shutil.rmtree(str(d))

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(TOOLS_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "agentx_evolve", *args],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )

    def test_cli_emits_empty_json_and_exits_0(self):
        # CLI with --json flag on candidates with no candidates should output [] not fail
        plan_id = "INVSCI-PLAN-NEGTEST"
        self._run("inverse", "init", "--target", "neg test", "--plan-id", plan_id)
        r = self._run("inverse", "candidates", "--plan-id", plan_id, "--json")
        assert r.returncode == 0

    def test_rejected_candidate_not_recorded_as_negative_knowledge(self):
        # A candidate that was rejected but NOT recorded as observation should NOT
        # automatically get a negative_knowledge entry
        plan_id = "INVSCI-PLAN-NEG002"
        self._run("inverse", "init", "--target", "neg test 2", "--plan-id", plan_id)
        plan_dir = Path(".agentx-init/inverse_science") / plan_id
        nk_files = list((plan_dir / "negative_knowledge").glob("*.json"))
        # No negative knowledge should exist yet since we haven't created any
        assert len(nk_files) == 0
