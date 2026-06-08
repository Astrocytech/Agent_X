from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Any

from agentx_evolve.runtime.session import RunSessionManager
from agentx_evolve.runtime.artifacts import ArtifactWriter
from agentx_evolve.runtime.results import (
    CLIResult, FinalVerdict, EvidenceManifest, ImplementationLedger,
    STATUS_PASS, STATUS_FAIL, STATUS_BLOCKED,
    EXIT_PASS, EXIT_FAIL, EXIT_BLOCKED,
)

SEED_DIRS = ["L0", "L1", "L2"]
_SEED_ROOT = Path(__file__).resolve().parent.parent.parent.parent
NEVER_COPY = {
    ".git", ".venv", "__pycache__", ".pytest_cache",
    ".env", "*.key", "*.pem", ".agentx-init/runs",
}


class InitAgentWorkflow:
    def __init__(self, config: Any):
        self.config = config
        self.session_mgr = RunSessionManager(run_root=config.run_root)

    def run(self) -> CLIResult:
        session = self.session_mgr.create_session(command="init-agent")
        run_dir = session.ensure_run_dir()
        writer = ArtifactWriter(run_dir)

        writer.write_metadata(session)
        writer.write_config(self.config.redacted_dict())

        if not self.config.agent_name:
            return self._blocked(session, writer, run_dir, "missing --name")
        if not self.config.dest:
            return self._blocked(session, writer, run_dir, "missing --dest")

        dest = Path(self.config.dest)
        if dest.exists():
            contents = list(dest.iterdir())
            if contents:
                return self._blocked(
                    session, writer, run_dir,
                    f"destination {dest} exists and is not empty",
                )

        preflight = {
            "status": "PASS",
            "agent_name": self.config.agent_name,
            "dest": str(dest),
        }
        writer.write_preflight(preflight)
        session.transition("PREFLIGHT_PASSED")

        dest.mkdir(parents=True, exist_ok=True)

        copied_files = self._copy_seed_files(dest)

        runtime_dir = dest / ".agentx-init" / "runs"
        runtime_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "agent_name": self.config.agent_name,
            "dest": str(dest),
            "copied_files": copied_files,
            "total_files": len(copied_files),
        }
        writer.write_context(manifest)
        session.transition("CONTEXT_PACKED")

        writer.write_request({
            "command": "init-agent",
            "agent_name": self.config.agent_name,
            "dest": str(dest),
        })

        writer.write_model_messages([])
        writer.write_model_response({
            "role": "assistant",
            "content": f"Initialized agent '{self.config.agent_name}' at {dest}",
            "finish_reason": "stop",
        })
        session.transition("MODEL_COMPLETED")

        writer.write_structured_plan(None)
        writer.write_proposed_patch(None)
        writer.write_applied_patch(None)

        validation_report = {
            "status": "PASS",
            "command": "init-agent",
            "destination_exists": dest.exists(),
            "files_copied": len(copied_files),
        }
        writer.write_validation_report(validation_report)
        session.transition("VALIDATION_COMPLETED")

        evidence = EvidenceManifest(
            run_id=session.run_id, command="init-agent",
            artifacts=[
                {"path": "run_metadata.json", "kind": "metadata", "required": True},
                {"path": "resolved_config.json", "kind": "config", "required": True},
                {"path": "preflight.json", "kind": "preflight", "required": True},
                {"path": "packed_context.json", "kind": "context", "required": True},
                {"path": "validation_report.json", "kind": "validation", "required": True},
                {"path": "evidence_manifest.json", "kind": "manifest", "required": True},
                {"path": "final_verdict.json", "kind": "verdict", "required": True},
                {"path": "implementation_ledger.json", "kind": "ledger", "required": True},
            ],
            commands_run=[],
            source_mutation_detected=False,
        )
        writer.write_evidence_manifest(evidence.to_dict())
        session.transition("EVIDENCE_WRITTEN")

        verdict = FinalVerdict(
            command="init-agent", status=STATUS_PASS, exit_code=EXIT_PASS,
            run_id=session.run_id,
            summary=f"initialized agent '{self.config.agent_name}'",
            validation_status=STATUS_PASS,
        )
        writer.write_final_verdict(verdict.to_dict())
        session.transition(STATUS_PASS)

        ledger = ImplementationLedger(run_id=session.run_id)
        writer.write_implementation_ledger(ledger.to_dict())

        return CLIResult(
            command="init-agent", status=STATUS_PASS, exit_code=EXIT_PASS,
            run_id=session.run_id, run_dir=str(run_dir),
            message=f"Agent '{self.config.agent_name}' initialized at {dest} ({len(copied_files)} files)",
            artifacts={
                "final_verdict": str(run_dir / "final_verdict.json"),
                "evidence_manifest": str(run_dir / "evidence_manifest.json"),
            },
        )

    def _copy_seed_files(self, dest: Path) -> list[str]:
        copied: list[str] = []
        for seed_dir_name in SEED_DIRS:
            seed_dir = _SEED_ROOT / seed_dir_name
            if not seed_dir.exists() or not seed_dir.is_dir():
                continue
            for root, dirs, files in os.walk(str(seed_dir)):
                rel_root = Path(root).relative_to(seed_dir)
                dirs[:] = [d for d in dirs if d not in NEVER_COPY]
                for f in files:
                    if self._is_never_copy(f):
                        continue
                    src = Path(root) / f
                    dst = dest / seed_dir_name / rel_root / f
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(src), str(dst))
                    copied.append(str(dst.relative_to(dest)))
        return copied

    @staticmethod
    def _is_never_copy(filename: str) -> bool:
        for pattern in NEVER_COPY:
            if pattern.startswith("*") and filename.endswith(pattern[1:]):
                return True
            if pattern == filename:
                return True
        return False

    def _blocked(self, session: Any, writer: ArtifactWriter, run_dir: Path, reason: str) -> CLIResult:
        writer.write_preflight({"status": "BLOCKED", "reason": reason})
        writer.write_validation_report({
            "status": "BLOCKED", "command": "init-agent", "errors": [reason],
        })
        verdict = FinalVerdict(
            command="init-agent", status=STATUS_BLOCKED, exit_code=EXIT_BLOCKED,
            run_id=session.run_id, summary=reason,
            blocked_reasons=[reason], validation_status=STATUS_BLOCKED,
        )
        writer.write_final_verdict(verdict.to_dict())
        ledger = ImplementationLedger(run_id=session.run_id)
        writer.write_implementation_ledger(ledger.to_dict())
        return CLIResult(
            command="init-agent", status=STATUS_BLOCKED, exit_code=EXIT_BLOCKED,
            run_id=session.run_id, run_dir=str(run_dir), message=reason,
            artifacts={},
        )
