"""LocalTracePort — L0 seed trace port backed by atomic JSONL files."""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[3] / ".local" / "runtime" / "traces"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            __import__("logging").getLogger(__name__).debug("temp cleanup failure", exc_info=True)
        raise


class LocalTracePort:
    runtime_safety_class = "production_seed_port"
    SCHEMA_VERSION = "seed.trace.v1"

    def __init__(self) -> None:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)

    def write(self, run_id: str, events: list[dict]) -> str:
        trace = {
            "schema_version": self.SCHEMA_VERSION,
            "artifact_type": "trace",
            "run_id": run_id,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "events": events,
        }
        ref = f"trace-{run_id}" if run_id else f"trace-{uuid.uuid4().hex[:12]}"
        _atomic_write(_DATA_DIR / f"{ref}.json", json.dumps(trace, indent=2, default=str))
        return ref
