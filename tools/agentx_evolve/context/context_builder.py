from __future__ import annotations
from typing import Any
from agentx_evolve.context.task_packet import (
    TaskPacket, TaskPacketBuilder, Snippet, ArtifactRef, ValidationPlan,
)
from agentx_evolve.context.file_selector import FileSelector
from agentx_evolve.context.artifact_selector import ArtifactSelector
from agentx_evolve.context.context_budgeter import ContextBudgeter
from agentx_evolve.context.context_compressor import ContextCompressor
from agentx_evolve.context.schema_injector import SchemaInjector
from agentx_evolve.context.validation_error_summarizer import ValidationErrorSummarizer


class ContextBuilder:
    def __init__(self, repo_path: str = "", max_tokens: int = 8192):
        self._file_selector = FileSelector(repo_path=repo_path)
        self._artifact_selector = ArtifactSelector()
        self._budgeter = ContextBudgeter(max_tokens=max_tokens)
        self._compressor = ContextCompressor()
        self._schema_injector = SchemaInjector()
        self._error_summarizer = ValidationErrorSummarizer()

    @property
    def budgeter(self) -> ContextBudgeter:
        return self._budgeter

    def build_packet(self, *, task_type: str, objective: str,
                     candidate_files: list[str] | None = None,
                     available_artifacts: list[dict] | None = None,
                     schemas: dict[str, Any] | None = None,
                     constraints: list[str] | None = None,
                     governance_result: dict | None = None,
                     risk_assessment: dict | None = None,
                     test_output: str | None = None,
                     ) -> TaskPacket:
        self._budgeter.reset()

        builder = TaskPacketBuilder()
        builder.with_task_type(task_type)
        builder.with_objective(objective)
        builder.with_token_budget(self._budgeter.max_tokens)

        if governance_result:
            builder.with_governance_result(governance_result)
        if risk_assessment:
            builder.with_risk_assessment(risk_assessment)
        if constraints:
            builder.with_constraints(constraints)

        file_result = self._file_selector.select(objective, task_type, candidate_files)
        if file_result.errors:
            for err in file_result.errors:
                builder._packet.errors.append(err)

        builder.with_allowed_files(file_result.allowed)
        builder.with_forbidden_files(file_result.forbidden)

        snippets = []
        for match in file_result.matches:
            self._budgeter.consume(f"{match.file_path}\n")
            snippets.append(Snippet(
                file_path=match.file_path,
                start_line=match.start_line,
                end_line=match.end_line,
                content=match.snippet,
                relevance_score=match.relevance_score,
            ))
        builder.with_source_snippets(snippets)

        if available_artifacts:
            art_result = self._artifact_selector.select(task_type, objective, available_artifacts)
            artifacts = []
            for match in art_result.selected:
                self._budgeter.consume(match.description)
                artifacts.append(ArtifactRef(
                    artifact_id=match.artifact_id,
                    artifact_type=match.artifact_type,
                    description=match.description,
                ))
            builder.with_relevant_artifacts(artifacts)

        output_schema = self._schema_injector.inject(task_type, schemas)
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
            error_summary = self._error_summarizer.summarize(test_output)
            builder._packet.relevant_artifacts.append(ArtifactRef(
                artifact_id="validation-errors",
                artifact_type="validation_error_summary",
                description=error_summary.summary_text,
            ))

        builder.with_token_used(self._budgeter.used)

        if self._budgeter.is_over_budget():
            builder._packet.warnings.append(
                f"Token budget exceeded: {self._budgeter.used} > {self._budgeter.max_tokens}"
            )

        return builder.build()
