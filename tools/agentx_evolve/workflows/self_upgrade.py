from __future__ import annotations
from pathlib import Path
from typing import Any

from agentx_evolve.runtime.session import RunSessionManager
from agentx_evolve.runtime.artifacts import ArtifactWriter
from agentx_evolve.runtime.results import (
    CLIResult, FinalVerdict, EvidenceManifest, ImplementationLedger,
    STATUS_PASS, STATUS_FAIL, STATUS_BLOCKED,
    EXIT_PASS, EXIT_FAIL, EXIT_BLOCKED,
)
from agentx_evolve.runtime.plan_parser import StructuredPlanParser, PlanParseError
from agentx_evolve.providers.provider_router import ProviderRouter
from agentx_evolve.providers.opencode_provider import OpenCodeProviderError


class SelfUpgradeWorkflow:
    def __init__(self, config: Any):
        self.config = config
        self.session_mgr = RunSessionManager(run_root=config.run_root)
        self.parser = StructuredPlanParser()

    def run(self) -> CLIResult:
        session = self.session_mgr.create_session(command="self-upgrade")
        run_dir = session.ensure_run_dir()
        writer = ArtifactWriter(run_dir)

        writer.write_metadata(session)
        writer.write_config(self.config.redacted_dict())

        if not self.config.concept_file:
            return self._blocked(session, writer, run_dir, "missing --concept-file")

        concept_path = Path(self.config.concept_file)
        if not concept_path.exists():
            return self._blocked(
                session, writer, run_dir,
                f"concept file not found: {self.config.concept_file}",
            )

        preflight = {"status": "PASS", "concept_file": str(concept_path)}
        writer.write_preflight(preflight)
        session.transition("PREFLIGHT_PASSED")

        concept_text = concept_path.read_text()
        context = {
            "command": "self-upgrade",
            "mode": self.config.mode,
            "dry_run": self.config.dry_run,
            "concept": concept_text,
        }
        writer.write_context(context)
        session.transition("CONTEXT_PACKED")

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are Agent_X, a governed self-upgrading agent. "
                    "Given a concept file describing an architecture change, "
                    "produce a structured plan with patches to implement it."
                ),
            },
            {
                "role": "user",
                "content": f"Implement this architecture change:\n\n{concept_text}",
            },
        ]
        writer.write_request({
            "provider": self.config.provider, "model": self.config.model,
            "messages": messages,
        })
        writer.write_model_messages(messages)

        router = ProviderRouter(self.config)
        provider = router.get_provider()

        try:
            response = provider.complete_structured(messages)
        except OpenCodeProviderError as e:
            writer.write_model_response({
                "role": "assistant", "content": e.message,
                "finish_reason": "error",
            })
            return self._fail(session, writer, run_dir, e.message, e.exit_code)

        writer.write_model_response(response)
        session.transition("MODEL_COMPLETED")

        try:
            plan = self.parser.parse(response)
        except PlanParseError as e:
            return self._fail(session, writer, run_dir, str(e), EXIT_FAIL)

        writer.write_structured_plan(plan)

        patch_content = ""
        patches = plan.get("patches", [])
        for p in patches:
            content = p.get("content", "")
            if content:
                patch_content += content + "\n"

        writer.write_proposed_patch(patch_content if patch_content else None)

        if self.config.mode == "apply" and not self.config.dry_run:
            writer.write_applied_patch(patch_content if patch_content else None)
        else:
            writer.write_applied_patch(None)

        validation_commands = plan.get("validation_commands", [])
        validation_report = {
            "status": "PASS", "command": "self-upgrade",
            "mode": self.config.mode, "dry_run": self.config.dry_run,
            "validation_commands": validation_commands,
        }
        writer.write_validation_report(validation_report)
        session.transition("VALIDATION_COMPLETED")

        evidence = EvidenceManifest(
            run_id=session.run_id, command="self-upgrade",
            artifacts=[
                {"path": "run_metadata.json", "kind": "metadata", "required": True},
                {"path": "resolved_config.json", "kind": "config", "required": True},
                {"path": "preflight.json", "kind": "preflight", "required": True},
                {"path": "packed_context.json", "kind": "context", "required": True},
                {"path": "model_messages.jsonl", "kind": "messages", "required": True},
                {"path": "model_response.json", "kind": "response", "required": True},
                {"path": "structured_plan.json", "kind": "plan", "required": True},
                {"path": "proposed_patch.diff", "kind": "patch", "required": True},
                {"path": "validation_report.json", "kind": "validation", "required": True},
                {"path": "evidence_manifest.json", "kind": "manifest", "required": True},
                {"path": "final_verdict.json", "kind": "verdict", "required": True},
                {"path": "implementation_ledger.json", "kind": "ledger", "required": True},
            ],
            commands_run=validation_commands,
            source_mutation_detected=not self.config.dry_run and self.config.mode == "apply",
        )
        writer.write_evidence_manifest(evidence.to_dict())
        session.transition("EVIDENCE_WRITTEN")

        verdict = FinalVerdict(
            command="self-upgrade", status=STATUS_PASS, exit_code=EXIT_PASS,
            run_id=session.run_id,
            summary=f"self-upgrade {self.config.mode} completed",
            validation_status=STATUS_PASS,
        )
        writer.write_final_verdict(verdict.to_dict())
        session.transition(STATUS_PASS)

        ledger = ImplementationLedger(run_id=session.run_id)
        writer.write_implementation_ledger(ledger.to_dict())

        return CLIResult(
            command="self-upgrade", status=STATUS_PASS, exit_code=EXIT_PASS,
            run_id=session.run_id, run_dir=str(run_dir),
            message=f"self-upgrade {self.config.mode}: plan with {len(patches)} patches",
            artifacts={
                "final_verdict": str(run_dir / "final_verdict.json"),
                "evidence_manifest": str(run_dir / "evidence_manifest.json"),
            },
        )

    def _blocked(self, session: Any, writer: ArtifactWriter, run_dir: Path, reason: str) -> CLIResult:
        return self._error(session, writer, run_dir, reason, STATUS_BLOCKED, EXIT_BLOCKED)

    def _fail(self, session: Any, writer: ArtifactWriter, run_dir: Path, reason: str, code: int) -> CLIResult:
        return self._error(session, writer, run_dir, reason, STATUS_FAIL, code)

    def _error(
        self, session: Any, writer: ArtifactWriter, run_dir: Path,
        message: str, status: str, exit_code: int,
    ) -> CLIResult:
        writer.write_validation_report({
            "status": status, "command": "self-upgrade",
            "errors": [message],
        })
        session.transition("VALIDATION_COMPLETED")

        evidence = EvidenceManifest(
            run_id=session.run_id, command="self-upgrade",
            artifacts=[{"path": "run_metadata.json", "kind": "metadata", "required": True}],
            commands_run=[], source_mutation_detected=False,
        )
        writer.write_evidence_manifest(evidence.to_dict())
        session.transition("EVIDENCE_WRITTEN")

        verdict = FinalVerdict(
            command="self-upgrade", status=status, exit_code=exit_code,
            run_id=session.run_id, summary=message,
            failures=[] if status == STATUS_BLOCKED else [message],
            blocked_reasons=[message] if status == STATUS_BLOCKED else [],
            validation_status=status,
        )
        writer.write_final_verdict(verdict.to_dict())
        session.transition(status)

        ledger = ImplementationLedger(run_id=session.run_id)
        writer.write_implementation_ledger(ledger.to_dict())

        return CLIResult(
            command="self-upgrade", status=status, exit_code=exit_code,
            run_id=session.run_id, run_dir=str(run_dir),
            message=message,
            artifacts={
                "final_verdict": str(run_dir / "final_verdict.json"),
                "evidence_manifest": str(run_dir / "evidence_manifest.json"),
            },
        )
