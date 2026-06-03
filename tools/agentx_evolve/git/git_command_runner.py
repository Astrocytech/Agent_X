import subprocess
import time
import hashlib
import tempfile
import shutil
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitCommandResult, GS_SUCCESS, GS_FAILED, GS_BLOCKED,
    new_id, utc_now_iso,
)
from agentx_evolve.security.secret_redactor import redact_secrets

MAX_OUTPUT_BYTES = 1048576
GIT_TIMEOUT = 30


def run_git_command(
    argv: list[str],
    cwd: str = ".",
    env: dict[str, str] | None = None,
    timeout_seconds: int = GIT_TIMEOUT,
    operation_id: str = "",
    operation_name: str = "",
) -> GitCommandResult:
    tmpdir = tempfile.mkdtemp(prefix="agentx_git_env_")
    try:
        base_env = {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": "",
            "SSH_ASKPASS": "",
            "GIT_PAGER": "cat",
            "PAGER": "cat",
            "GIT_EXTERNAL_DIFF": "",
            "GIT_CONFIG_NOSYSTEM": "1",
            "HOME": tmpdir,
            "XDG_CONFIG_HOME": str(Path(tmpdir) / "config"),
            "LC_ALL": "C",
        }
        merged_env = {**base_env, **(env or {})}
        start = time.monotonic()
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=cwd,
            env=merged_env,
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        stdout_raw = proc.stdout[:MAX_OUTPUT_BYTES] if proc.stdout else ""
        stderr_raw = proc.stderr[:MAX_OUTPUT_BYTES] if proc.stderr else ""
        stdout_redacted = redact_secrets(stdout_raw).redacted_text
        stderr_redacted = redact_secrets(stderr_raw).redacted_text
        argv_sha = hashlib.sha256(" ".join(argv).encode()).hexdigest()
        return GitCommandResult(
            result_id=new_id("gcr"),
            timestamp=utc_now_iso(),
            operation_id=operation_id,
            operation_name=operation_name,
            status=GS_SUCCESS if proc.returncode == 0 else GS_FAILED,
            exit_code=proc.returncode,
            stdout=stdout_redacted,
            stderr=stderr_redacted,
            duration_ms=duration_ms,
            argv_sha256=argv_sha,
        )
    except subprocess.TimeoutExpired:
        return GitCommandResult(
            result_id=new_id("gcr"),
            timestamp=utc_now_iso(),
            operation_id=operation_id,
            operation_name=operation_name,
            status=GS_FAILED,
            exit_code=-1,
            stderr="git command timed out",
            duration_ms=timeout_seconds * 1000,
            errors=["TimeoutExpired"],
        )
    except FileNotFoundError:
        return GitCommandResult(
            result_id=new_id("gcr"),
            timestamp=utc_now_iso(),
            operation_id=operation_id,
            operation_name=operation_name,
            status=GS_FAILED,
            exit_code=-1,
            stderr="git executable not found",
            errors=["FileNotFoundError"],
        )
    except Exception as e:
        return GitCommandResult(
            result_id=new_id("gcr"),
            timestamp=utc_now_iso(),
            operation_id=operation_id,
            operation_name=operation_name,
            status=GS_FAILED,
            exit_code=-1,
            stderr=str(e),
            errors=[str(e)],
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
