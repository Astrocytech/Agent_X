from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
PLAN_ID = "INVSCI-PLAN-SYSTEST"
PLAN_DIR = Path(".agentx-init/inverse_science") / PLAN_ID


def _cleanup():
    import shutil
    if PLAN_DIR.exists():
        shutil.rmtree(str(PLAN_DIR))


def _run(*args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(TOOLS_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "agentx_evolve", *args],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
    )


def _write_candidate(candidate_id: str, plan_id: str, change: str,
                     hc_check: str = "PASS", rollback: str = "git revert",
                     evidence: str = "run tests",
                     plan_dir: Path = PLAN_DIR) -> Path:
    candidates_dir = plan_dir / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    cand = {
        "candidate_id": candidate_id,
        "plan_id": plan_id,
        "schema_version": "1.0.0",
        "candidate_type": "patch",
        "proposed_change": change,
        "primary_variable_changed": "test",
        "rationale": "System test",
        "score_components": {
            "expected_target_gain": 5, "expected_information_gain": 3,
            "novelty": 2, "reversibility_bonus": 2,
            "constraint_risk": 1, "safety_risk": 0.5,
            "cost": 2, "complexity_penalty": 1,
        },
        "acquisition_score": 7.5,
        "hard_constraint_check": hc_check,
        "rollback_plan": rollback,
        "evidence_plan": evidence,
        "human_review_required": False,
        "created_at_utc": "2026-06-11T12:00:00Z",
    }
    path = candidates_dir / f"{candidate_id}.json"
    path.write_text(json.dumps(cand))
    return path


class TestSystemInverseScience:
    def setup_method(self):
        _cleanup()

    def teardown_method(self):
        _cleanup()

    def test_accept_path_full_workflow(self):
        r = _run("inverse", "init", "--target", "system test accept",
                 "--plan-id", PLAN_ID)
        assert r.returncode == 0
        assert (PLAN_DIR / "plan.json").exists()

        _write_candidate("INVSCI-CAND-SYSACC01", PLAN_ID,
                         "Accept path candidate")

        r = _run("inverse", "rank", "--plan-id", PLAN_ID)
        assert r.returncode == 0
        assert (PLAN_DIR / "ranking.json").exists()

        r = _run("inverse", "govern", "--plan-id", PLAN_ID,
                 "--candidate-id", "INVSCI-CAND-SYSACC01", "--allow")
        assert r.returncode == 0
        gov_files = list((PLAN_DIR / "governance").glob("*.json"))
        assert len(gov_files) >= 1
        gov = json.loads(gov_files[0].read_text())
        assert gov["decision"] == "allow"

        r = _run("inverse", "observe", "--plan-id", PLAN_ID,
                 "--candidate-id", "INVSCI-CAND-SYSACC01",
                 "--validity", "valid")
        assert r.returncode == 0
        ledger_files = list((PLAN_DIR / "evidence_ledger").glob("*.json"))
        assert len(ledger_files) >= 1

        r = _run("inverse", "report", "--plan-id", PLAN_ID)
        assert r.returncode == 0
        assert (PLAN_DIR / "final_report.json").exists()
        assert (PLAN_DIR / "evidence_manifest.json").exists()

    def test_reject_path_full_workflow(self):
        reject_plan_id = "INVSCI-PLAN-SYSREJ"
        reject_dir = Path(".agentx-init/inverse_science") / reject_plan_id
        import shutil
        if reject_dir.exists():
            shutil.rmtree(str(reject_dir))
        try:
            r = _run("inverse", "init", "--target", "system test reject",
                     "--plan-id", reject_plan_id)
            assert r.returncode == 0

            _write_candidate("INVSCI-CAND-SYSREJ01", reject_plan_id,
                             "Reject path candidate",
                             plan_dir=reject_dir)

            r = _run("inverse", "govern", "--plan-id", reject_plan_id,
                     "--candidate-id", "INVSCI-CAND-SYSREJ01", "--reject")
            assert r.returncode == 0
            gov_files = list((reject_dir / "governance").glob("*.json"))
            assert len(gov_files) >= 1
            gov = json.loads(gov_files[0].read_text())
            assert gov["decision"] == "reject"

            r = _run("inverse", "observe", "--plan-id", reject_plan_id,
                     "--candidate-id", "INVSCI-CAND-SYSREJ01",
                     "--validity", "invalid")
            assert r.returncode == 0

            r = _run("inverse", "report", "--plan-id", reject_plan_id)
            assert r.returncode == 0
            assert (reject_dir / "final_report.json").exists()
        finally:
            if reject_dir.exists():
                shutil.rmtree(str(reject_dir))
