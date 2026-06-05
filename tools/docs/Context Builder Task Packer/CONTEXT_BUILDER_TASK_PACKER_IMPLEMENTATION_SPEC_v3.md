# CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_SPEC

```text
document_id: CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_SPEC
version: v3.0
status: final frozen implementation-ready coding-agent handoff
component_id: AGENTX_CONTEXT_BUILDER_TASK_PACKER
component_name: Context Builder / Task Packer
roadmap_layer: 8
roadmap_phase: Phase C — Model Input Preparation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Prompt Contract Acceptance Criteria, Model Runtime Compatibility Criteria, Command Acceptance Criteria if CLI commands are exposed
optional_standards: ES, Report Template
target_language: Python
canonical_subdirectory: tools/agentx_evolve/context/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/context_packs/
implementation_mode: deterministic context assembly, task packing, budget enforcement, injection filtering, and compatibility checking
rating_target: 10/10
previous_version_rating: 9.8/10
current_version_rating: 10/10
```


---

# 0. v2 Review and Upgrade Summary

## 0.1 v1 Rating

The v1 implementation spec was rated:

```text
9.4/10
```

## 0.2 Why v1 Was Not Fully 10/10

The v1 document was strong and implementation-ready. It already covered the requested files, schemas, classes, functions, tests, implementation order, acceptance criteria, integrations, and Definition of Done.

It was not fully 10/10 because several production-control details were under-specified:

```text
1. It did not define strict dependency gates for missing Policy, Model Adapter, Runtime Profile, Tool Adapter, or Prompt Contract layers.
2. It did not define a clear context-authority order for resolving conflicts between system constraints, contracts, tool output, user text, and untrusted content.
3. It did not define exact source-to-item conversion rules for turning approved sources into ContextItem objects.
4. It did not define a deterministic final packing order.
5. It did not require a schema validation utility or schema example fixture set.
6. It did not require an evidence manifest with hashes for final context-pack artifacts.
7. It did not define stale-context and contradiction handling.
8. It did not define hard caps for budget failure, injection risk, sensitive data leakage, or compatibility failure.
9. It did not define implementation drift blockers as strongly as the previous Agent_X layer specs.
10. It did not include a final freeze rule to prevent broad uncontrolled scope expansion.
```

## 0.3 v2 Improvements

This v2 adds:

```text
dependency gates and restricted mode
context authority order
source-to-item conversion rules
deterministic final packing order
schema validation utility requirements
schema example fixture requirements
evidence manifest and hashing rules
stale-context and contradiction handling
hard fail-closed caps
implementation drift blockers
fresh-clone validation requirements
final freeze rule
```

Final v2 rating:

```text
10/10
```

## 0.4 v3 Review and Upgrade Summary

The v2 document was strong and very close to final. I would rate it:

```text
9.8/10
```

It was not fully 10/10 because a few implementation-handoff details still needed to be made explicit:

```text
1. Public function signatures for validation, source-to-item conversion, and final pack status were not fully defined.
2. The allowed import boundary was not explicit enough for a coding agent.
3. Draft vs final TaskPack semantics were implied but not formalized.
4. The pack validation pipeline did not explicitly require one validation function before artifact writing.
5. The evidence report fields did not fully mirror the stricter pattern used by previous Agent_X layers.
6. Runtime artifact immutability after final sign-off was not explicit.
7. The final implementation acceptance matrix needed a compact frozen checklist.
```

This v3 adds:

