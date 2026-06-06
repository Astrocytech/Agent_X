from __future__ import annotations
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any

from agentx_evolve.scheduler.scheduler_models import new_id, utc_now_iso

try:
    from agentx_evolve.scheduler.lease_manager import LeaseManager

    warnings.warn(
        "lease_manager.LeaseManager is deprecated; use task_lease.TaskLease instead",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    LeaseManager = None  # type: ignore

__all__ = [
    "TaskLease",
    "acquire_lease",
    "release_lease",
    "renew_lease",
]


@dataclass
class TaskLease:
    task_id: str = ""
    worker_id: str = ""
    acquired_at: str = ""
    expires_at: str = ""
    lease_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def acquire_lease(
    task: dict[str, Any],
    worker: str,
    duration: int = 300,
) -> dict[str, Any]:
    now = utc_now_iso()
    now_dt = datetime.now(timezone.utc)
    expires_dt = now_dt + timedelta(seconds=duration)
    expires_at = expires_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{expires_dt.microsecond:06d}Z"
    return {
        "status": "LEASE_ACQUIRED",
        "lease_id": new_id("ls"),
        "task_id": task.get("task_id", ""),
        "worker_id": worker,
        "acquired_at": now,
        "expires_at": expires_at,
    }


def release_lease(lease: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "LEASE_RELEASED",
        "lease_id": lease.get("lease_id", ""),
        "task_id": lease.get("task_id", ""),
    }


def renew_lease(lease: dict[str, Any], duration: int = 300) -> dict[str, Any]:
    now_dt = datetime.now(timezone.utc)
    expires_dt = now_dt + timedelta(seconds=duration)
    expires_at = expires_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{expires_dt.microsecond:06d}Z"
    return {
        "status": "LEASE_RENEWED",
        "lease_id": lease.get("lease_id", ""),
        "expires_at": expires_at,
    }
