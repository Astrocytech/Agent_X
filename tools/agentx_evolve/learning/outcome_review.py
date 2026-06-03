from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import os
import time
from agentx_evolve.models.model_models import new_id

LEARNING_SCHEMA_VERSION = "1.0"
LEARNING_SCHEMA_ID = "learning_outcome_record.schema.json"

LOCK_TIMEOUT_SECONDS = 10


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


def write_json_atomic(path: Path, data: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data), encoding="utf-8")
    tmp.replace(path)
    return path


def append_jsonl(path: Path, data: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(data, separators=(",", ":")) + "\n"
    with open(str(path), "a", encoding="utf-8") as f:
        f.write(line)
    return path


@dataclass
class LearningOutcomeRecord:
    schema_version: str = LEARNING_SCHEMA_VERSION
    schema_id: str = LEARNING_SCHEMA_ID
    outcome_id: str = ""
    session_id: str = ""
    attempted_task: str = ""
    proposal_type: str = ""
    files_changed: list[str] = field(default_factory=list)
    model_used: str = ""
    validation_outcome: str = ""
    rollback_outcome: str = ""
    failure_reason: str = ""
    successful_strategy: str = ""
    future_recommendation: str = ""
    created_at: str = ""
    outcome_hash: str = ""
    tags: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class LearningOutcomeReview:
    def __init__(self):
        self._records: list[LearningOutcomeRecord] = []

    def record_outcome(self, outcome: LearningOutcomeRecord) -> None:
        if not outcome.outcome_id:
            outcome.outcome_id = new_id("lr")
        if not outcome.created_at:
            outcome.created_at = datetime.now(timezone.utc).isoformat()
        if not outcome.outcome_hash:
            d = to_dict(outcome)
            d.pop("outcome_hash", None)
            outcome.outcome_hash = sha256_dict(d)
        self._records.append(outcome)

    def get_by_session(self, session_id: str) -> list[LearningOutcomeRecord]:
        return [r for r in self._records if r.session_id == session_id]

    def get_by_tag(self, tag: str) -> list[LearningOutcomeRecord]:
        return [r for r in self._records if tag in r.tags]

    def get_successful_strategies(self) -> list[LearningOutcomeRecord]:
        return [r for r in self._records if r.successful_strategy]

    def get_failure_patterns(self) -> list[LearningOutcomeRecord]:
        return [r for r in self._records if r.failure_reason]

    def get_recommendations(self) -> list[str]:
        return [r.future_recommendation for r in self._records if r.future_recommendation]

    def list_all(self) -> list[LearningOutcomeRecord]:
        return list(self._records)

    def write_outcome_history(self, repo_root: str | Path) -> Path:
        lock = self.acquire_learning_lock(repo_root)
        try:
            dest = Path(repo_root) / ".agentx-init" / "learning" / "outcome_history.json"
            records_dict = [to_dict(r) for r in self._records]
            return write_json_atomic(dest, {"records": records_dict})
        finally:
            self.release_learning_lock(lock, repo_root)

    def append_outcome_history(self, outcome: LearningOutcomeRecord, repo_root: str | Path) -> Path:
        lock = self.acquire_learning_lock(repo_root)
        try:
            dest = Path(repo_root) / ".agentx-init" / "learning" / "outcome_history.jsonl"
            return append_jsonl(dest, to_dict(outcome))
        finally:
            self.release_learning_lock(lock, repo_root)

    def acquire_learning_lock(self, repo_root: str | Path, timeout_seconds: int = LOCK_TIMEOUT_SECONDS) -> object:
        lock_path = Path(repo_root) / ".agentx-init" / "learning" / ".learning.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return {"acquired": True, "path": str(lock_path)}
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Could not acquire learning lock within {timeout_seconds}s: {lock_path}")
                time.sleep(0.1)

    def release_learning_lock(self, lock: object, repo_root: str | Path) -> None:
        lock_path = Path(repo_root) / ".agentx-init" / "learning" / ".learning.lock"
        try:
            lock_path.unlink(missing_ok=True)
        except FileNotFoundError:
            pass


class StrategyMemory:
    def __init__(self):
        self._store: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        self._store[key] = value

    def retrieve(self, key: str) -> Any | None:
        return self._store.get(key)

    def search(self, prefix: str) -> dict[str, Any]:
        return {k: v for k, v in self._store.items() if k.startswith(prefix)}

    def clear(self) -> None:
        self._store.clear()

    def persist_memory(self, repo_root: str | Path) -> Path:
        lock_path = Path(repo_root) / ".agentx-init" / "learning" / ".learning.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                break
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Could not acquire learning lock for memory persist within {LOCK_TIMEOUT_SECONDS}s")
                time.sleep(0.1)
        try:
            dest = Path(repo_root) / ".agentx-init" / "learning" / "strategy_memory.json"
            return write_json_atomic(dest, self._store)
        finally:
            try:
                lock_path.unlink(missing_ok=True)
            except FileNotFoundError:
                pass

    def load_memory(self, repo_root: str | Path) -> None:
        src = Path(repo_root) / ".agentx-init" / "learning" / "strategy_memory.json"
        if src.exists():
            raw = src.read_text(encoding="utf-8")
            self._store = json.loads(raw)
