from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ARTIFACT_PLACEHOLDER_SCHEMA = "agentx.artifact_placeholder.v1"


def make_placeholder(reason: str = "not applicable") -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_PLACEHOLDER_SCHEMA,
        "status": "NOT_APPLICABLE",
        "reason": reason,
    }


class ArtifactWriter:
    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)

    def ensure_dir(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def atomic_write(self, name: str, data: dict[str, Any] | list | str) -> Path:
        self.ensure_dir()
        path = self.run_dir / name

        if isinstance(data, (dict, list)):
            content = json.dumps(data, indent=2, default=str)
        else:
            content = str(data)

        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.run_dir),
            prefix=f".{name}.tmp.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, str(path))
        except BaseException:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

        return path

    def write_metadata(self, session: Any) -> Path:
        return self.atomic_write("run_metadata.json", session.to_dict())

    def write_request(self, request: dict[str, Any]) -> Path:
        return self.atomic_write("request.json", request)

    def write_config(self, config: dict[str, Any]) -> Path:
        return self.atomic_write("resolved_config.json", config)

    def write_preflight(self, preflight: dict[str, Any]) -> Path:
        return self.atomic_write("preflight.json", preflight)

    def write_context(self, context: dict[str, Any]) -> Path:
        return self.atomic_write("packed_context.json", context)

    def write_model_messages(self, messages: list[dict[str, Any]]) -> Path:
        lines = "\n".join(json.dumps(m, default=str) for m in messages)
        return self.atomic_write("model_messages.jsonl", lines)

    def write_model_response(self, response: dict[str, Any]) -> Path:
        return self.atomic_write("model_response.json", response)

    def write_structured_plan(self, plan: dict[str, Any] | None) -> Path:
        data = plan if plan is not None else make_placeholder("no plan for this command")
        return self.atomic_write("structured_plan.json", data)

    def write_proposed_patch(self, content: str | None) -> Path:
        data = content if content is not None else make_placeholder("no patch for this command")
        return self.atomic_write("proposed_patch.diff", data)

    def write_applied_patch(self, content: str | None) -> Path:
        data = content if content is not None else make_placeholder("no patch applied")
        return self.atomic_write("applied_patch.diff", data)

    def write_validation_report(self, report: dict[str, Any]) -> Path:
        return self.atomic_write("validation_report.json", report)

    def write_evidence_manifest(self, manifest: dict[str, Any]) -> Path:
        return self.atomic_write("evidence_manifest.json", manifest)

    def write_final_verdict(self, verdict: dict[str, Any]) -> Path:
        return self.atomic_write("final_verdict.json", verdict)

    def write_implementation_ledger(self, ledger: dict[str, Any]) -> Path:
        return self.atomic_write("implementation_ledger.json", ledger)
