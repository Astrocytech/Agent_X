from __future__ import annotations
import json
from pathlib import Path
from agentx_evolve.patch_execution._v1.patch_models import ImplementationEvidence, to_dict


class ImplementationEvidenceWriter:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root.resolve()
        self._impl_dir = self._repo_root / ".agentx-init" / "implementation"

    def write_evidence(self, evidence: ImplementationEvidence) -> dict:
        evidence_path = self._impl_dir / "implementation_evidence.jsonl"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        with open(evidence_path, "a") as f:
            f.write(json.dumps(evidence.to_dict(), separators=(",", ":")) + "\n")
        return {"status": "APPENDED", "path": str(evidence_path)}

    def write_latest_session(self, session_data: dict) -> dict:
        path = self._impl_dir / "implementation_latest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".tmp.{Path(session_data.get('session_id', 'unknown'))}")
        tmp.write_text(json.dumps(session_data, indent=2, default=str))
        tmp.replace(path)
        return {"status": "WRITTEN", "path": str(path)}