```text
explicit public API signatures
allowed and forbidden import boundaries
TaskPack status semantics
single validation gate before artifact writing
review/evidence report fields
artifact immutability rule
final frozen acceptance matrix
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document is the full implementation specification for the **Context Builder / Task Packer** layer.

It is the coding-agent handoff document for implementing a deterministic context assembly layer that prepares safe, bounded, auditable task packs for downstream model execution.

The Context Builder / Task Packer must decide:

```text
which task inputs are normalized
which context sources are allowed
which context items are included
which context items are excluded
which context items are summarized
which context items are redacted
which context items are blocked as unsafe
how context is prioritized
how token budget is estimated
how model context limits are enforced
how tool outputs are included safely
how final task packs are written as evidence
```

This layer must not become a bypass around:

```text
Policy / Capability Registry
Model Adapter Layer
Local Model Runtime Profile Layer
Tool / MCP Adapter Layer
Prompt Contract / Prompt Versioning Layer
Security Sandbox / Filesystem Boundary
Failure Taxonomy / Recovery Playbook
```

The output of this layer is a structured, schema-valid **TaskPack** that can be passed to a model worker or orchestrator later.

---

# 2. Canonical Subdirectory

Create the implementation here:

```text
tools/agentx_evolve/context/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/context_packs/
```

Expected package relationship:

```text
tools/agentx_evolve/context/       = new Context Builder / Task Packer layer
tools/agentx_evolve/policy/        = Policy / Capability Registry integration
tools/agentx_evolve/model_adapter/ = Model Adapter integration
tools/agentx_evolve/local_runtime/ = Local Model Runtime Profile integration
tools/agentx_evolve/tools/         = Tool / MCP Adapter integration
tools/agentx_evolve/prompts/       = Prompt Contract / Prompt Versioning integration
```

---

# 3. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic context builder that can:

```text
load approved context sources
normalize task input
create structured context items
score context priority
score context recency
deduplicate overlapping context items
estimate budget use
plan compression
select summaries
filter prompt-injection content
redact sensitive data
build bounded task packs
check model-context compatibility
check tool-context compatibility
write runtime evidence artifacts
validate all outputs against schemas
fail closed when safety or budget checks fail
```

The layer must not implement:

```text
LLM generation
model inference
tool execution
source mutation
patch creation
Git operations
network retrieval
human approval UI
prompt template authoring
long-term memory learning
```

---

# 4. Files to Create

## 4.1 Package Files

Create:

```text
tools/agentx_evolve/context/__init__.py
tools/agentx_evolve/context/context_models.py
tools/agentx_evolve/context/context_source_loader.py
tools/agentx_evolve/context/task_input_normalizer.py
tools/agentx_evolve/context/priority_scorer.py
tools/agentx_evolve/context/budget_estimator.py
tools/agentx_evolve/context/deduplication_engine.py
tools/agentx_evolve/context/recency_scorer.py
tools/agentx_evolve/context/compression_planner.py
tools/agentx_evolve/context/summary_selector.py
tools/agentx_evolve/context/prompt_injection_filter.py
tools/agentx_evolve/context/sensitive_data_redactor.py
tools/agentx_evolve/context/task_pack_builder.py
tools/agentx_evolve/context/model_context_compatibility.py
tools/agentx_evolve/context/tool_context_compatibility.py
tools/agentx_evolve/context/context_artifact_writer.py
```

## 4.2 Schema Files

Create:

```text
tools/agentx_evolve/schemas/context_source.schema.json
tools/agentx_evolve/schemas/task_input.schema.json
tools/agentx_evolve/schemas/context_item.schema.json
tools/agentx_evolve/schemas/context_pack.schema.json
tools/agentx_evolve/schemas/context_priority_score.schema.json
tools/agentx_evolve/schemas/context_budget_estimate.schema.json
tools/agentx_evolve/schemas/context_deduplication_report.schema.json
tools/agentx_evolve/schemas/context_compression_plan.schema.json
tools/agentx_evolve/schemas/context_redaction_report.schema.json
tools/agentx_evolve/schemas/context_injection_filter_report.schema.json
tools/agentx_evolve/schemas/task_pack.schema.json
tools/agentx_evolve/schemas/context_model_compatibility.schema.json
tools/agentx_evolve/schemas/context_tool_compatibility.schema.json
tools/agentx_evolve/schemas/context_pack_evidence.schema.json
```

## 4.3 Test Files

Create:

```text
tools/agentx_evolve/tests/test_context_source_loader.py
tools/agentx_evolve/tests/test_task_input_normalizer.py
tools/agentx_evolve/tests/test_context_models.py
tools/agentx_evolve/tests/test_priority_scorer.py
tools/agentx_evolve/tests/test_budget_estimator.py
tools/agentx_evolve/tests/test_deduplication_engine.py
tools/agentx_evolve/tests/test_recency_scorer.py
tools/agentx_evolve/tests/test_compression_planner.py
tools/agentx_evolve/tests/test_summary_selector.py
tools/agentx_evolve/tests/test_prompt_injection_filter.py
tools/agentx_evolve/tests/test_sensitive_data_redactor.py
tools/agentx_evolve/tests/test_task_pack_builder.py
tools/agentx_evolve/tests/test_model_context_compatibility.py
tools/agentx_evolve/tests/test_tool_context_compatibility.py
tools/agentx_evolve/tests/test_context_artifact_writer.py
tools/agentx_evolve/tests/test_context_negative_cases.py
tools/agentx_evolve/tests/test_context_schema_validation.py
```

## 4.4 Validation Utility Files

Create:

```text
tools/agentx_evolve/tests/validate_context_builder_schemas.py
```

If this script is not created, the same valid/invalid schema coverage must be proven by `test_context_schema_validation.py`.

---

# 5. Public Classes and Data Models

Implement all models in:

```text
tools/agentx_evolve/context/context_models.py
```

## 5.1 Required Constants

### Source Trust Levels

```python
SOURCE_TRUST_SYSTEM = "SOURCE_TRUST_SYSTEM"
SOURCE_TRUST_AGENTX_CONTRACT = "SOURCE_TRUST_AGENTX_CONTRACT"
SOURCE_TRUST_VALIDATED_ARTIFACT = "SOURCE_TRUST_VALIDATED_ARTIFACT"
SOURCE_TRUST_USER_INPUT = "SOURCE_TRUST_USER_INPUT"
SOURCE_TRUST_TOOL_OUTPUT = "SOURCE_TRUST_TOOL_OUTPUT"
SOURCE_TRUST_UNTRUSTED_TEXT = "SOURCE_TRUST_UNTRUSTED_TEXT"
SOURCE_TRUST_BLOCKED = "SOURCE_TRUST_BLOCKED"
```

### Context Item Kinds

```python
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
```

### Inclusion Decisions

```python
INCLUDE = "INCLUDE"
EXCLUDE_DUPLICATE = "EXCLUDE_DUPLICATE"
EXCLUDE_LOW_PRIORITY = "EXCLUDE_LOW_PRIORITY"
EXCLUDE_OVER_BUDGET = "EXCLUDE_OVER_BUDGET"
EXCLUDE_POLICY_BLOCKED = "EXCLUDE_POLICY_BLOCKED"
EXCLUDE_INJECTION_RISK = "EXCLUDE_INJECTION_RISK"
EXCLUDE_SENSITIVE = "EXCLUDE_SENSITIVE"
SUMMARIZE = "SUMMARIZE"
REDACT_AND_INCLUDE = "REDACT_AND_INCLUDE"
```

### Compatibility Decisions

```python
COMPATIBLE = "COMPATIBLE"
INCOMPATIBLE_OVER_CONTEXT_WINDOW = "INCOMPATIBLE_OVER_CONTEXT_WINDOW"
INCOMPATIBLE_MODEL_POLICY = "INCOMPATIBLE_MODEL_POLICY"
INCOMPATIBLE_TOOL_POLICY = "INCOMPATIBLE_TOOL_POLICY"
INCOMPATIBLE_PROMPT_CONTRACT = "INCOMPATIBLE_PROMPT_CONTRACT"
NEEDS_COMPRESSION = "NEEDS_COMPRESSION"
NEEDS_REDACTION = "NEEDS_REDACTION"
```

## 5.2 `ContextSource`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "context_source.schema.json"
source_id: str
source_type: str
source_path: str | None
source_component: str
source_trust_level: str
created_at: str | None
modified_at: str | None
loaded_at: str
allowed_by_policy: bool
policy_decision_id: str | None
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 5.3 `TaskInput`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "task_input.schema.json"
task_input_id: str
created_at: str
source_component: str = "ContextBuilderTaskPacker"
task_title: str
task_description: str
task_type: str
user_constraints: list[str]
system_constraints: list[str]
required_outputs: list[str]
forbidden_actions: list[str]
target_component_id: str | None
target_files: list[str]
requested_tools: list[str]
requested_model_profile_id: str | None
requested_runtime_profile_id: str | None
warnings: list[str]
errors: list[str]
```

## 5.4 `ContextItem`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "context_item.schema.json"
context_item_id: str
created_at: str
source_id: str
source_component: str
source_trust_level: str
item_kind: str
title: str
content: str
content_hash: str
token_estimate: int
priority_score: float
recency_score: float
dedupe_key: str
injection_risk_score: float
sensitive_data_score: float
inclusion_decision: str
redacted: bool
summarized: bool
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 5.5 `ContextPack`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "context_pack.schema.json"
context_pack_id: str
created_at: str
source_component: str = "ContextBuilderTaskPacker"
task_input_id: str
model_profile_id: str | None
runtime_profile_id: str | None
max_context_tokens: int
reserved_output_tokens: int
available_input_tokens: int
total_estimated_tokens: int
included_items: list[ContextItem]
excluded_items: list[ContextItem]
summary_items: list[ContextItem]
redaction_report_id: str | None
compression_plan_id: str | None
model_compatibility_id: str | None
tool_compatibility_id: str | None
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 5.6 `TaskPack`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "task_pack.schema.json"
task_pack_id: str
created_at: str
source_component: str = "ContextBuilderTaskPacker"
task_input: TaskInput
context_pack: ContextPack
prompt_contract_id: str | None
model_profile_id: str | None
runtime_profile_id: str | None
allowed_tools: list[str]
blocked_tools: list[str]
final_instructions: list[str]
required_outputs: list[str]
forbidden_actions: list[str]
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 5.7 Helper Functions

