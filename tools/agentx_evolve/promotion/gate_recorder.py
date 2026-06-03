from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from agentx_evolve.models.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    PromotionGateDecision, canonical_json, sha256_dict,
    to_dict, write_json_atomic, append_jsonl,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


class LockUnavailableError(Exception):
    pass


def _gate_dir(repo_root: Path) -> Path:
    return promotion_runs_dir(repo_root)


def write_gate_decision(decision: PromotionGateDecision, repo_root: Path) -> Path:
    return write_latest_gate_decision(decision, repo_root)


def append_gate_decision_history(decision: PromotionGateDecision, repo_root: Path) -> Path:
    path = _gate_dir(repo_root) / "gate_decision_history.jsonl"
    return append_jsonl(path, to_dict(decision))


def append_blocked_promotion(decision: PromotionGateDecision, repo_root: Path) -> Path:
    path = _gate_dir(repo_root) / "blocked_promotions.jsonl"
    return append_jsonl(path, to_dict(decision))


def append_invalid_promotion(decision: PromotionGateDecision, repo_root: Path) -> Path:
    path = _gate_dir(repo_root) / "invalid_promotions.jsonl"
    return append_jsonl(path, to_dict(decision))


def write_latest_gate_decision(decision: PromotionGateDecision, repo_root: Path) -> Path:
    path = _gate_dir(repo_root) / "latest_gate_decision.json"
    return write_json_atomic(path, to_dict(decision))


def acquire_promotion_lock(
    repo_root: Path,
    timeout_seconds: int = 10,
    stale_lock_age_seconds: int = 900,
    allow_stale_lock_recovery: bool = False,
) -> None:
    import time
    import os
    lock_dir = _gate_dir(repo_root)
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_file = lock_dir / ".promotion_gate.lock"
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            if lock_file.exists():
                age = time.time() - lock_file.stat().st_mtime
                if age > stale_lock_age_seconds:
                    if allow_stale_lock_recovery:
                        lock_file.unlink()
                    else:
                        raise LockUnavailableError(
                            f"Stale lock found, age={age:.0f}s > {stale_lock_age_seconds}s "
                            f"and allow_stale_lock_recovery=False"
                        )
                else:
                    time.sleep(0.1)
                    continue
            lock_file.write_text(f"pid={os.getpid()}\nacquired_at={utc_now_iso()}\n")
            return
        except LockUnavailableError:
            raise
        except OSError:
            time.sleep(0.1)
    raise LockUnavailableError(
        f"Could not acquire promotion lock within {timeout_seconds}s"
    )


def release_promotion_lock(repo_root: Path) -> None:
    lock_file = _gate_dir(repo_root) / ".promotion_gate.lock"
    try:
        if lock_file.exists():
            lock_file.unlink()
    except OSError:
        pass
