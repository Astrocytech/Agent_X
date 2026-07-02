"""Serial executor guard — prevents concurrent execution of MVP proof runs.

Uses a file-based lock in `.agentx-init/reports/` to detect and reject
concurrent runs. Also produces a lock-evidence artifact for the proof bundle.

Usage:
    python3 serial_executor_guard.py lock <run_id> [--report-dir PATH]
    python3 serial_executor_guard.py unlock <run_id> [--report-dir PATH]
    python3 serial_executor_guard.py check [--report-dir PATH]
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _lock_path(report_dir: Path) -> Path:
    return report_dir / ".mvp_run_lock"


def acquire_lock(
    run_id: str,
    report_dir: Path,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Acquire a serial execution lock. Blocks until acquired or timeout."""
    report_dir.mkdir(parents=True, exist_ok=True)
    lock_file = _lock_path(report_dir)
    deadline = time.monotonic() + timeout_seconds
    lock: dict[str, Any] = {
        "acquired": False,
        "run_id": run_id,
        "lock_held_by": "",
        "acquired_at": "",
    }
    while time.monotonic() < deadline:
        try:
            if not lock_file.exists():
                lock_data = {
                    "run_id": run_id,
                    "pid": os.getpid(),
                    "host": os.uname().nodename,
                    "acquired_at": datetime.now(timezone.utc).isoformat(),
                }
                lock_file.write_text(
                    json.dumps(lock_data, indent=2) + "\n",
                    encoding="utf-8",
                )
                lock["acquired"] = True
                lock["lock_held_by"] = run_id
                lock["acquired_at"] = lock_data["acquired_at"]
                return lock
            existing = json.loads(lock_file.read_text(encoding="utf-8"))
            lock["lock_held_by"] = existing.get("run_id", "unknown")
            # Stale lock detection: if the owning PID is no longer alive, reclaim
            owner_pid = existing.get("pid")
            if owner_pid is not None:
                try:
                    os.kill(owner_pid, 0)
                except (OSError, ProcessLookupError):
                    lock_file.unlink(missing_ok=True)
                    continue
        except (OSError, json.JSONDecodeError):
            time.sleep(0.1)
            continue
        time.sleep(0.5)
    return lock


def release_lock(run_id: str, report_dir: Path) -> dict[str, Any]:
    """Release the serial execution lock if held by the given run_id."""
    lock_file = _lock_path(report_dir)
    result: dict[str, Any] = {
        "released": False,
        "run_id": run_id,
        "lock_held_by": "",
    }
    if lock_file.exists():
        try:
            existing = json.loads(lock_file.read_text(encoding="utf-8"))
            result["lock_held_by"] = existing.get("run_id", "unknown")
            if existing.get("run_id") == run_id:
                lock_file.unlink()
                result["released"] = True
        except (OSError, json.JSONDecodeError):
            lock_file.unlink(missing_ok=True)
            result["released"] = True
    return result


def check_lock(report_dir: Path) -> dict[str, Any]:
    """Check if a lock is currently held."""
    lock_file = _lock_path(report_dir)
    if not lock_file.exists():
        return {"locked": False, "held_by": ""}
    try:
        existing = json.loads(lock_file.read_text(encoding="utf-8"))
        return {
            "locked": True,
            "held_by": existing.get("run_id", "unknown"),
            "pid": existing.get("pid"),
            "acquired_at": existing.get("acquired_at"),
        }
    except (OSError, json.JSONDecodeError):
        return {"locked": False, "held_by": ""}


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("Usage: serial_executor_guard.py <lock|unlock|check> [run_id] [--report-dir PATH]",
              file=sys.stderr)
        return 1

    command = args[0]
    run_id = ""
    report_dir = Path(".agentx-init/reports")

    i = 1
    while i < len(args):
        if args[i] == "--report-dir" and i + 1 < len(args):
            report_dir = Path(args[i + 1])
            i += 2
        elif not args[i].startswith("--") and not run_id:
            run_id = args[i]
            i += 1
        else:
            i += 1

    if command == "lock":
        if not run_id:
            print("lock requires run_id", file=sys.stderr)
            return 1
        lock = acquire_lock(run_id, report_dir)
        print(json.dumps(lock, indent=2))
        if lock.get("acquired"):
            print(f"Lock acquired for run {run_id}")
            return 0
        else:
            print(f"Lock held by {lock['lock_held_by']} — cannot acquire",
                  file=sys.stderr)
            return 1

    elif command == "unlock":
        if not run_id:
            print("unlock requires run_id", file=sys.stderr)
            return 1
        result = release_lock(run_id, report_dir)
        print(json.dumps(result, indent=2))
        if result.get("released"):
            print(f"Lock released for run {run_id}")
        else:
            print(f"Lock not held by {run_id} (held by {result['lock_held_by']})",
                  file=sys.stderr)
        return 0

    elif command == "check":
        status = check_lock(report_dir)
        print(json.dumps(status, indent=2))
        return 1 if status.get("locked") else 0

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    main()