Implement:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
stable_hash(value: str | dict | list) -> str
estimate_tokens_rough(text: str) -> int
to_dict(obj: object) -> dict
```

Rules:

```text
stable_hash must use SHA-256.
estimate_tokens_rough must be deterministic and must not call a model.
to_dict must serialize nested dataclasses.
No helper may read or write files.
```

---

# 6. Schemas to Create

Each schema must:

```text
require schema_version
require schema_id
require warnings
require errors
define enum values where applicable
reject missing required fields
reject invalid enum values
allow evidence_refs and artifact_refs arrays where applicable
```

Required schemas:

```text
context_source.schema.json
task_input.schema.json
context_item.schema.json
context_pack.schema.json
context_priority_score.schema.json
context_budget_estimate.schema.json
context_deduplication_report.schema.json
context_compression_plan.schema.json
context_redaction_report.schema.json
context_injection_filter_report.schema.json
task_pack.schema.json
context_model_compatibility.schema.json
context_tool_compatibility.schema.json
context_pack_evidence.schema.json
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
```

---

# 7. File-by-File Implementation Spec

---

## 7.1 `__init__.py`

Purpose:

```text
Expose the public Context Builder / Task Packer API.
```

Required exports:

```python
from .context_models import (
    ContextSource,
    TaskInput,
    ContextItem,
    ContextPack,
    TaskPack,
)

from .context_source_loader import load_context_sources
from .task_input_normalizer import normalize_task_input
from .task_pack_builder import build_task_pack
from .model_context_compatibility import check_model_context_compatibility
from .tool_context_compatibility import check_tool_context_compatibility
from .context_artifact_writer import write_context_pack_artifacts
```

Must not do:

```text
no filesystem writes on import
no policy calls on import
no model calls on import
no tool calls on import
```

---

## 7.2 `context_source_loader.py`

Purpose:

```text
Load approved context source descriptors into ContextSource objects.
```

Required public function:

```python
load_context_sources(
    source_requests: list[dict],
    policy_context: dict,
    repo_root: Path | None = None
) -> list[ContextSource]
```

Required behavior:

```text
normalize source descriptors
check source trust level
check Policy / Capability Registry if available
block disallowed sources
do not read source contents directly unless source was already approved
attach policy_decision_id where available
return ContextSource objects with evidence refs
```

Must not do:

```text
no network fetch
no raw filesystem traversal outside approved paths
no source mutation
no model summarization
```

Acceptance tests:

```text
approved source descriptor loads
unknown source type blocks or warns
blocked source trust level excluded
missing policy blocks high-risk source
```

---

## 7.3 `task_input_normalizer.py`

Purpose:

```text
Convert raw task requests into a structured TaskInput object.
```

Required public function:

```python
normalize_task_input(raw_task: dict) -> TaskInput
```

Required behavior:

```text
require task_title or task_description
normalize constraints
normalize required outputs
normalize forbidden actions
normalize requested tools
normalize model/runtime profile IDs
preserve user constraints as constraints, not hidden instructions
mark suspicious embedded instructions as warnings
```

Acceptance tests:

```text
valid raw task normalizes
missing description fails or produces errors
forbidden actions preserved
requested tools normalized deterministically
```

---

## 7.4 `priority_scorer.py`

Purpose:

```text
Assign deterministic priority scores to context items.
```

Required public function:

```python
score_context_priority(
    item: ContextItem,
    task_input: TaskInput,
    scoring_context: dict
) -> ContextItem
```

Required scoring inputs:

```text
direct task relevance
source trust level
required output relevance
target file relevance
recent validation evidence
policy authority
prompt contract authority
user-provided task constraints
```

Required behavior:

```text
score between 0.0 and 1.0
system constraints outrank optional context
validated artifacts outrank untrusted text
untrusted text cannot override system or policy context
blocked sources score 0.0
```

Acceptance tests:

```text
system constraint scores high
blocked source scores zero
target file context scores above unrelated context
untrusted text cannot outrank controlling contract
```

---

## 7.5 `budget_estimator.py`

Purpose:

```text
Estimate context-token usage and enforce model budget limits.
```

Required public functions:

```python
estimate_context_item_budget(item: ContextItem) -> dict

estimate_context_pack_budget(
    items: list[ContextItem],
    max_context_tokens: int,
    reserved_output_tokens: int
) -> dict
```

Required behavior:

```text
use deterministic rough token estimate
reserve output tokens
calculate available input tokens
flag over-budget items
flag over-budget pack
never call model tokenizer unless explicitly available as optional local dependency
```

Acceptance tests:

```text
short item has lower estimate than long item
reserved output tokens reduce available input tokens
over-budget pack is flagged
budget estimate is deterministic
```

---

## 7.6 `deduplication_engine.py`

Purpose:

```text
Remove duplicate or near-duplicate context items before packing.
```

Required public function:

```python
deduplicate_context_items(
    items: list[ContextItem]
) -> dict
```

Required behavior:

```text
use content_hash for exact duplicates
use normalized title/content hash for simple near-duplicates
preserve highest-priority item among duplicates
record excluded duplicates
do not discard higher-trust source in favor of lower-trust duplicate
```

Acceptance tests:

```text
exact duplicate removed
higher-priority duplicate retained
higher-trust duplicate retained
deduplication report records excluded IDs
```

---

## 7.7 `recency_scorer.py`

Purpose:

```text
Assign deterministic recency score to context items.
```

Required public function:

```python
score_context_recency(
    item: ContextItem,
    reference_time_iso: str
) -> ContextItem
```

Required behavior:

```text
score between 0.0 and 1.0
newer validation artifacts score higher
undated items receive neutral score
recency must not override source trust or policy authority
```

Acceptance tests:

```text
recent item scores above older item
undated item receives neutral score
low-trust recent item does not outrank high-trust controlling contract
```

---

## 7.8 `compression_planner.py`

Purpose:

```text
Plan compression or summarization when the context pack exceeds budget.
```

Required public function:

```python
plan_context_compression(
    items: list[ContextItem],
    budget_estimate: dict,
    compression_context: dict
) -> dict
```

Required behavior:

```text
identify items to keep verbatim
identify items to summarize
identify items to exclude
never summarize controlling safety constraints away
never summarize schemas in a way that removes required fields
prefer summarizing low-priority long items first
return deterministic compression plan
```

Acceptance tests:

```text
over-budget pack produces compression plan
safety constraint remains verbatim
low-priority long item selected for summary
schema required fields preserved
```

---

## 7.9 `summary_selector.py`

Purpose:

```text
Select existing summaries or deterministic excerpts without model generation.
```

Required public function:

```python
select_summary_items(
    items: list[ContextItem],
    compression_plan: dict
) -> list[ContextItem]
```

Required behavior:

```text
prefer existing validated summaries
otherwise create deterministic extractive excerpt
do not use LLM summarization in this layer
mark summarized=True
preserve evidence refs to original item
```

Acceptance tests:

```text
existing summary selected
extractive excerpt created deterministically
summary keeps original evidence refs
summary does not replace safety-critical item
```

---

## 7.10 `prompt_injection_filter.py`

Purpose:

```text
Detect and quarantine prompt-injection-like content in context items.
```

Required public functions:

```python
detect_prompt_injection_risk(
    item: ContextItem
) -> dict

