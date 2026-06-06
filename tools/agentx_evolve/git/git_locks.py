import fcntl
import os
import time
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitLockRecord, GIT_LOCK_ACQUIRED, GIT_LOCK_RELEASED,
    GIT_LOCK_BLOCKED, GIT_LOCK_TIMEOUT, GIT_LOCK_STALE_REJECTED,
    new_id, utc_now_iso,
)


def _lock_path(repo_root: str) -> Path:
    return Path(repo_root) / ".agentx-init" / "git" / "locks" / "git_mutation.lock"


def acquire_git_lock(repo_root: str, operation_id: str = "", timeout_seconds: int = 30) -> GitLockRecord:
    lock_file = _lock_path(repo_root)
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_id = new_id("gl")
    holder_id = str(os.getpid())
    acquired_at = utc_now_iso()
    fd = None
    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR, 0o644)
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (BlockingIOError, OSError):
                if time.monotonic() >= deadline:
                    os.close(fd)
                    return GitLockRecord(
                        lock_id=lock_id,
                        holder_id=holder_id,
                        operation_id=operation_id,
                        status=GIT_LOCK_TIMEOUT,
                        acquired_at=acquired_at,
                        timeout_seconds=timeout_seconds,
                        errors=["Lock acquisition timed out"],
                    )
                time.sleep(0.1)
        os.write(fd, f"{holder_id}\n".encode())
        os.fsync(fd)
        return GitLockRecord(
            lock_id=lock_id,
            holder_id=holder_id,
            operation_id=operation_id,
            status=GIT_LOCK_ACQUIRED,
            acquired_at=acquired_at,
            timeout_seconds=timeout_seconds,
        )
    except Exception as e:
        if fd is not None:
            os.close(fd)
        return GitLockRecord(
            lock_id=lock_id,
            holder_id=holder_id,
            operation_id=operation_id,
            status=GIT_LOCK_BLOCKED,
            acquired_at=acquired_at,
            timeout_seconds=timeout_seconds,
            errors=[f"Lock acquisition failed: {e}"],
        )


def release_git_lock(repo_root: str, lock_record: GitLockRecord) -> None:
    lock_file = _lock_path(repo_root)
    try:
        fd = os.open(str(lock_file), os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except Exception:
        pass
    finally:
        lock_record.status = GIT_LOCK_RELEASED
        lock_record.released_at = utc_now_iso()


def is_git_lock_stale(repo_root: str, max_age_seconds: int = 300) -> bool:
    lock_file = _lock_path(repo_root)
    if not lock_file.exists():
        return False
    try:
        age = time.time() - lock_file.stat().st_mtime
        return age > max_age_seconds
    except Exception:
        return False
