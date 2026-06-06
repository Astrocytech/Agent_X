from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_utils import ensure_dir


@dataclass
class RetentionPolicy:
    max_days: int = 30
    max_events: int = 10000
    max_metrics: int = 100000
    max_traces: int = 5000
    max_alerts: int = 1000


def apply_retention_policy(
    base_dir: Path,
    policy: RetentionPolicy | None = None,
) -> dict[str, int]:
    if policy is None:
        policy = RetentionPolicy()
    cutoff = datetime.now(timezone.utc) - timedelta(days=policy.max_days)
    cutoff_str = cutoff.isoformat()
    removed: dict[str, int] = {"events": 0, "metrics": 0, "traces": 0, "alerts": 0}

    for subdir, kind in [
        ("events", "events"), ("metrics", "metrics"),
        ("traces", "traces"), ("alerts", "alerts"),
    ]:
        dir_path = base_dir / subdir
        if not dir_path.exists():
            continue
        for f in dir_path.iterdir():
            if f.suffix in (".jsonl", ".json"):
                try:
                    content = f.read_text()
                    lines = content.strip().split("\n")
                    kept = []
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            import json
                            data = json.loads(line)
                            ts = data.get("timestamp", "")
                            if ts and ts >= cutoff_str:
                                kept.append(line)
                        except (json.JSONDecodeError, KeyError):
                            kept.append(line)
                    if len(kept) < len(lines):
                        f.write_text("\n".join(kept) + "\n")
                        removed[kind] += len(lines) - len(kept)
                except Exception:
                    pass

    return removed


def apply_monitoring_retention_policy(
    base_dir: Path,
    policy: RetentionPolicy | None = None,
) -> dict[str, int]:
    return apply_retention_policy(base_dir, policy)
