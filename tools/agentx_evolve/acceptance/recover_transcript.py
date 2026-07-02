"""Recover the command transcript from record_command debug NDJSON.
The main transcript JSON can be reset by some test fixtures during test-evolve.
This script reconstructs the canonical transcript from the append-only debug log.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports")
TRANSCRIPT_PATH = REPORT_DIR / "functional_runtime_mvp_command_transcript.json"
DEB_PATH = REPORT_DIR / "record_command_debug.ndjson"
CHECKPOINT_PATH = REPORT_DIR / "functional_runtime_mvp_transcript_checkpoint.json"


def recover() -> list[dict]:
    if not DEB_PATH.exists():
        return []
    entries: dict[int, dict] = {}
    with open(DEB_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            entry = record.get("_entry")
            if not entry:
                continue
            idx = entry.get("cmd_index")
            if idx is not None:
                entries[idx] = entry
    # Sort by index
    sorted_entries = [entries[k] for k in sorted(entries)]
    return sorted_entries


def main() -> int:
    recovered = recover()
    if not recovered:
        print("recover-transcript: no debug entries found")
        return 1
    TRANSCRIPT_PATH.write_text(json.dumps(recovered, indent=2), encoding="utf-8")
    print(f"recover-transcript: recovered {len(recovered)} entries to {TRANSCRIPT_PATH}")
    # Also write checkpoint
    CHECKPOINT_PATH.write_text(json.dumps(recovered, indent=2), encoding="utf-8")
    print(f"recover-transcript: checkpoint saved ({len(recovered)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
