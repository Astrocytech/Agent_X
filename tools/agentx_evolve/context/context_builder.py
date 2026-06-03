from __future__ import annotations
from pathlib import Path
from typing import Any

from agentx_evolve.context.context_models import (
    TaskInput, ContextPack, TaskPack,
    TaskPacket, TaskPacketBuilder, Snippet, ArtifactRef, ValidationPlan,
    new_id, utc_now_iso,
    TP_DRAFT, TP_READY, TP_BLOCKED, TP_INVALID,
    COMPATIBLE,
)
from agentx_evolve.context.task_pack_builder import build_task_pack, inject_schema
from agentx_evolve.context.task_pack_validator import validate_task_pack
from agentx_evolve.context.context_source_loader import select_files, select_artifacts
from agentx_evolve.context.validation_error_summarizer import summarize_test_output


class ContextBuilder:
    def __init__(self, repo_path: str = "", max_tokens: int = 8192):
        self._repo_path = repo_path
        self._max_tokens = max_tokens

    @property
    def budgeter(self) -> dict:
        return {"max_tokens": self._max_tokens, "used": 0}

    def build_packet(self, *, task_type: str, objective: str,
                     candidate_files: list[str] | None = None,
                     available_artifacts: list[dict] | None = None,
                     schemas: dict[str, Any] | None = None,
                     constraints: list[str] | None = None,
                     governance_result: dict | None = None,
                     risk_assessment: dict | None = None,
                     test_output: str | None = None,
                     ) -> TaskPacket:
        builder = TaskPacketBuilder()
        builder.with_task_type(task_type)
        builder.with_objective(objective)
        builder.with_token_budget(self._max_tokens)

        if governance_result:
            builder.with_governance_result(governance_result)
        if risk_assessment:
            builder._packet.risk_assessment = risk_assessment
        if constraints:
            builder.with_constraints(constraints)

        file_result = select_files(objective, task_type, candidate_files)
        if file_result.errors:
            for err in file_result.errors:
                builder._packet.errors.append(err)

        builder.with_allowed_files(file_result.allowed)
        builder.with_forbidden_files(file_result.forbidden)

        snippets: list[Snippet] = []
        for match in file_result.matches:
            snippets.append(Snippet(
                file_path=match.file_path,
                start_line=match.start_line,
                end_line=match.end_line,
                content=match.snippet,
                relevance_score=match.relevance_score,
            ))
        builder.with_source_snippets(snippets)

        if available_artifacts:
            art_result = select_artifacts(task_type, objective, available_artifacts)
            artifacts = [
                ArtifactRef(
                    artifact_id=m.artifact_id,
                    artifact_type=m.artifact_type,
                    description=m.description,
                )
                for m in art_result.selected
            ]
            builder.with_relevant_artifacts(artifacts)

        if schemas:
            output_schema = inject_schema(task_type, schemas)
            if output_schema:
                builder.with_output_schema(output_schema)

        validation_plan = ValidationPlan()
        if file_result.allowed:
            validation_plan.expected_files = list(file_result.allowed)
        if constraints:
            validation_plan.forbidden_changes = [
                c for c in constraints if "forbidden" in c.lower() or "block" in c.lower()
            ]
        builder.with_validation_plan(validation_plan)

        if test_output:
            summary = summarize_test_output(test_output)
            builder._packet.relevant_artifacts.append(ArtifactRef(
                artifact_id="validation-errors",
                artifact_type="validation_error_summary",
                description=summary.summary_text,
            ))

        raw_task = {"task_title": objective, "task_description": objective, "task_type": task_type}
        if constraints:
            raw_task["user_constraints"] = constraints
        source_requests = []
        if candidate_files:
            for f in candidate_files:
                source_requests.append({
                    "source_id": f"file:{f}",
                    "source_type": "REPOSITORY_FILE",
                    "source_component": "file_selector",
                    "source_path": f,
                    "source_trust_level": "SOURCE_TRUST_VALIDATED_ARTIFACT",
                    "allowed_by_policy": True,
                })
        builder_context = {
            "max_context_tokens": self._max_tokens,
            "reserved_output_tokens": 1024,
        }
        if governance_result:
            builder_context["policy_context"] = governance_result

        new_tp = build_task_pack(raw_task, source_requests, builder_context,
                                 repo_root=Path(self._repo_path) if self._repo_path else None)
        validation = validate_task_pack(new_tp)

        token_used = 0
        if new_tp.context_pack:
            token_used = new_tp.context_pack.total_estimated_tokens
            for item in new_tp.context_pack.included_items:
                if item.source_id not in {s.file_path for s in builder._packet.source_snippets}:
                    builder._packet.source_snippets.append(Snippet(
                        file_path=item.source_id,
                        content=item.content,
                    ))
        builder.with_token_used(token_used)

        if new_tp.context_pack and new_tp.context_pack.total_estimated_tokens > self._max_tokens:
            builder._packet.warnings.append(
                f"Token budget exceeded: {new_tp.context_pack.total_estimated_tokens} > {self._max_tokens}"
            )

        if validation.get("errors"):
            builder._packet.errors.extend(validation["errors"])
        if validation.get("warnings"):
            builder._packet.warnings.extend(validation["warnings"])
        if validation.get("status") in (TP_BLOCKED, TP_INVALID):
            builder._packet.warnings.append(f"TaskPack validation: {validation['status']}")

        return builder.build()
