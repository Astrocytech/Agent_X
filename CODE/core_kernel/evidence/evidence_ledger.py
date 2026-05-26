"""evidence_ledger — Append-only evidence ledger for turn results.

Each turn writes an evidence entry. Entries are used to back release claims,
universality scores, and promotion decisions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEDGER_PATH = Path(".local/runtime/evidence/evidence_ledger.jsonl")


def record_evidence(entry: dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_recent_evidence(limit: int = 10) -> list[dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    entries: list[dict[str, Any]] = []
    with open(LEDGER_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries[-limit:]
