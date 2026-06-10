import os, sys, tempfile, subprocess
from pathlib import Path


class TestAgentxEvolveCliHelp:
    """System tests for CLI help, version, and unknown commands."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    AGENTX_EVOLVE_DIR = REPO_ROOT / "tools" / "agentx_evolve"

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.REPO_ROOT / "tools") + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "agentx_evolve", *args],
            capture_output=True, text=True, cwd=str(self.REPO_ROOT), env=env,
        )

    def test_help_flag_prints_help_and_exits_zero(self):
        result = self._run("--help")
        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_help_command_prints_help_and_exits_zero(self):
        result = self._run("help")
        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_version_prints_version_info(self):
        result = self._run("version")
        assert result.returncode == 0
        assert "agentx-evolve" in result.stdout

    def test_unknown_command_exits_nonzero(self):
        result = self._run("nonexistent-command-xyz")
        assert result.returncode != 0
        assert "Unknown command" in result.stdout
