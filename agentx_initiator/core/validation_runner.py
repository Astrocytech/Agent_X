import subprocess
from pathlib import Path
from agentx_initiator.core.config import load_config
from agentx_initiator.core.paths import repo_root


def run_validation() -> list[dict]:
    config = load_config()
    results = []

    for cmd_template in config.allowlisted_commands:
        cmd_str = _resolve_command(cmd_template)
        try:
            result = subprocess.run(
                cmd_str, shell=True, capture_output=True, text=True,
                timeout=60, cwd=repo_root(),
            )
            passed = result.returncode == 0
            results.append({
                "command": cmd_template,
                "passed": passed,
                "returncode": result.returncode,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500],
            })
        except subprocess.TimeoutExpired:
            results.append({
                "command": cmd_template,
                "passed": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out after 60s",
            })
        except FileNotFoundError:
            results.append({
                "command": cmd_template,
                "passed": False,
                "returncode": -2,
                "stdout": "",
                "stderr": "Command not found",
            })

    return results


def _resolve_command(cmd: str) -> str:
    root = repo_root()
    replacements = {
        "{root}": str(root),
        "{repo}": str(root),
    }
    for key, val in replacements.items():
        cmd = cmd.replace(key, val)
    return cmd
