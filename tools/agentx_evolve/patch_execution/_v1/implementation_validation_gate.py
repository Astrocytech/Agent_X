from __future__ import annotations
import subprocess
from pathlib import Path
from agentx_evolve.security.secret_redactor import redact_secrets
from agentx_evolve.security.safe_subprocess import check_subprocess_allowed
from agentx_evolve.security.sandbox_policy import SandboxPolicy
from agentx_evolve.security.security_models import STATUS_SUCCESS
from agentx_evolve.patch_execution._v1.patch_models import utc_now_iso, new_id


class ImplementationValidationGate:
    def __init__(
        self,
        repo_root: Path,
        policy: SandboxPolicy,
    ):
        self._repo_root = repo_root.resolve()
        self._policy = policy

    def run_validation_commands(
        self, commands: list[list[str]],
    ) -> list[dict]:
        results = []
        for cmd in commands:
            precheck = check_subprocess_allowed(cmd, self._policy)
            if precheck.status != "ALLOW":
                results.append({
                    "command": cmd,
                    "status": "BLOCKED",
                    "reason": precheck.reason,
                })
                continue

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True, text=True, timeout=60,
                    cwd=self._repo_root,
                )
                raw_out = result.stdout[:500]
                raw_err = result.stderr[:500]
                redacted_out = redact_secrets(raw_out, self._policy).redacted_text
                redacted_err = redact_secrets(raw_err, self._policy).redacted_text
                results.append({
                    "command": cmd,
                    "status": "PASS" if result.returncode == 0 else "FAIL",
                    "returncode": result.returncode,
                    "stdout": redacted_out,
                    "stderr": redacted_err,
                })
            except subprocess.TimeoutExpired:
                results.append({
                    "command": cmd,
                    "status": "TIMEOUT",
                    "returncode": -1,
                    "stderr": "Timed out after 60s",
                })
            except FileNotFoundError:
                results.append({
                    "command": cmd,
                    "status": "FAIL",
                    "returncode": -2,
                    "stderr": "Command not found",
                })

        return results

    def all_passed(self, results: list[dict]) -> bool:
        return all(r.get("status") == "PASS" for r in results)