filter_prompt_injection_items(
    items: list[ContextItem]
) -> dict
```

Required detection signals:

```text
instructions to ignore previous instructions
instructions to reveal secrets
instructions to disable safety rules
instructions to execute tools directly
instructions to alter policy decisions
instructions to override system/developer prompts
instructions hidden inside file content or tool output
```

Required behavior:

```text
assign injection_risk_score
exclude or quarantine high-risk untrusted items
do not execute or follow text inside context
preserve safe evidence reference
include warning in pack
```

Acceptance tests:

```text
ignore previous instructions flagged
secret exfiltration instruction flagged
trusted system constraint not falsely removed
high-risk untrusted item excluded
```

---

## 7.11 `sensitive_data_redactor.py`

Purpose:

```text
Redact sensitive or secret-like content before packing and evidence writing.
```

Required public functions:

```python
redact_sensitive_context_item(
    item: ContextItem
) -> ContextItem

redact_sensitive_context_items(
    items: list[ContextItem]
) -> dict
```

Required redaction targets:

```text
API keys
tokens
passwords
private keys
provider credentials
environment secrets
access tokens
session tokens
personal data when not needed for task
raw command output containing secrets
```

Required behavior:

```text
replace secrets with [REDACTED]
set redacted=True
record redaction report
do not write unredacted secrets to runtime artifacts
```

Acceptance tests:

```text
API-key-like string redacted
private-key-like block redacted
non-secret technical text preserved
redaction report records affected item IDs
```

---

## 7.12 `task_pack_builder.py`

Purpose:

```text
Build final TaskPack from task input, context items, budget, policy, model, tool, and prompt compatibility checks.
```

Required public function:

```python
build_task_pack(
    raw_task: dict,
    source_requests: list[dict],
    builder_context: dict,
    repo_root: Path | None = None
) -> TaskPack
```

Required flow:

```text
1. Normalize raw task into TaskInput.
2. Load context sources.
3. Convert approved sources into ContextItems.
4. Filter prompt-injection risk.
5. Redact sensitive data.
6. Score priority.
7. Score recency.
8. Deduplicate items.
9. Estimate budget.
10. Plan compression if needed.
11. Select summaries if needed.
12. Check model-context compatibility.
13. Check tool-context compatibility.
14. Apply prompt contract constraints.
15. Build ContextPack.
16. Build TaskPack.
17. Validate schemas.
18. Write runtime artifacts.
19. Return TaskPack.
```

Required behavior:

```text
fail closed if policy blocks context
fail closed if model context window is exceeded after compression
fail closed if requested tools are not allowed
fail closed if prompt contract is incompatible
preserve evidence refs
never execute tools
never call models
never mutate source
```

Acceptance tests:

```text
valid task pack builds
over-budget pack compresses or blocks
policy-blocked context excluded
injection-risk context excluded
sensitive context redacted
requested blocked tool appears in blocked_tools
final TaskPack validates against schema
```

---

## 7.13 `model_context_compatibility.py`

Purpose:

```text
Check whether the context pack fits the selected model and runtime profile.
```

Required public function:

```python
check_model_context_compatibility(
    context_pack: ContextPack,
    model_profile: dict,
    runtime_profile: dict | None
) -> dict
```

Required checks:

```text
model context window
reserved output tokens
input token budget
model policy permissions
local vs hosted mode
runtime memory budget signal if available
max request size
required output format support
```

Required behavior:

```text
return COMPATIBLE only if all checks pass
return NEEDS_COMPRESSION if budget can be reduced
return INCOMPATIBLE_OVER_CONTEXT_WINDOW if still too large
return INCOMPATIBLE_MODEL_POLICY if model policy forbids task/context
attach evidence refs where available
```

Acceptance tests:

```text
compatible pack passes
over-window pack fails
reserved output budget enforced
model policy denial blocks
```

---

## 7.14 `tool_context_compatibility.py`

Purpose:

```text
Check whether requested tools are allowed and safe for the final task pack.
```

Required public function:

```python
check_tool_context_compatibility(
    task_input: TaskInput,
    context_pack: ContextPack,
    tool_registry: dict | None,
    policy_context: dict
) -> dict
```

Required checks:

```text
requested tool exists
requested tool is allowlisted
caller role may use tool
tool does not exceed task authority
tool is compatible with prompt contract
tool does not require missing governance
tool does not require missing human approval
tool does not require source mutation unless authorized
```

Required behavior:

```text
allowed tools listed
blocked tools listed with reasons
unknown tools blocked
mutating tools blocked unless explicitly authorized
MCP tools are least-privilege by default
```

Acceptance tests:

```text
known read-only tool allowed
unknown tool blocked
mutating tool blocked without governance
tool requiring approval blocked without approval ID
```

---

## 7.15 `context_artifact_writer.py`

Purpose:

```text
Write TaskPack, ContextPack, and related evidence artifacts.
```

Required public functions:

```python
write_context_pack_artifacts(
    task_pack: TaskPack,
    repo_root: Path
) -> dict

append_context_pack_history(
    task_pack: TaskPack,
    repo_root: Path
) -> dict

write_latest_context_pack(
    task_pack: TaskPack,
    repo_root: Path
) -> dict

