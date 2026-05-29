"""Runs L0 proof suite and collects results."""

import subprocess
import sys


class ProofRunner:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def run_seed_boot(self) -> dict:
        result = subprocess.run(
            ["make", "seed-boot"],
            capture_output=True, text=True, cwd=self.repo_path
        )
        return {"passed": result.returncode == 0, "output": result.stdout}

    def run_prove_seed(self) -> dict:
        result = subprocess.run(
            ["make", "prove-seed"],
            capture_output=True, text=True, cwd=self.repo_path
        )
        return {"passed": result.returncode == 0, "output": result.stdout}

    def run_all(self) -> dict:
        return {
            "seed_boot": self.run_seed_boot(),
            "prove_seed": self.run_prove_seed(),
        }
