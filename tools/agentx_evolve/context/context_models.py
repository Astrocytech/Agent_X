from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

SOURCE_TRUST_SYSTEM = "SOURCE_TRUST_SYSTEM"
SOURCE_TRUST_AGENTX_CONTRACT = "SOURCE_TRUST_AGENTX_CONTRACT"
SOURCE_TRUST_VALIDATED_ARTIFACT = "SOURCE_TRUST_VALIDATED_ARTIFACT"
SOURCE_TRUST_USER_INPUT = "SOURCE_TRUST_USER_INPUT"
SOURCE_TRUST_TOOL_OUTPUT = "SOURCE_TRUST_TOOL_OUTPUT"
SOURCE_TRUST_UNTRUSTED_TEXT = "SOURCE_TRUST_UNTRUSTED_TEXT"
SOURCE_TRUST_BLOCKED = "SOURCE_TRUST_BLOCKED"

ITEM_KIND_TASK = "TASK"
ITEM_KIND_REQUIREMENT = "REQUIREMENT"
ITEM_KIND_CONSTRAINT = "CONSTRAINT"
ITEM_KIND_FILE_SNIPPET = "FILE_SNIPPET"
ITEM_KIND_SCHEMA = "SCHEMA"
ITEM_KIND_TEST_RESULT = "TEST_RESULT"
ITEM_KIND_TOOL_RESULT = "TOOL_RESULT"
ITEM_KIND_POLICY_DECISION = "POLICY_DECISION"
ITEM_KIND_MODEL_PROFILE = "MODEL_PROFILE"
ITEM_KIND_RUNTIME_PROFILE = "RUNTIME_PROFILE"
ITEM_KIND_PROMPT_CONTRACT = "PROMPT_CONTRACT"
ITEM_KIND_SUMMARY = "SUMMARY"
ITEM_KIND_EVIDENCE_REF = "EVIDENCE_REF"

INCLUDE = "INCLUDE"
EXCLUDE_DUPLICATE = "EXCLUDE_DUPLICATE"
EXCLUDE_LOW_PRIORITY = "EXCLUDE_LOW_PRIORITY"
EXCLUDE_OVER_BUDGET = "EXCLUDE_OVER_BUDGET"
EXCLUDE_POLICY_BLOCKED = "EXCLUDE_POLICY_BLOCKED"
EXCLUDE_INJECTION_RISK = "EXCLUDE_INJECTION_RISK"
EXCLUDE_SENSITIVE = "EXCLUDE_SENSITIVE"
SUMMARIZE = "SUMMARIZE"
REDACT_AND_INCLUDE = "REDACT_AND_INCLUDE"

COMPATIBLE = "COMPATIBLE"
INCOMPATIBLE_OVER_CONTEXT_WINDOW = "INCOMPATIBLE_OVER_CONTEXT_WINDOW"
INCOMPATIBLE_MODEL_POLICY = "INCOMPATIBLE_MODEL_POLICY"
INCOMPATIBLE_TOOL_POLICY = "INCOMPATIBLE_TOOL_POLICY"
INCOMPATIBLE_PROMPT_CONTRACT = "INCOMPATIBLE_PROMPT_CONTRACT"
NEEDS_COMPRESSION = "NEEDS_COMPRESSION"
NEEDS_REDACTION = "NEEDS_REDACTION"

TP_DRAFT = "DRAFT"
TP_READY = "READY"
TP_BLOCKED = "BLOCKED"
TP_INVALID = "INVALID"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{ts}"


def stable_hash(value: str | dict | list) -> str:
    if isinstance(value, dict):
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"))
    elif isinstance(value, list):
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"))
    else:
        raw = value
    return hashlib.sha256(raw.encode()).hexdigest()


def estimate_tokens_rough(text: str) -> int:
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(words, chars // 4)


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return dict(obj)


@dataclass
class ContextSource:
    schema_version: str = "1.0"
    schema_id: str = "context_source.schema.json"
    source_id: str = ""
    source_type: str = ""
    source_path: str | None = None
    source_component: str = ""
    source_trust_level: str = SOURCE_TRUST_UNTRUSTED_TEXT
    created_at: str | None = None
    modified_at: str | None = None
    loaded_at: str = ""
    allowed_by_policy: bool = False
    policy_decision_id: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class TaskInput:
    schema_version: str = "1.0"
    schema_id: str = "task_input.schema.json"
    task_input_id: str = ""
    created_at: str = ""
    source_component: str = "ContextBuilderTaskPacker"
    task_title: str = ""
    task_description: str = ""
    task_type: str = ""
    user_constraints: list[str] = field(default_factory=list)
    system_constraints: list[str] = field(default_factory=list)
    required_outputs: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    target_component_id: str | None = None
    target_files: list[str] = field(default_factory=list)
    requested_tools: list[str] = field(default_factory=list)
    requested_model_profile_id: str | None = None
    requested_runtime_profile_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ContextItem:
    schema_version: str = "1.0"
    schema_id: str = "context_item.schema.json"
    context_item_id: str = ""
    created_at: str = ""
    source_id: str = ""
    source_component: str = ""
    source_trust_level: str = SOURCE_TRUST_UNTRUSTED_TEXT
    item_kind: str = ""
    title: str = ""
    content: str = ""
    content_hash: str = ""
    token_estimate: int = 0
    priority_score: float = 0.0
    recency_score: float = 0.0
    dedupe_key: str = ""
    injection_risk_score: float = 0.0
    sensitive_data_score: float = 0.0
    inclusion_decision: str = INCLUDE
    redacted: bool = False
    summarized: bool = False
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ContextPack:
    schema_version: str = "1.0"
    schema_id: str = "context_pack.schema.json"
    context_pack_id: str = ""
    created_at: str = ""
    source_component: str = "ContextBuilderTaskPacker"
    task_input_id: str = ""
    model_profile_id: str | None = None
    runtime_profile_id: str | None = None
    max_context_tokens: int = 0
    reserved_output_tokens: int = 0
    available_input_tokens: int = 0
    total_estimated_tokens: int = 0
    included_items: list[ContextItem] = field(default_factory=list)
    excluded_items: list[ContextItem] = field(default_factory=list)
    summary_items: list[ContextItem] = field(default_factory=list)
    redaction_report_id: str | None = None
    compression_plan_id: str | None = None
    model_compatibility_id: str | None = None
    tool_compatibility_id: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class TaskPack:
    schema_version: str = "1.0"
    schema_id: str = "task_pack.schema.json"
    task_pack_id: str = ""
    created_at: str = ""
    source_component: str = "ContextBuilderTaskPacker"
    task_input: TaskInput | None = None
    context_pack: ContextPack | None = None
    prompt_contract_id: str | None = None
    model_profile_id: str | None = None
    runtime_profile_id: str | None = None
    status: str = TP_DRAFT
    failure_class: str | None = None
    allowed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    final_instructions: list[str] = field(default_factory=list)
    required_outputs: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Legacy TaskPacket types (absorbed from task_packet.py)
# ---------------------------------------------------------------------------

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
