from __future__ import annotations
from pathlib import Path
from typing import Any

from agentx_evolve.runtime.session import RunSessionManager, STATE_PASS, STATE_FAIL
from agentx_evolve.runtime.artifacts import ArtifactWriter, make_placeholder
from agentx_evolve.runtime.results import (
    CLIResult, FinalVerdict, EvidenceManifest, ImplementationLedger,
    STATUS_PASS, STATUS_FAIL, STATUS_BLOCKED,
    EXIT_PASS, EXIT_FAIL,
)
from agentx_evolve.providers.provider_router import ProviderRouter
from agentx_evolve.providers.opencode_provider import OpenCodeProviderError


class ChatWorkflow:
    def __init__(self, config: Any):
        self.config = config
        self.session_mgr = RunSessionManager(run_root=config.run_root)

    def run(self) -> CLIResult:
        session = self.session_mgr.create_session(command="chat")
        run_dir = session.ensure_run_dir()
        writer = ArtifactWriter(run_dir)

        writer.write_metadata(session)
        writer.write_config(self.config.redacted_dict())

        preflight = {"status": "PASS", "checks": {"run_root_exists": True}}
        if self.config.once_message:
            preflight["once_message"] = self.config.once_message
        writer.write_preflight(preflight)
        session.transition("PREFLIGHT_PASSED")

        context = {
            "repo": "Agent_X",
            "command": "chat",
            "provider": self.config.provider,
            "model": self.config.model,
        }
        writer.write_context(context)
        session.transition("CONTEXT_PACKED")

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": "You are Agent_X, a governed agent system."},
            {"role": "user", "content": self.config.once_message or "hello"},
        ]
        request = {
            "provider": self.config.provider,
            "model": self.config.model,
            "messages": messages,
            "stream": False,
        }
        writer.write_request(request)

        writer.write_model_messages(messages)
        session.transition("MODEL_COMPLETED")

        router = ProviderRouter(self.config)
        provider = router.get_provider()
        try:
            response = provider.complete(messages)
        except OpenCodeProviderError as e:
            content = e.message
            status = STATUS_FAIL if e.status == "FAIL" else STATUS_BLOCKED
            exit_code = e.exit_code
            return self._build_error_result(
                session, writer, run_dir, content, status, exit_code,
            )
        writer.write_model_response(response)

        writer.write_structured_plan(None)
        writer.write_proposed_patch(None)
        writer.write_applied_patch(None)

        validation_report = {
            "status": "PASS",
            "command": "chat",
            "validation_results": [],
            "warnings": [],
        }
        writer.write_validation_report(validation_report)
        session.transition("VALIDATION_COMPLETED")

        evidence = EvidenceManifest(
            run_id=session.run_id,
            command="chat",
            artifacts=[
                {"path": "run_metadata.json", "kind": "metadata", "required": True},
                {"path": "resolved_config.json", "kind": "config", "required": True},
                {"path": "preflight.json", "kind": "preflight", "required": True},
                {"path": "packed_context.json", "kind": "context", "required": True},
                {"path": "model_messages.jsonl", "kind": "messages", "required": True},
                {"path": "model_response.json", "kind": "response", "required": True},
                {"path": "structured_plan.json", "kind": "plan", "required": False},
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

        content = response.get("content", "")
        status = STATUS_PASS
        exit_code = EXIT_PASS
        summary = f"{self.config.provider} chat completed"
        failures: list[str] = []

        if not content:
            status = STATUS_FAIL
            exit_code = EXIT_FAIL
            failures.append("empty response from provider")

        verdict = FinalVerdict(
            command="chat",
            status=status,
            exit_code=exit_code,
            run_id=session.run_id,
            summary=summary,
            failures=failures,
            blocked_reasons=[],
            validation_status=STATUS_PASS,
        )
        writer.write_final_verdict(verdict.to_dict())
        session.transition(status)

        ledger = ImplementationLedger(
            run_id=session.run_id,
            repo_drift_notes=[],
            compatibility_shims_used=[],
            deviations_from_brief=[],
            files_changed_by_command=[],
        )
        writer.write_implementation_ledger(ledger.to_dict())

        message = content if content else "chat completed"

        result = CLIResult(
            command="chat",
            status=status,
            exit_code=exit_code,
            run_id=session.run_id,
            run_dir=str(run_dir),
            message=message,
            artifacts={
                "final_verdict": str(run_dir / "final_verdict.json"),
                "evidence_manifest": str(run_dir / "evidence_manifest.json"),
            },
        )
        return result

    def _build_error_result(
        self,
        session: Any,
        writer: ArtifactWriter,
        run_dir: Path,
        message: str,
        status: str,
        exit_code: int,
    ) -> CLIResult:
        writer.write_model_response({
            "role": "assistant",
            "content": message,
            "tool_calls": [],
            "finish_reason": "error",
        })
        writer.write_structured_plan(None)
        writer.write_proposed_patch(None)
        writer.write_applied_patch(None)
        writer.write_validation_report({
            "status": status, "command": "chat",
            "validation_results": [], "warnings": [],
        })
        session.transition("VALIDATION_COMPLETED")

        evidence = EvidenceManifest(
            run_id=session.run_id, command="chat",
            artifacts=[{"path": "run_metadata.json", "kind": "metadata", "required": True}],
            commands_run=[], source_mutation_detected=False,
        )
        writer.write_evidence_manifest(evidence.to_dict())
        session.transition("EVIDENCE_WRITTEN")

        blocked = [message] if status == "BLOCKED" else []
        verdict = FinalVerdict(
            command="chat", status=status, exit_code=exit_code,
            run_id=session.run_id, summary=message,
            failures=[] if status == "BLOCKED" else [message],
            blocked_reasons=blocked,
            validation_status=status,
        )
        writer.write_final_verdict(verdict.to_dict())
        session.transition(status)

        ledger = ImplementationLedger(run_id=session.run_id)
        writer.write_implementation_ledger(ledger.to_dict())

        return CLIResult(
            command="chat", status=status, exit_code=exit_code,
            run_id=session.run_id, run_dir=str(run_dir),
            message=message,
            artifacts={
                "final_verdict": str(run_dir / "final_verdict.json"),
                "evidence_manifest": str(run_dir / "evidence_manifest.json"),
            },
        )