write_context_pack_evidence(
    evidence_record: dict,
    repo_root: Path
) -> dict
```

Required paths:

```text
.agentx-init/context_packs/context_pack_history.jsonl
.agentx-init/context_packs/task_pack_history.jsonl
.agentx-init/context_packs/latest_context_pack.json
.agentx-init/context_packs/latest_task_pack.json
.agentx-init/context_packs/context_pack_evidence.json
.agentx-init/context_packs/context_builder_completion_record.json
```

Rules:

```text
append JSONL for history
write latest JSON atomically
write evidence with SHA-256 hashes
redact before durable writing
do not write unapproved files outside runtime artifact root
do not write source files
```

Acceptance tests:

```text
context pack history written
task pack history written
latest context pack written atomically
latest task pack written atomically
evidence includes hashes
unredacted secrets not persisted
```

---

# 8. Integration Requirements

## 8.1 Policy / Capability Registry Integration

Required:

```text
context source loading checks policy
requested tools checked against policy
model/task authority checked against policy
blocked sources are excluded
blocked tools are listed in blocked_tools
policy decision IDs included in evidence_refs where available
missing policy blocks high-risk sources, mutating tools, and untrusted context
```

Fail-closed rules:

```text
policy unavailable -> allow only low-risk read-only already-validated artifacts
policy unavailable -> block untrusted tool output
policy unavailable -> block source-write task packs
policy unavailable -> block requested mutating tools
```

## 8.2 Model Adapter Layer Integration

Required:

```text
consume model profile metadata
check model context window
check model supported input/output types
check model safety/task restrictions
check hosted vs local mode restrictions
return incompatibility instead of trimming silently
```

This layer must not call the model.

## 8.3 Local Model Runtime Profile Layer Integration

Required:

```text
consume runtime profile metadata
check max context window supported locally
check memory budget estimate where available
check quantization/profile limits where available
check request-size limit
block or compress when runtime cannot support pack
```

This layer must not start local model runtime.

## 8.4 Tool / MCP Adapter Layer Integration

Required:

```text
consume tool registry metadata
check requested tools against tool definitions
include tool outputs only as untrusted context unless validated
block or quarantine tool output with prompt-injection risk
include tool evidence refs when available
do not execute tools
```

## 8.5 Prompt Contract / Prompt Versioning Layer Integration

Required:

```text
consume prompt contract metadata
include required prompt sections
preserve non-overridable instructions
block packs that conflict with prompt contract
mark user-provided context as untrusted unless policy says otherwise
include prompt contract ID in TaskPack
```

This layer may assemble prompt-ready data, but the final prompt formatting belongs to the Prompt Contract / Prompt Versioning Layer unless that layer delegates it.

---

# 9. Runtime Artifact Rules

Runtime artifacts must be under:

```text
.agentx-init/context_packs/
```

Required artifacts:

```text
context_pack_history.jsonl
task_pack_history.jsonl
latest_context_pack.json
latest_task_pack.json
context_pack_evidence.json
context_builder_completion_record.json
```

Rules:

```text
append-only JSONL for history
atomic JSON writes for latest
SHA-256 hashes for final evidence artifacts
redact secrets before writing
do not write source files
do not write raw untrusted text if blocked for injection risk
do not persist unredacted sensitive data
```

---

# 10. Implementation Order

Implement in this exact order:

```text
1. tools/agentx_evolve/context/context_models.py
2. context schemas
3. task_input_normalizer.py
4. context_source_loader.py
5. prompt_injection_filter.py
6. sensitive_data_redactor.py
7. priority_scorer.py
8. recency_scorer.py
9. deduplication_engine.py
10. budget_estimator.py
11. compression_planner.py
12. summary_selector.py
13. model_context_compatibility.py
14. tool_context_compatibility.py
15. context_artifact_writer.py
16. task_pack_builder.py
17. tests
18. completion evidence
```

Rationale:

```text
models and schemas first
task normalization before source loading
safety filters before scoring and packing
redaction before durable writing
scoring before deduplication and budgeting
budgeting before compression
compatibility checks before final pack
artifact writer before final builder integration
tests after public surfaces exist
```

---

# 11. Minimal Implementation Slices

## 11.1 Slice A — Models and Schemas

Implement:

```text
context_models.py
all context/task schemas
test_context_models.py
test_context_schema_validation.py
```

Acceptance:

```text
dataclasses instantiate
schemas validate valid examples
schemas reject missing required fields
schemas reject invalid enum values
no filesystem writes
no model calls
no tool calls
```

## 11.2 Slice B — Task and Source Intake

Implement:

```text
task_input_normalizer.py
context_source_loader.py
```

Acceptance:

```text
raw task normalizes
source descriptors normalize
policy-blocked source excluded
source trust levels preserved
```

## 11.3 Slice C — Safety Filters

Implement:

```text
prompt_injection_filter.py
sensitive_data_redactor.py
```

Acceptance:

```text
prompt-injection text flagged
high-risk untrusted item excluded
secret-like values redacted
redaction report created
```

## 11.4 Slice D — Scoring, Deduplication, Budgeting

Implement:

```text
priority_scorer.py
recency_scorer.py
deduplication_engine.py
budget_estimator.py
compression_planner.py
summary_selector.py
```

Acceptance:

```text
priority scores deterministic
recency scores deterministic
duplicates removed safely
budget overrun detected
compression plan produced
summaries selected deterministically
```

## 11.5 Slice E — Compatibility and Builder

Implement:

```text
model_context_compatibility.py
tool_context_compatibility.py
task_pack_builder.py
```

Acceptance:

```text
model limits enforced
tool permissions enforced
prompt contract constraints preserved
TaskPack created and schema-valid
```

## 11.6 Slice F — Artifact Writer and Completion Evidence

Implement:

```text
context_artifact_writer.py
completion record writing
```

Acceptance:

```text
runtime artifacts written under .agentx-init/context_packs/
latest artifacts written atomically
history JSONL appended
SHA-256 hashes included
secrets are not persisted
```

---

# 12. Test Cases

Required tests:

```text
test_context_source_loader_approved_source_loads
test_context_source_loader_blocked_source_excluded
test_context_source_loader_missing_policy_blocks_high_risk_source
test_task_input_normalizer_valid_task
test_task_input_normalizer_missing_description_errors
test_task_input_normalizer_preserves_forbidden_actions
test_context_item_instantiates_and_serializes
test_context_pack_instantiates_and_serializes
test_task_pack_instantiates_and_serializes
test_priority_scorer_system_constraint_high
test_priority_scorer_blocked_source_zero
test_priority_scorer_untrusted_text_cannot_outrank_contract
test_budget_estimator_short_vs_long
test_budget_estimator_reserved_output_tokens
test_budget_estimator_over_budget_pack_flagged
test_deduplication_exact_duplicate_removed
test_deduplication_higher_trust_duplicate_retained
test_recency_scorer_recent_above_old
test_recency_scorer_undated_neutral
test_compression_planner_over_budget_plan_created
test_compression_planner_safety_constraint_verbatim
test_summary_selector_existing_summary_preferred
test_summary_selector_extractive_summary_deterministic
test_prompt_injection_filter_ignore_previous_instructions_flagged
test_prompt_injection_filter_secret_exfiltration_flagged
test_prompt_injection_filter_high_risk_untrusted_excluded
test_sensitive_data_redactor_api_key_redacted
test_sensitive_data_redactor_private_key_redacted
test_task_pack_builder_valid_pack_builds
test_task_pack_builder_over_budget_compresses_or_blocks
test_task_pack_builder_policy_blocked_context_excluded
test_task_pack_builder_injection_context_excluded
test_task_pack_builder_sensitive_context_redacted
test_task_pack_builder_blocked_tool_recorded
test_model_context_compatibility_compatible_pack_passes
test_model_context_compatibility_over_window_fails
test_model_context_compatibility_model_policy_denial_blocks
test_tool_context_compatibility_read_only_tool_allowed
test_tool_context_compatibility_unknown_tool_blocked
test_tool_context_compatibility_mutating_tool_without_governance_blocked
test_context_artifact_writer_history_written
test_context_artifact_writer_latest_written_atomically
test_context_artifact_writer_hashes_written
test_context_artifact_writer_unredacted_secret_not_persisted
```

Negative tests:

```text
test_context_builder_does_not_call_model
test_context_builder_does_not_execute_tools
test_context_builder_does_not_mutate_source
test_context_builder_does_not_fetch_network
test_prompt_injection_text_not_followed
test_blocked_context_not_persisted_as_included_item
test_untrusted_tool_output_cannot_override_policy
test_over_budget_pack_not_marked_compatible
test_missing_policy_does_not_allow_high_risk_context
test_unredacted_secret_never_written_to_latest_pack
```

---

# 13. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/context
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_context_*.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts under .agentx-init/context_packs/
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
running MCP server
running local model server
```

