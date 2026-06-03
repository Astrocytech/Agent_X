from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentx_evolve.model.model_models import new_id, utc_now_iso, to_dict

TP_SCHEMA_VERSION = "1.0"

TT_IMPLEMENT_PATCH = "IMPLEMENT_PATCH"
TT_FIX_VALIDATION = "FIX_VALIDATION"
TT_WRITE_TEST = "WRITE_TEST"
TT_EXPLAIN_FAILURE = "EXPLAIN_FAILURE"
ALL_TASK_TYPES = [TT_IMPLEMENT_PATCH, TT_FIX_VALIDATION, TT_WRITE_TEST, TT_EXPLAIN_FAILURE]


@dataclass
class Snippet:
    file_path: str = ""
    start_line: int = 0
    end_line: int = 0
    content: str = ""
    language: str = ""
    relevance_score: float = 1.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ArtifactRef:
    artifact_id: str = ""
    artifact_type: str = ""
    description: str = ""
    content: str = ""
    source: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ValidationPlan:
    run_tests: bool = True
    expected_files: list[str] = field(default_factory=list)
    forbidden_changes: list[str] = field(default_factory=list)
    required_checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class TaskPacket:
    schema_version: str = TP_SCHEMA_VERSION
    task_packet_id: str = ""
    task_type: str = TT_IMPLEMENT_PATCH
    objective: str = ""
    allowed_files: list[str] = field(default_factory=list)
    forbidden_files: list[str] = field(default_factory=list)
    source_snippets: list[Snippet] = field(default_factory=list)
    relevant_artifacts: list[ArtifactRef] = field(default_factory=list)
    output_schema: dict | None = None
    constraints: list[str] = field(default_factory=list)
    validation_plan: ValidationPlan | None = None
    token_budget: int = 0
    token_used: int = 0
    governance_result: dict | None = None
    risk_assessment: dict | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def token_headroom(self) -> int:
        return max(0, self.token_budget - self.token_used)

    def is_within_budget(self) -> bool:
        return self.token_used <= self.token_budget


class TaskPacketBuilder:
    def __init__(self):
        self._packet = TaskPacket(task_packet_id=new_id("tp"))

    def with_task_type(self, task_type: str) -> TaskPacketBuilder:
        if task_type not in ALL_TASK_TYPES:
            self._packet.errors.append(f"Unknown task type: {task_type}")
        self._packet.task_type = task_type
        return self

    def with_objective(self, objective: str) -> TaskPacketBuilder:
        self._packet.objective = objective
        return self

    def with_allowed_files(self, files: list[str]) -> TaskPacketBuilder:
        self._packet.allowed_files = list(files)
        return self

    def with_forbidden_files(self, files: list[str]) -> TaskPacketBuilder:
        self._packet.forbidden_files = list(files)
        return self

    def with_source_snippets(self, snippets: list[Snippet]) -> TaskPacketBuilder:
        self._packet.source_snippets = list(snippets)
        return self

    def with_relevant_artifacts(self, artifacts: list[ArtifactRef]) -> TaskPacketBuilder:
        self._packet.relevant_artifacts = list(artifacts)
        return self

    def with_output_schema(self, schema: dict) -> TaskPacketBuilder:
        self._packet.output_schema = schema
        return self

    def with_constraints(self, constraints: list[str]) -> TaskPacketBuilder:
        self._packet.constraints = list(constraints)
        return self

    def with_validation_plan(self, plan: ValidationPlan) -> TaskPacketBuilder:
        self._packet.validation_plan = plan
        return self

    def with_token_budget(self, budget: int) -> TaskPacketBuilder:
        self._packet.token_budget = budget
        return self

    def with_token_used(self, used: int) -> TaskPacketBuilder:
        self._packet.token_used = used
        return self

    def with_governance_result(self, result: dict) -> TaskPacketBuilder:
        self._packet.governance_result = result
        return self

    def with_risk_assessment(self, assessment: dict) -> TaskPacketBuilder:
        self._packet.risk_assessment = assessment
        return self

    def build(self) -> TaskPacket:
        if not self._packet.task_packet_id:
            self._packet.task_packet_id = new_id("tp")
        if not self._packet.objective:
            self._packet.warnings.append("Task packet has no objective")
        return self._packet
