from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
TEST_PLAN_ID = "INVSCI-PLAN-CLITEST"
INVERSE_ROOT = Path(".agentx-init") / "inverse_science"


def _clean_test_artifacts() -> None:
    test_dir = REPO_ROOT / INVERSE_ROOT / TEST_PLAN_ID
    if test_dir.exists():
        shutil.rmtree(test_dir)


class TestInverseScienceCli:
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(TOOLS_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "agentx_evolve", *args],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )

    def test_inverse_help_prints_usage(self) -> None:
        result = self._run("inverse", "--help")
        assert result.returncode == 0
        assert "init" in result.stdout

    def test_inverse_unknown_subcommand(self) -> None:
        result = self._run("inverse", "nonexistent")
        assert result.returncode == 1
        assert "Unknown inverse subcommand" in result.stdout

    def test_inverse_init_requires_target(self) -> None:
        result = self._run("inverse", "init")
        assert result.returncode == 1
        assert "--target is required" in result.stdout

    def test_inverse_init_creates_plan(self) -> None:
        _clean_test_artifacts()
        result = self._run(
            "inverse", "init", "--target", "test umbrella improvement",
            "--plan-id", TEST_PLAN_ID,
        )
        assert result.returncode == 0
        assert "Plan created" in result.stdout
        plan_dir = REPO_ROOT / INVERSE_ROOT / TEST_PLAN_ID
        assert (plan_dir / "plan.json").exists()
        assert (plan_dir / "candidates").is_dir()
        assert (plan_dir / "governance").is_dir()
        assert (plan_dir / "observations").is_dir()
        assert (plan_dir / "evidence_ledger").is_dir()
        assert (plan_dir / "negative_knowledge").is_dir()
        assert (plan_dir / "best_known_solution").is_dir()
        assert (plan_dir / "event_log.jsonl").exists()

    def test_inverse_init_rejects_duplicate(self) -> None:
        result = self._run(
            "inverse", "init", "--target", "test",
            "--plan-id", TEST_PLAN_ID,
        )
        assert result.returncode == 1

    def test_inverse_candidates_empty(self) -> None:
        result = self._run("inverse", "candidates", "--plan-id", TEST_PLAN_ID)
        assert result.returncode == 0

    def test_inverse_candidates_missing_plan(self) -> None:
        result = self._run("inverse", "candidates", "--plan-id", "NONEXISTENT")
        assert result.returncode == 1

    def test_inverse_validate_with_plan(self) -> None:
        result = self._run("inverse", "validate", "--plan-id", TEST_PLAN_ID)
        assert result.returncode == 1

    def test_inverse_report_creates_report(self) -> None:
        result = self._run("inverse", "report", "--plan-id", TEST_PLAN_ID)
        assert result.returncode == 0
        assert "Report created" in result.stdout
        plan_dir = REPO_ROOT / INVERSE_ROOT / TEST_PLAN_ID
        assert (plan_dir / "final_report.json").exists()