---

# 14. Acceptance Criteria

The layer may be accepted only if:

```text
canonical package exists
all required files exist
all required schemas exist
all required tests exist
compileall passes
pytest passes
schema validation passes
task input normalization works
context source loading respects policy
prompt-injection filtering works
sensitive-data redaction works
priority scoring is deterministic
recency scoring is deterministic
deduplication preserves higher-trust/higher-priority items
budget estimation is deterministic
compression planning preserves safety-critical content
summary selection is deterministic and non-LLM
model compatibility checks context limits
tool compatibility checks requested tools
TaskPack validates against schema
runtime artifacts are written only under .agentx-init/context_packs/
evidence includes hashes
no model is called
no tool is executed
no source mutation occurs
no network is used
secrets are not persisted
completion record exists
```

---

# 15. No-Go Criteria

The implementation is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
TaskPack is not schema-valid
context source loading bypasses policy
blocked context is included as trusted context
prompt-injection text is followed or treated as instruction
untrusted tool output can override policy/system/prompt contract
sensitive data is persisted unredacted
over-budget context pack is marked compatible
model is called by this layer
tool is executed by this layer
network is used by this layer
source files are modified
raw source traversal bypasses sandbox/policy
runtime artifacts are written outside .agentx-init/context_packs/ without deviation
final task pack lacks evidence refs
completion record is missing
```

---

# 16. Definition of Done

The Context Builder / Task Packer Layer is done when it can build safe, bounded, auditable task packs for downstream model execution.

It must prove:

```text
task input is normalized
context sources are policy-checked
context items are structured
priority is deterministic
recency is deterministic
duplicates are handled safely
token budget is estimated
over-budget packs are compressed or blocked
summaries are deterministic and non-LLM
prompt-injection risk is filtered
sensitive data is redacted
model context compatibility is checked
tool context compatibility is checked
prompt contract constraints are preserved
final TaskPack is schema-valid
runtime artifacts are written
evidence hashes are written
no model execution occurs
no tool execution occurs
no source mutation occurs
no network access occurs
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/context
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_context_*.py
git status --short
```

Expected proof:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

---

# 17. Completion Evidence Record

After validation, create:

```text
.agentx-init/context_packs/context_builder_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
  "component_name": "Context Builder / Task Packer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/context/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/context_packs/",
  "basis_documents": [
    "CONTEXT_BUILDER_TASK_PACKER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_SPEC"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "policy_integration_verified": [],
  "model_adapter_integration_verified": [],
  "local_runtime_profile_integration_verified": [],
  "tool_adapter_integration_verified": [],
  "prompt_contract_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_artifacts": [],
  "evidence_hashes": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

---

# 18. Coding-Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The canonical package is tools/agentx_evolve/context/.
[ ] Runtime artifacts are written only under .agentx-init/context_packs/.
[ ] This layer builds context and task packs only.
[ ] This layer does not call models.
[ ] This layer does not execute tools.
[ ] This layer does not mutate source.
[ ] This layer does not fetch from network.
[ ] Policy integration is fail-closed.
[ ] Tool output is treated as untrusted unless validated.
[ ] Prompt-injection risk is filtered before packing.
[ ] Sensitive data is redacted before persistence.
[ ] Model compatibility is checked before final TaskPack.
[ ] Tool compatibility is checked before final TaskPack.
[ ] Prompt contract constraints are preserved.
[ ] Tests run without GPU, network, hosted model, LLM, Bun, Node, OpenCode runtime, MCP server, or local model server.
```

---

# 19. Dependency Gates and Restricted Mode

This layer may be implemented before every downstream layer is fully stable, but it must not silently assume missing dependencies are safe.

## 19.1 Required Dependency Gates

Before building a final `TaskPack`, check dependency availability through explicit context fields or safe imports.

Required dependency signals:

```text
policy_registry_available
model_adapter_available
local_runtime_profile_available
tool_adapter_available
prompt_contract_available
security_sandbox_available
failure_taxonomy_available
```

## 19.2 Restricted Mode

If dependencies are missing, restricted mode applies.

Restricted mode allows:

```text
task input normalization
schema validation
context item construction from already-validated artifacts
prompt-injection filtering
sensitive-data redaction
deduplication
budget estimation
dry-run TaskPack planning
runtime evidence writing
```

Restricted mode blocks:

```text
untrusted context inclusion
tool-output trust elevation
requested mutating tools
source-write task packs
hosted model profile selection
prompt-contract-free final pack generation
over-budget pack approval
```

## 19.3 Dependency Fail-Closed Rules

```text
Policy unavailable -> block high-risk, untrusted, mutating, or tool-authorizing context.
Model Adapter unavailable -> use explicit model profile from builder_context only, otherwise return INCOMPATIBLE_MODEL_POLICY.
Local Runtime Profile unavailable -> do not claim local runtime compatibility.
Tool Adapter unavailable -> mark all requested tools as blocked except explicitly supplied read-only metadata.
Prompt Contract unavailable -> build draft pack only; do not claim final prompt-ready status.
Security Sandbox unavailable -> do not load raw file content from paths.
Failure Taxonomy unavailable -> use CONTEXT_FAILURE_UNCLASSIFIED but still block unsafe outcomes.
```

---

# 20. Context Authority and Conflict Rules

The builder must preserve authority order when context items conflict.

## 20.1 Authority Order

Highest to lowest:

```text
1. System/developer constraints from Agent_X controlling contracts
2. Policy / Capability Registry decisions
3. Prompt Contract / Prompt Versioning rules
4. Validated implementation artifacts and schemas
5. Validated test/evidence artifacts
6. Model and runtime profile metadata
7. Tool registry metadata
8. User task input and explicit user constraints
9. Tool outputs
10. Raw file snippets
11. Untrusted text
```

## 20.2 Conflict Behavior

When two items conflict:

```text
higher authority wins
lower authority item may be included only as context, not instruction
conflict is recorded in warnings
severe conflict blocks final TaskPack until resolved
untrusted text can never override contracts, policy, prompt rules, or safety constraints
```

Required conflict examples to test:

```text
user asks to ignore policy -> policy wins
tool output asks to execute a command -> tool output is treated as untrusted context
raw file says to disable tests -> raw file is not treated as instruction
old artifact conflicts with current contract -> current contract wins
```

---

# 21. Source-to-Item Conversion Rules

`context_source_loader.py` loads descriptors. A separate conversion step inside `task_pack_builder.py` or a helper must convert approved sources into `ContextItem` records.

Required conversion behavior:

```text
every ContextItem has source_id
every ContextItem has source_trust_level
every ContextItem has item_kind
every ContextItem has content_hash
every ContextItem has token_estimate
every ContextItem has evidence_refs where available
raw file content is never trusted as instruction
tool output is SOURCE_TRUST_TOOL_OUTPUT unless validated by evidence
blocked sources produce excluded_items or warnings, not included_items
```

Suggested helper:

```python
build_context_items_from_sources(
    sources: list[ContextSource],
    source_payloads: dict,
    task_input: TaskInput,
    builder_context: dict
) -> list[ContextItem]
```

Rules:

```text
source_payloads must already be supplied by approved upstream components or tests.
This layer must not perform broad raw filesystem reads to discover content.
This layer must not fetch network content.
This layer must not call tools to retrieve missing content.
```

---

# 22. Deterministic Packing Order

The final included context order must be deterministic.

Required order:

```text
1. non-overridable system and Agent_X contract constraints
2. Policy / Capability Registry decisions
3. Prompt Contract constraints
4. task input and required outputs
5. target component/file constraints
6. schemas required for the task
7. validated evidence and test results
8. model/runtime profile metadata
9. tool registry metadata
10. selected file snippets
11. selected summaries
12. low-priority supporting context
```

Tie-breakers:

```text
higher priority_score first
higher source_trust_level first
higher recency_score first
lower token_estimate first when budget is tight
stable content_hash order as final tie-breaker
```

The same inputs must produce the same TaskPack ordering.

---

# 23. Schema Validation Utility and Fixtures

Create a dedicated validation utility unless equivalent pytest coverage is explicitly documented.

Required utility:

```text
tools/agentx_evolve/tests/validate_context_builder_schemas.py
```

Required behavior:

```text
load every context-builder schema
validate at least one valid example for every schema
validate at least one missing-required-field failure for every schema
validate at least one invalid-enum failure for every enum schema
return exit code 0 only when all schema checks pass
```

Required example fixture names:

```text
valid_context_source
valid_task_input
valid_context_item
valid_context_pack
valid_context_priority_score
valid_context_budget_estimate
valid_context_deduplication_report
valid_context_compression_plan
valid_context_redaction_report
valid_context_injection_filter_report
valid_task_pack
valid_context_model_compatibility
valid_context_tool_compatibility
valid_context_pack_evidence
```

Manual validation command:

```bash
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_context_builder_schemas.py
```

---

# 24. Evidence Manifest and Hashing Rules

Create:

```text
.agentx-init/context_packs/context_builder_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "context_pack_evidence.schema.json",
  "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "runtime_artifact_root": ".agentx-init/context_packs/",
  "task_pack_id": "<task_pack_id>",
  "context_pack_id": "<context_pack_id>",
  "context_sources_used": [],
  "context_sources_excluded": [],
  "included_item_ids": [],
  "excluded_item_ids": [],
  "redacted_item_ids": [],
  "summarized_item_ids": [],
  "blocked_tool_names": [],
  "model_compatibility_status": "<status>",
  "tool_compatibility_status": "<status>",
  "prompt_contract_status": "<status>",
  "commands_run": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "deviation_register": [],
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final latest_task_pack, latest_context_pack, history artifacts used for review, evidence manifest, and completion record.
Use Python standard-library hashlib if no project helper exists.
```

A final DONE claim is invalid if evidence hashes are missing.

---

# 25. Stale Context, Contradictions, and Budget Hard Caps

## 25.1 Stale Context Rules

```text
current controlling contract outranks older summaries
newer validated evidence outranks older unvalidated notes
undated context receives neutral recency score
stale context can be included only if marked as historical/supporting
stale context cannot override current requirements
```

## 25.2 Contradiction Rules

```text
contradictions between equal-authority sources must be recorded
contradictions involving safety constraints block final TaskPack
contradictions involving optional implementation choices may be warnings
contradictions must not be silently resolved by low-trust or recency alone
```

## 25.3 Hard Caps and Blockers

The layer must fail closed if:

```text
final pack remains over model context window after compression
prompt-injection risk exceeds allowed threshold for included untrusted content
sensitive data remains unredacted in final pack
requested mutating tool is marked allowed without policy/governance
model compatibility is unknown but final pack claims COMPATIBLE
tool compatibility is unknown but final pack claims tools are allowed
prompt contract is missing but final pack claims prompt-ready status
runtime artifacts are written outside .agentx-init/context_packs/ without deviation
```

---

# 26. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places implementation files outside tools/agentx_evolve/context/ without recorded deviation
writes runtime artifacts outside .agentx-init/context_packs/ without recorded deviation
calls an LLM or model
starts a local model runtime
executes tools
fetches from network
mutates source files
uses raw shell
loads arbitrary files without sandbox/policy approval
treats tool output as trusted instructions
treats raw file text as trusted instructions
lets untrusted text override policy, prompt contract, or system constraints
marks over-budget packs as compatible
persists unredacted secrets
omits schema validation
omits evidence writing
omits evidence hashes
returns unstructured task packs
```

Allowed implementation choices:

```text
use deterministic rough token estimation
use extractive summaries only
use restrictive fallback when integrations are missing
mark final pack as draft when prompt contract is unavailable
block requested tools when tool registry is unavailable
block model compatibility when model profile is unavailable
```

---

# 27. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve/context
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_context_*.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_context_builder_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected runtime artifacts only
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final git status: clean or only expected runtime artifacts under .agentx-init/context_packs/
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
running MCP server
running local model server
```

---

# 28. Public API Boundary

The implementation must expose a small deterministic public API. Other packages must call these functions instead of directly calling internal scoring/filtering modules.

## 28.1 Required Public Functions

Expose these from `tools/agentx_evolve/context/__init__.py`:

```python
normalize_task_input(raw_task: dict) -> TaskInput

load_context_sources(
    source_requests: list[dict],
    policy_context: dict,
    repo_root: Path | None = None
) -> list[ContextSource]

build_context_items_from_sources(
    sources: list[ContextSource],
    source_payloads: dict,
    task_input: TaskInput,
    builder_context: dict
) -> list[ContextItem]

validate_context_pack(
    context_pack: ContextPack,
    validation_context: dict
) -> dict

validate_task_pack(
    task_pack: TaskPack,
    validation_context: dict
) -> dict

build_task_pack(
    raw_task: dict,
    source_requests: list[dict],
    builder_context: dict,
    repo_root: Path | None = None
) -> TaskPack

write_context_pack_artifacts(
    task_pack: TaskPack,
    repo_root: Path
) -> dict
```

## 28.2 Required Internal Functions

Internal modules may expose their own functions for tests, but external packages must not bypass:

```text
task input normalization
policy-gated source loading
source-to-item conversion
prompt-injection filtering
sensitive-data redaction
budget estimation
model compatibility check
tool compatibility check
TaskPack validation
artifact redaction/hashing
```

## 28.3 Required Validation Gate

Before writing any final artifact, the builder must call:

```python
validate_task_pack(
    task_pack: TaskPack,
    validation_context: dict
) -> dict
```

The validation result must include:

```text
status: PASS | FAIL
schema_valid: true | false
budget_valid: true | false
model_compatible: true | false
tool_compatible: true | false
prompt_contract_compatible: true | false
injection_risk_accepted: true | false
redaction_complete: true | false
evidence_refs_present: true | false
errors: []
warnings: []
```

If validation status is `FAIL`, the artifact writer may write a blocked/draft evidence artifact, but it must not write `latest_task_pack.json` as a final accepted pack.

---

# 29. Import and Dependency Boundary

## 29.1 Allowed Standard-Library Imports

Allowed:

```text
dataclasses
typing
pathlib
json
hashlib
datetime
uuid
re
copy
tempfile
os, only for safe path metadata when needed
```

## 29.2 Allowed Agent_X Imports

Allowed:

```text
agentx_evolve.policy, only through stable policy-check wrapper when available
agentx_evolve.model_adapter, only for model profile metadata
agentx_evolve.local_runtime, only for runtime profile metadata
agentx_evolve.tools, only for tool registry metadata, not execution
agentx_evolve.prompts, only for prompt contract metadata
agentx_evolve.security, only for approved source/path checks if raw paths are used
agentx_evolve.failures, only for failure-class constants if available
```

## 29.3 Forbidden Imports and Runtime Behavior

Forbidden:

```text
LLM/model clients
token-generating model APIs
tool execution dispatcher calls
network clients
subprocess
shell helpers
Git helpers
MCP runtime/server
OpenCode runtime
Bun
Node
browser automation
background scheduler
```

If a coding agent needs any forbidden dependency to make a test pass, the implementation is drifting and must be revised.

---

# 30. TaskPack Status Semantics

`TaskPack` must include or derive a final status.

Required status values:

```text
DRAFT
READY
BLOCKED
INVALID
```

Status meanings:

```text
DRAFT:
  Pack is structurally useful but cannot be treated as final prompt/model input yet.

READY:
  Pack is schema-valid, within budget, compatible with model/runtime/tool/prompt constraints, redacted, injection-filtered, and evidenced.

BLOCKED:
  Pack could not be made safe or compatible.

INVALID:
  Raw task input or required structure was invalid.
```

Required rules:

```text
missing prompt contract -> DRAFT or BLOCKED, not READY
unknown model compatibility -> DRAFT or BLOCKED, not READY
unknown tool compatibility -> DRAFT or BLOCKED, not READY
over-budget after compression -> BLOCKED
unredacted sensitive data -> BLOCKED
high-risk injection included -> BLOCKED
schema invalid -> INVALID
```

If the existing `TaskPack` dataclass does not include `status`, add:

```python
status: str
failure_class: str | None
```

The `task_pack.schema.json` must validate these fields.

---

# 31. Review Report and Evidence Fields

In addition to the evidence manifest, create a review-ready report artifact after validation:

```text
.agentx-init/context_packs/context_builder_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "context_builder_review_report.schema.json",
  "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "commands_run": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve/context",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "coverage_statuses": {
    "task_input_normalization": "PASS",
    "context_source_loading": "PASS",
    "prompt_injection_filtering": "PASS",
    "sensitive_data_redaction": "PASS",
    "budget_estimation": "PASS",
    "deduplication": "PASS",
    "compression": "PASS",
    "model_compatibility": "PASS",
    "tool_compatibility": "PASS",
    "artifact_writing": "PASS",
    "negative_tests": "PASS"
  },
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/context_packs/context_builder_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/context_packs/context_builder_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

Add schema:

```text
tools/agentx_evolve/schemas/context_builder_review_report.schema.json
```

Add test coverage:

```text
test_context_builder_review_report_schema_accepts_valid_report
test_context_builder_review_report_schema_rejects_missing_commit
test_context_builder_review_report_schema_rejects_missing_exit_code
```

A DONE claim is invalid without this report.

---

# 32. Runtime Artifact Immutability Rule

After a final `READY` TaskPack or final `DONE` completion record is written:

```text
final evidence files must not be modified in place
changed hashes invalidate the previous DONE verdict
new validation evidence must create a new timestamped evidence record
manual edits after sign-off must be recorded as deviations
latest_task_pack.json may be replaced only by a new validation run
history JSONL must remain append-only
```

Required tests:

```text
test_context_artifact_writer_history_append_only
test_context_artifact_writer_latest_replaced_only_after_validation
test_context_artifact_writer_hash_changes_detected
```

---

# 33. Final Frozen Acceptance Matrix

| Area | Required result |
|---|---|
| Package path | `tools/agentx_evolve/context/` exists |
| Schemas | all required context schemas exist and validate |
| Public API | required public functions exported |
| Task input | raw task normalized deterministically |
| Sources | source requests policy-checked |
| Context items | source-to-item conversion records trust, hash, tokens, evidence |
| Authority | context conflict rules follow authority order |
| Safety filters | injection-risk and sensitive data handled before packing |
| Scoring | priority and recency deterministic |
| Deduplication | higher-trust / higher-priority item preserved |
| Budget | over-budget packs compressed or blocked |
| Summaries | deterministic extractive or existing summaries only |
| Model compatibility | context window and policy checked |
| Runtime compatibility | local runtime limits checked when available |
| Tool compatibility | requested tools allowed/blocked with reasons |
| Prompt contract | missing/incompatible prompt contract prevents READY status |
| Validation gate | TaskPack validation runs before final artifact write |
| Evidence | manifest, review report, completion record, hashes written |
| Negative tests | model/tool/network/source-mutation bypasses fail |
| Source mutation | no source files modified |
| Final status | only safe, compatible, evidenced packs can be READY |

Any failed required area prevents final `DONE`.


---

# 34. Final Freeze Rule

This v3 implementation spec is frozen as the coding-agent handoff for the Context Builder / Task Packer layer.

Allowed future changes:

```text
PATCH: typo fixes, wording clarifications, examples
MINOR: additive optional tests or optional helper functions that do not change safety behavior
MAJOR: changed context authority order, changed allowed dependency behavior, changed budget safety behavior, changed final TaskPack schema, changed model/tool compatibility policy
```

Blocked without major revision:

```text
allowing model calls in this layer
allowing tool execution in this layer
allowing network fetch in this layer
allowing source mutation in this layer
removing prompt-injection filtering
removing sensitive-data redaction
removing policy fail-closed behavior
removing model compatibility checks
removing tool compatibility checks
removing evidence hashes
treating untrusted text as executable instruction
```

---

# 35. Final Rating

This v3 implementation spec is rated:

```text
10/10
```

Reason:

```text
It preserves the v2 production-control requirements and fixes the remaining implementation-handoff gaps: explicit public APIs, import boundaries, TaskPack status semantics, a required validation gate, stricter evidence/report fields, runtime artifact immutability, and a final frozen acceptance matrix.
```
