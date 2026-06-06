from __future__ import annotations
import subprocess
from pathlib import Path
from agentx_evolve.security.security_models import (
    utc_now_iso, new_id,
)


class GitDiffGuard:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root.resolve()

    def get_diff(self) -> str:
        try:
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True, text=True, timeout=30,
                cwd=self._repo_root,
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    def get_diff_name_only(self) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, timeout=30,
                cwd=self._repo_root,
            )
            if result.returncode != 0:
                return []
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return []

    def get_diff_stat(self) -> str:
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"],
                capture_output=True, text=True, timeout=30,
                cwd=self._repo_root,
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    def get_diff_for_file(self, file_path: str) -> str:
        try:
            result = subprocess.run(
                ["git", "diff", "--", file_path],
                capture_output=True, text=True, timeout=30,
                cwd=self._repo_root,
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    def has_changes(self) -> bool:
        files = self.get_diff_name_only()
        return len(files) > 0

    def verify_only_expected_files_changed(
        self, expected_paths: set[str],
    ) -> tuple[bool, list[str]]:
        changed = self.get_diff_name_only()
        unexpected = [p for p in changed if p not in expected_paths]
        if unexpected:
            return False, unexpected
        return True, []
