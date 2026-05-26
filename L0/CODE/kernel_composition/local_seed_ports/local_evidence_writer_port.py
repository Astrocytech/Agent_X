"""LocalEvidenceWriterPort — writes evidence envelopes to the local filesystem."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


class LocalEvidenceWriterPort:
    runtime_safety_class = "production_seed_port"

    def __init__(self, base_path: str = ".local/runtime/evidence") -> None:
        self._base = Path(base_path)

    def write(self, event_type: str, payload: dict[str, Any]) -> str:
        self._base.mkdir(parents=True, exist_ok=True)
        evidence_id = f"ev-{uuid.uuid4().hex[:12]}"
        (self._base / f"{evidence_id}.json").write_text(
            json.dumps({"event_type": event_type, "payload": payload}, default=str),
            encoding="utf-8",
        )
        return evidence_id
