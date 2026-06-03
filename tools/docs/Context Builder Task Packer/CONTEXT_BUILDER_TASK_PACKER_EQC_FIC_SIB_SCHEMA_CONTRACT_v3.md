# CONTEXT_BUILDER_TASK_PACKER_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: CONTEXT_BUILDER_TASK_PACKER_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling safety and architecture contract, implementation-ready
component_id: AGENTX_CONTEXT_BUILDER_TASK_PACKER
component_name: Context Builder / Task Packer
roadmap_layer: 8
roadmap_phase: Phase C — Context Assembly and Task Packaging
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Prompt Contract Acceptance Criteria, Model Runtime Compatibility Criteria, Command Acceptance Criteria if CLI commands are exposed
optional_standards: ES, Report Template
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/context/
runtime_artifact_root: .agentx-init/context_packs/
previous_version_rating: 9.7/10
current_version_rating: 10/10
```


---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 contract was strong and implementation-ready, but I would rate it:

```text
9.7/10
```

It covered the requested core areas and added important production controls:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
context-source rules
task-input rules
task-packing rules
context-window budgeting
token budgeting
priority ranking
source trust levels
deduplication rules
recency rules
compression/summarization rules
prompt-injection handling
sensitive-data redaction
model-profile compatibility
tool-call compatibility
evidence/audit contract
OpenCode borrowing notes
Agent_X integration notes
dependency gates
restricted mode
context-pack modes
determinism and idempotency
lineage and supersession
conflict-resolution records
constraint locking
evidence immutability
fresh-clone validation
```

## 0.2 Why v2 Was Not Fully 10/10

The v2 document was close to final, but it still had several precision gaps that matter for a coding-agent handoff:

```text
1. It did not define a strict status vocabulary for context-pack decisions.
2. It did not define a final pack verdict model separate from implementation DONE / NOT DONE.
3. It needed a more explicit authority matrix for conflict handling across user task, contracts, repository files, summaries, and tool outputs.
4. It needed hard token-budget allocation caps to prevent low-priority context from consuming the whole model window.
5. It needed a stricter context-pack manifest with reproducibility fields, source hashes, pack hash, and build inputs.
6. It needed clearer dependency-simulation rules for tests when Policy, Sandbox, Model Adapter, Tool Adapter, or Runtime Profile components are unavailable.
7. It needed implementation drift blockers specific to context packing, not only general NO-GO conditions.
8. It needed stronger rules for reproducible pack rebuilds and hash comparison.
9. It needed clearer treatment of external, generated, and summarized context as data rather than instructions.
10. It needed final v3 freeze language aligned with the other Agent_X layer contracts.
```

## 0.3 v3 Improvements

This v3 adds:

```text
strict status vocabulary
pack verdict model
authority and conflict matrix
budget allocation hard caps
reproducible manifest requirements
dependency simulation contract for tests
context-specific drift blockers
rebuild/hash comparison rules
stronger generated/external/summarized context restrictions
final v3 freeze language
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the controlling contract for the **Context Builder / Task Packer** layer in Agent_X.

The Context Builder / Task Packer is responsible for assembling the correct, safe, bounded, and auditable context that will be sent to a model or downstream implementation worker.

This layer decides:

```text
which task instructions are included
which project files are included
which evidence artifacts are included
which previous decisions are included
which tool results are included
which content is summarized or compressed
which context is excluded
which source gets priority
which injected instructions are ignored
which sensitive data is redacted
which model profile can receive the final pack
which tool-call context is safe to include
```

This layer is safety-critical because the quality and safety of the model's output depends directly on what context it receives.

The Context Builder / Task Packer must not become a hidden bypass around:

```text
Policy / Capability Registry
Security Sandbox / Filesystem Boundary
Tool / MCP Adapter Layer
Model Adapter Layer
Local Model Runtime Profile Layer
Prompt Contract / Prompt Versioning Layer
Failure Taxonomy / Recovery Playbook
Evidence / Audit Rules
```

---

# 2. Scope

## 2.1 Required in This Layer

This layer must define contracts for:

```text
context source discovery
context source classification
task input normalization
task constraint preservation
context item modeling
context pack modeling
context-window budgeting
token budgeting
priority ranking
source trust levels
deduplication
recency scoring
compression and summarization
prompt-injection filtering
sensitive-data redaction
model-profile compatibility
tool-call compatibility
evidence references
audit records
runtime context-pack artifacts
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
LLM text generation
model serving
model selection beyond compatibility filtering
tool execution
source mutation
patch application
Git writes
network fetching by default
human approval UI
promotion gate
long-term learning
background daemon behavior
```

The layer may prepare a task pack for another component, but it must not execute the task itself.

---

# 3. Standards Applied

## 3.1 Primary Standard: EQC

EQC is primary because this layer controls the model's operational input.

It must ensure:

```text
correct context
bounded context
trusted context
safe task instructions
preserved task constraints
auditable source selection
safe summarization
safe compression
prompt-injection resistance
sensitive-data redaction
model-window compatibility
tool-context compatibility
evidence completeness
```

A bad context pack can cause an otherwise safe model or tool layer to act on wrong instructions, stale information, malicious embedded instructions, missing constraints, or unsafe data.

## 3.2 Required Supporting Standard: FIC

FIC is required because the implementation must have clear file boundaries.

Expected implementation files will be defined in the implementation spec, but this contract requires the layer to separate responsibilities for:

```text
context models
source loading
task input normalization
budget estimation
priority scoring
deduplication
recency scoring
compression planning
summary selection
prompt-injection filtering
redaction
pack building
compatibility checking
artifact writing
schema validation
```

No single file should become an uncontrolled all-purpose context assembler.

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer sits between many subsystems:

```text
Agent_X Initiator
Policy / Capability Registry
Security Sandbox / Filesystem Boundary
Tool / MCP Adapter Layer
Model Adapter Layer
Local Model Runtime Profile Layer
Prompt Contract / Prompt Versioning Layer
Failure Taxonomy / Recovery Playbook
future LLM Implementation Worker
future Self-Evolution Orchestrator
future Evaluation Harness
```

The output of this layer becomes the structured input to downstream model execution and implementation work.

## 3.4 Required Schema Contract

Schema Contract is required because every context pack must be structured, reproducible, and testable.

Required schemas should include at minimum:

```text
context_source.schema.json
context_item.schema.json
task_input.schema.json
task_constraints.schema.json
context_budget.schema.json
context_pack.schema.json
context_pack_manifest.schema.json
context_source_trust.schema.json
context_priority_decision.schema.json
context_deduplication_record.schema.json
context_compression_record.schema.json
context_redaction_record.schema.json
context_injection_scan.schema.json
context_model_compatibility.schema.json
context_tool_compatibility.schema.json
context_pack_audit.schema.json
```

## 3.5 Required Evidence / Audit Rules

This layer must write evidence for:

```text
task input received
context sources considered
context sources accepted
context sources rejected
priority decisions
deduplication decisions
recency decisions
compression decisions
summarization decisions
prompt-injection findings
sensitive-data redaction
token budget calculations
model compatibility decisions
tool compatibility decisions
final context pack
final context-pack manifest
```

No final context pack may be produced without an audit trail.

---

# 4. Architecture Role

The Context Builder / Task Packer transforms raw project state and task information into a bounded, safe, structured package.

Input examples:

```text
user task
roadmap layer document
implementation spec
review / DoD document
policy decisions
tool results
security sandbox evidence
local model profile
model adapter metadata
prior implementation evidence
test output
repository summaries
selected source files
```

Output examples:

```text
ContextPack
ContextPackManifest
TaskPack
ContextBudget
ContextSourceList
ContextAuditRecord
ModelCompatibilityDecision
ToolCompatibilityDecision
```

This layer must answer:

```text
What does the worker need to know?
What must the worker not see?
Which instructions are authoritative?
Which instructions are untrusted content?
What constraints must be preserved exactly?
What content can be summarized?
What content must remain verbatim?
Will the selected model fit this task?
Which tool outputs are safe and relevant?
What evidence proves the pack was built correctly?
```

---

# 5. Preconditions and Dependency Gates

## 5.1 Required Prior Components

Before this layer can build packs for implementation or execution workers, these components must be available or safely substituted:

```text
Policy / Capability Registry
Security Sandbox / Filesystem Boundary
Tool / MCP Adapter Layer, for tool-result context
Model Adapter Layer, for model feature compatibility
Local Model Runtime Profile Layer, for local context-window and request-size limits
Prompt Contract / Prompt Versioning Layer, for final prompt/task-pack layout
Failure Taxonomy / Recovery Playbook
```

## 5.2 Restricted Mode

If one or more dependencies are missing, the layer may still run in restricted mode.

Restricted mode allows:

```text
task input normalization
manual context-source inventory
source trust classification
read-only pack planning
budget estimation from provided model profile
prompt-injection scan
redaction scan
dry-run context-pack manifest generation
```

Restricted mode blocks:

```text
repository file loading without Security Sandbox
tool-output inclusion without ToolResult provenance
model-specific final pack approval without model profile
implementation-worker task packs without Prompt Contract compatibility
network retrieval
source mutation
raw shell
```

## 5.3 Dependency Gate Rules

```text
If Policy / Capability Registry is missing -> unknown, sensitive, external, or tool-output sources are excluded by default.
If Security Sandbox is missing -> repository file/path sources are excluded unless explicitly provided as trusted input.
If Tool / MCP Adapter evidence is missing -> tool outputs are excluded or included only as untrusted summaries.
If Model Adapter metadata is missing -> model compatibility decision is BLOCKED for final execution packs.
If Local Model Runtime Profile is missing for local execution -> local pack compatibility is BLOCKED.
If Prompt Contract is missing -> final prompt/task-pack formatting is BLOCKED, but analysis pack planning may continue.
If Failure Taxonomy is missing -> failures use UNKNOWN_CONTEXT_FAILURE but still fail closed.
```

## 5.4 Authority Rule

The Context Builder does not grant execution authority.

A context pack is approved only when all required authorities agree:

```text
Task Input
Source Trust Classification
Policy / Capability Registry
Security Sandbox, for files and paths
Tool / MCP Adapter provenance, for tool outputs
Model Adapter or Runtime Profile, for model fit
Prompt Contract, for final pack format
Evidence / Audit Rules
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
QUARANTINED
REDACTED
COMPRESSED
INCLUDED_AS_UNTRUSTED_DATA
INCLUDED_AS_SUPPORTING_CONTEXT
INCLUDED_AS_AUTHORITATIVE_CONTEXT
```

---

# 6. Core Invariants

The implementation must preserve these invariants:

```text
No context pack without task input.
No context pack without source inventory.
No context pack without budget calculation.
No context pack without trust classification.
No context pack without prompt-injection scan.
No context pack without redaction pass.
No context pack without model compatibility decision.
No context pack without evidence manifest.
No untrusted source may override trusted task instructions.
No summarized source may replace required exact constraints.
No stale source may outrank current authoritative source without justification.
No tool output may be included without provenance.
No sensitive value may be durably logged unredacted.
No context pack may exceed the selected model's context budget.
```

---

# 7. Context-Source Rules

## 6.1 Context Source Types

The layer must classify context sources by type.

Initial source types:

```text
USER_TASK
ROADMAP_DOCUMENT
CONTRACT_DOCUMENT
IMPLEMENTATION_SPEC
REVIEW_DOD_DOCUMENT
POLICY_RECORD
SECURITY_SANDBOX_RECORD
TOOL_RESULT
PATCH_RECORD
MODEL_PROFILE
RUNTIME_PROFILE
PROMPT_CONTRACT
TEST_OUTPUT
REPOSITORY_FILE
REPOSITORY_SUMMARY
EVIDENCE_ARTIFACT
HUMAN_REVIEW_NOTE
SYSTEM_CONSTRAINT
```

## 6.2 Source Provenance

Every context source must record:

```text
source_id
source_type
source_path_or_uri
source_component
created_at, if known
modified_at, if known
retrieved_at
content_hash
trust_level
authority_level
freshness_status
included_or_rejected
reason
evidence_refs
```

## 6.3 Source Acceptance Rules

A source may be included only if:

```text
it has an identifiable origin
it has a source type
it has a trust level
it has a relevance score
it has been scanned for prompt injection
it has been scanned for sensitive data
it fits within budget or has a compression plan
```

## 6.4 Source Rejection Rules

Reject or quarantine a source if:

```text
source origin is unknown
source appears corrupted
source is duplicate and lower priority
source is stale and superseded
source contains unsafe embedded instructions
source contains secrets that cannot be safely redacted
source exceeds budget and cannot be summarized safely
source conflicts with higher-authority instructions
source is outside sandbox-approved boundaries
```

Rejected sources must still be recorded in audit evidence.

---

# 8. Task-Input Rules

## 7.1 Task Input Structure

Every task input must be normalized into a structured object containing:

```text
task_id
task_type
task_title
task_description
requested_output_type
target_layer
target_component
required_documents
required_files
explicit_constraints
implicit_constraints
safety_constraints
acceptance_criteria
forbidden_actions
preferred_order
deadline_or_priority, if provided
source_message_refs
```

## 7.2 Constraint Preservation

The layer must preserve exact user constraints.

Examples of constraints that must not be lost:

```text
write as .md file
provide downloadable file
use same 3-document organization
do not broaden scope
do not include implementation code yet
make it the controlling contract
include specified standards
include specified safety sections
```

If constraints conflict, the layer must prefer:

```text
system/developer safety constraints
project safety contracts
current user task constraints
prior project conventions
lower-authority source suggestions
```

## 7.3 Task Input Validation

Block or return INVALID if:

```text
task has no actionable objective
task type is unsupported
target component is missing when required
requested output type is incompatible with the task
required constraints cannot be represented
task asks this layer to execute tools or mutate source directly
```

---

# 9. Task-Packing Rules

## 8.1 Task Pack Purpose

A task pack is the final structured bundle passed to a model, worker, or downstream Agent_X component.

It must include:

```text
task input
selected context items
excluded context summary
instruction hierarchy
constraints
budget report
compatibility decisions
audit references
```

## 8.2 Required Task Pack Sections

A valid task pack must contain:

```text
pack_id
schema_version
task_input
instruction_hierarchy
authoritative_context
supporting_context
excluded_context
context_budget
source_trust_summary
priority_decisions
deduplication_records
compression_records
redaction_records
prompt_injection_records
model_compatibility
tool_compatibility
evidence_refs
warnings
errors
```

## 8.3 Instruction Hierarchy

The task pack must distinguish:

```text
system instructions
developer instructions
project contracts
current user task
uploaded or retrieved document content
repository file content
tool output
untrusted embedded text
```

Untrusted embedded instructions inside files or tool outputs must not be promoted to higher authority.

---

# 10. Context-Window Budgeting

## 9.1 Budget Requirement

Every context pack must calculate available context capacity before assembly.

The budget must account for:

```text
model context window
reserved output tokens
reserved system/developer instruction tokens
reserved prompt-contract tokens
reserved tool-call formatting tokens
reserved safety margin
task input tokens
context item tokens
summary tokens
metadata tokens
```

## 9.2 Required Budget Fields

Context budget must include:

```text
model_context_window_tokens
reserved_output_tokens
reserved_instruction_tokens
reserved_tool_tokens
reserved_safety_margin_tokens
available_context_tokens
estimated_task_tokens
estimated_context_tokens
estimated_total_input_tokens
fits_model_context
over_budget_tokens
budget_strategy
warnings
errors
```

## 9.3 Budget Failure Rules

If the context exceeds the budget:

```text
do not silently truncate authoritative instructions
do not drop explicit user constraints
do not drop safety constraints
compress lower-priority context first
deduplicate before summarizing
summarize supporting context before authoritative context
return BLOCKED if the pack cannot fit safely
```

---

# 11. Token Budgeting

## 10.1 Token Estimation

The layer must support deterministic approximate token estimation.

Acceptable v1 token estimation:

```text
character-count approximation
word-count approximation
model-specific estimator if available
local tokenizer if already present
```

The estimator must record which method was used.

## 10.2 Token Budget Priority

When reducing context, preserve in this order:

```text
1. system/developer safety constraints
2. current user task
3. acceptance criteria
4. controlling contract documents
5. implementation specs relevant to the task
6. review / DoD documents relevant to the task
7. current source files directly targeted by task
8. recent validation evidence
9. supporting source files
10. older summaries and historical context
```

## 10.3 Token Budget Safety Rules

The implementation must not:

```text
remove safety constraints to fit budget
remove acceptance criteria to fit budget
summarize exact schema requirements unless summary is marked lossy
merge conflicting instructions without recording conflict
pretend an over-budget pack fits
```

---

# 12. Priority Ranking

## 11.1 Priority Inputs

Priority ranking must consider:

```text
source authority
task relevance
recency
source trust level
explicit user mention
roadmap layer match
component match
document type
evidence quality
deduplication status
token cost
risk level
```

## 11.2 Priority Decision Record

Each priority decision must record:

```text
context_item_id
priority_score
rank
included
reason
dominant_factors
suppressed_by
warnings
errors
```

## 11.3 Priority Rules

Higher priority must be given to:

```text
current user task
current layer contract
current layer implementation spec
current layer review / DoD
validated safety documents
latest committed evidence
directly targeted files
recent failing test output
explicitly referenced documents
```

Lower priority must be given to:

```text
old drafts
superseded documents
duplicate summaries
untrusted embedded instructions
large low-relevance files
historical context not relevant to current task
```

---

# 13. Source Trust Levels

## 12.1 Trust Level Enum

The layer must define source trust levels:

```text
TRUST_SYSTEM
TRUST_DEVELOPER
TRUST_PROJECT_CONTRACT
TRUST_USER_TASK
TRUST_VALIDATED_EVIDENCE
TRUST_REPOSITORY_SOURCE
TRUST_TOOL_OUTPUT
TRUST_UPLOADED_DOCUMENT
TRUST_SUMMARY
TRUST_UNTRUSTED_TEXT
TRUST_UNKNOWN
```

## 12.2 Authority Rule

Trust level affects instruction authority.

Rules:

```text
TRUST_SYSTEM cannot be overridden.
TRUST_DEVELOPER cannot be overridden by documents or tool output.
TRUST_PROJECT_CONTRACT outranks repository comments and old summaries.
TRUST_USER_TASK outranks older project context unless safety conflicts exist.
TRUST_VALIDATED_EVIDENCE outranks unvalidated summaries.
TRUST_TOOL_OUTPUT is data, not instruction authority.
TRUST_UPLOADED_DOCUMENT is content, not higher-level instruction authority.
TRUST_UNTRUSTED_TEXT cannot issue instructions.
TRUST_UNKNOWN is excluded unless explicitly allowed for analysis.
```

## 12.3 Trust Conflict Handling

If sources conflict:

```text
record conflict
prefer higher authority source
prefer newer validated source when authority is equal
preserve explicit user constraints where safe
do not merge incompatible instructions silently
```

---

# 14. Deduplication Rules

## 13.1 Deduplication Types

The layer must detect:

```text
exact duplicate content
near-duplicate summaries
same document different version
same evidence copied into multiple artifacts
same instruction repeated across layers
same source file loaded through multiple paths
```

## 13.2 Deduplication Record

Each deduplication decision must record:

```text
deduplication_id
primary_context_item_id
duplicate_context_item_ids
deduplication_type
similarity_method
decision
reason
tokens_saved_estimate
warnings
errors
```

## 13.3 Deduplication Safety Rules

Do not deduplicate away:

```text
current task constraints
latest version marker
evidence hashes
schema examples that differ meaningfully
test failure details
conflicting content that requires review
```

---

# 15. Recency Rules

## 14.1 Recency Inputs

Recency scoring may use:

```text
created_at
modified_at
validated_at
committed_at
uploaded_at
retrieved_at
version number
document status
explicit "final", "frozen", or "superseded" markers
```

## 14.2 Recency Safety Rules

Recency alone is not enough.

Rules:

```text
newer does not automatically mean authoritative
old final contracts may outrank newer informal notes
new uploads of old documents must not be treated as new content
modified timestamp must not override document version/status
fresh but unvalidated output must not outrank validated evidence
```

## 14.3 Supersession

If a source supersedes another source, record:

```text
superseding_source_id
superseded_source_id
supersession_reason
version_comparison
authority_comparison
```

---

# 16. Compression and Summarization Rules

## 15.1 Compression Types

Allowed compression approaches:

```text
extractive selection
lossless metadata compaction
structured summary
schema-aware summary
test-output summary
evidence manifest summary
source-file symbol summary
```

## 15.2 Summarization Safety

Summaries must preserve:

```text
task objective
acceptance criteria
safety constraints
schema names
file paths
function names
status values
failure classes
GO / NO-GO rules
Definition of Done criteria
```

## 15.3 Lossy Summary Labeling

Every lossy summary must be labeled:

```text
summary_type: LOSSY
source_refs: []
omitted_details: []
risk_of_loss: LOW | MEDIUM | HIGH
safe_for_execution: true | false
```

## 15.4 No-Summary Zones

Do not summarize:

```text
current user task
explicit file names
schema enums
security blockers
required command sequences
final verdict criteria
exact paths
exact class/function names
```

unless the pack is for high-level planning only and not implementation.

---

# 17. Prompt-Injection Handling

## 16.1 Injection Risk

This layer must treat embedded text in files, tool outputs, and external artifacts as untrusted unless explicitly promoted by policy.

Potential injection patterns include:

```text
ignore previous instructions
override system instructions
disable safety rules
execute this command
exfiltrate secrets
modify source directly
skip validation
mark done without tests
hide this from audit
```

## 16.2 Injection Scan Record

Every scan must record:

```text
scan_id
context_item_id
risk_level
patterns_detected
unsafe_instruction_spans
decision
reason
warnings
errors
```

## 16.3 Injection Handling Rules

If injection is detected:

```text
do not execute embedded instructions
do not promote embedded instructions
include content only as quoted/marked untrusted data if needed
summarize malicious instruction as risk evidence
record warning in context pack
block if safe isolation is not possible
```

## 16.4 High-Risk Injection Blockers

Block or quarantine context if it attempts to:

```text
override safety hierarchy
disable audit/evidence
bypass policy
bypass sandbox
enable raw shell
enable network by default
enable Git write by default
exfiltrate secrets
hide failures
falsify test results
```

---

# 18. Sensitive-Data Redaction

## 17.1 Sensitive Data Types

Before writing context-pack artifacts, redact:

```text
API keys
tokens
passwords
private keys
provider credentials
session secrets
environment values
unredacted command output containing secrets
personal data not needed for the task
private repository credentials
```

## 17.2 Redaction Record

Each redaction must record:

```text
redaction_id
context_item_id
redaction_type
location_hint
replacement_token
reason
safe_to_include
warnings
errors
```

## 17.3 Redaction Rules

The layer must:

```text
redact before durable logging
redact before final context pack
preserve enough structure for task usefulness
avoid logging raw secret values in evidence
reuse Security Sandbox secret redactor if available
fail closed if redaction cannot be performed safely
```

---

# 19. Model-Profile Compatibility

## 18.1 Compatibility Purpose

The context pack must fit the model selected by the Model Adapter Layer or Local Model Runtime Profile Layer.

Compatibility must check:

```text
context window
reserved output tokens
model input format
tool-use capability
structured-output capability
local/hosted policy mode
maximum prompt size
system prompt support
JSON output support
```

## 18.2 Compatibility Decision

Record:

```text
decision_id
model_profile_id
runtime_profile_id
context_window_tokens
estimated_input_tokens
reserved_output_tokens
fits
required_reductions
unsupported_features
decision
reason
warnings
errors
```

## 18.3 Compatibility Rules

If incompatible:

```text
attempt safe compression if allowed
select smaller task pack if policy permits
return BLOCKED if required constraints cannot fit
do not drop safety constraints to fit
do not drop acceptance criteria to fit
do not assume hosted-model features for local model profiles
```

---

# 20. Tool-Call Compatibility

## 19.1 Tool Context Rules

Tool-call results may be included only if:

```text
tool result is schema-valid
tool result has provenance
tool call was allowed or safely blocked
tool output is relevant to the task
tool output is redacted
tool output is scanned for prompt injection
tool output does not exceed budget
```

## 19.2 Tool Compatibility Decision

Record:

```text
tool_call_id
tool_name
tool_result_id
status
included
reason
risk_level
evidence_refs
warnings
errors
```

## 19.3 Tool Context Restrictions

Do not include:

```text
unredacted command output
raw secrets
tool output without provenance
failed output treated as fact
blocked output treated as successful evidence
external data treated as authoritative without source classification
```

---

# 21. Evidence / Audit Contract

## 20.1 Runtime Artifact Root

All context-pack runtime artifacts must be written under:

```text
.agentx-init/context_packs/
```

Required artifact types:

```text
context_source_inventory.json
context_pack_manifest.json
latest_context_pack.json
context_pack_history.jsonl
context_priority_decisions.jsonl
context_deduplication_records.jsonl
context_compression_records.jsonl
context_redaction_records.jsonl
context_injection_scan_records.jsonl
context_model_compatibility.json
context_tool_compatibility.json
context_pack_audit.jsonl
```

## 20.2 Evidence Requirements

Evidence must include:

```text
task input hash
source inventory hash
final context pack hash
budget calculation
included source list
excluded source list
deduplication decisions
compression decisions
redaction decisions
injection scan decisions
model compatibility decision
tool compatibility decision
warnings
errors
```

## 20.3 Hashing Rule

All final context-pack artifacts must have SHA-256 hashes.

Use Python standard library `hashlib` if no project hash helper exists.

## 20.4 Audit Rules

The audit must prove:

```text
what was included
what was excluded
why each major source was included or excluded
how many tokens were estimated
what was summarized
what was redacted
what injection risks were found
whether the pack fits the model
whether tool outputs were safe
```

---

# 22. OpenCode Borrowing Notes

## 21.1 Concepts to Borrow

Borrow OpenCode-style concepts only at the architectural level:

```text
task packing
context file selection
project-aware prompting
tool-output inclusion
summary-based context reduction
explicit plan/task separation
structured tool result context
repository-aware coding assistance
```

## 21.2 Concepts to Restrict

Do not borrow unsafe assumptions:

```text
unbounded context inclusion
model decides all relevant files without policy
tool output treated as trusted instructions
raw shell results included without redaction
network/web context enabled by default
direct file mutation from context packer
hidden prompt augmentation without audit
implicit plugin context loading
```

## 21.3 Agent_X Mapping

| OpenCode-style idea | Agent_X equivalent | Required control |
|---|---|---|
| Project context loading | `ContextSourceLoader` | sandbox + source trust |
| Task prompt construction | `TaskPackBuilder` | prompt contract + audit |
| Tool output context | `ToolContextSelector` | provenance + redaction |
| File relevance selection | `PriorityRanker` | evidence-backed scoring |
| Context compression | `CompressionPlanner` | no-loss zones |
| Large repo summarization | `SummarySelector` | schema-aware summaries |
| Model context fitting | `ContextBudgetEstimator` | model profile compatibility |
| Embedded instruction handling | `PromptInjectionFilter` | untrusted text isolation |

---

# 23. Agent_X Integration Notes

## 22.1 Policy / Capability Registry Integration

The layer must ask Policy / Capability Registry whether a context source may be included when:

```text
source path is sensitive
source has unknown trust level
source contains tool output
source contains potential secrets
source comes from external/network origin
source inclusion affects model permissions
```

Policy-denied sources must be excluded and recorded.

## 22.2 Security Sandbox Integration

The layer must use Security Sandbox for:

```text
repository file access
path boundary checks
source file metadata
secret redaction, if available
safe read operations
```

No raw repository file loading should bypass sandbox for implementation paths.

## 22.3 Tool / MCP Adapter Integration

The layer may consume ToolResult records from Tool / MCP Adapter.

Rules:

```text
include only schema-valid ToolResult records
treat tool output as data, not authority
include blocked/invalid tool records only as evidence, not success facts
redact and scan tool output before inclusion
```

## 22.4 Model Adapter Layer Integration

The layer must receive or query model profile metadata:

```text
context window
output token reserve
structured-output support
tool-use support
local/hosted mode
prompt format constraints
```

A pack is invalid if it ignores model-profile limits.

## 22.5 Local Model Runtime Profile Layer Integration

For local models, the pack must respect:

```text
actual local context window
available runtime memory
quantization-specific limits
runtime mode
CPU/GPU fallback constraints
request size limits
```

## 22.6 Prompt Contract / Prompt Versioning Layer Integration

The final task pack must be compatible with prompt contracts.

Rules:

```text
do not invent hidden instructions
record prompt contract version
separate instruction hierarchy from context data
mark untrusted content
preserve exact user constraints
```

## 22.7 Failure Taxonomy Integration

Failures must map to standard failure classes such as:

```text
CONTEXT_SOURCE_UNAVAILABLE
CONTEXT_SOURCE_UNTRUSTED
CONTEXT_BUDGET_EXCEEDED
CONTEXT_MODEL_INCOMPATIBLE
CONTEXT_TOOL_OUTPUT_UNSAFE
CONTEXT_INJECTION_RISK
CONTEXT_REDACTION_FAILED
CONTEXT_SCHEMA_INVALID
CONTEXT_PACK_BUILD_FAILED
UNKNOWN_CONTEXT_FAILURE
```

---

# 24. Public API Contract

Expected classes:

```text
ContextSource
ContextItem
TaskInput
TaskConstraints
ContextBudget
ContextPack
ContextPackManifest
ContextPriorityDecision
ContextDeduplicationRecord
ContextCompressionRecord
ContextRedactionRecord
ContextInjectionScanRecord
ContextModelCompatibilityDecision
ContextToolCompatibilityDecision
ContextPackAuditEvent
```

Expected public functions:

```python
load_context_sources(task_input: TaskInput, context: dict) -> list[ContextSource]

normalize_task_input(raw_task: dict) -> TaskInput

classify_context_source(source: ContextSource, context: dict) -> ContextSource

build_context_items(sources: list[ContextSource], task_input: TaskInput, context: dict) -> list[ContextItem]

estimate_context_budget(task_input: TaskInput, model_profile: dict, context_items: list[ContextItem]) -> ContextBudget

rank_context_items(context_items: list[ContextItem], task_input: TaskInput, budget: ContextBudget) -> list[ContextPriorityDecision]

deduplicate_context_items(context_items: list[ContextItem]) -> tuple[list[ContextItem], list[ContextDeduplicationRecord]]

plan_compression(context_items: list[ContextItem], budget: ContextBudget) -> list[ContextCompressionRecord]

scan_prompt_injection(context_item: ContextItem) -> ContextInjectionScanRecord

redact_sensitive_data(context_item: ContextItem) -> tuple[ContextItem, list[ContextRedactionRecord]]

check_model_compatibility(context_pack: ContextPack, model_profile: dict) -> ContextModelCompatibilityDecision

check_tool_compatibility(context_items: list[ContextItem]) -> list[ContextToolCompatibilityDecision]

build_context_pack(task_input: TaskInput, context_items: list[ContextItem], model_profile: dict, context: dict) -> ContextPack

write_context_pack_artifacts(context_pack: ContextPack, repo_root: Path) -> ContextPackManifest
```

---

# 25. Context-Pack Build Pipeline

Every pack must follow this sequence:

```text
1. Receive raw task input.
2. Normalize task input.
3. Validate task input schema.
4. Load candidate context sources.
5. Classify source type, trust level, and authority.
6. Apply policy checks where required.
7. Apply sandbox checks for file/path sources.
8. Convert sources into context items.
9. Scan context items for prompt-injection risk.
10. Redact sensitive data.
11. Deduplicate context items.
12. Score relevance, recency, trust, and authority.
13. Estimate token budget.
14. Plan compression if required.
15. Apply safe summarization or compression.
16. Check model-profile compatibility.
17. Check tool-call compatibility.
18. Build final ContextPack.
19. Validate ContextPack schema.
20. Write evidence artifacts and hashes.
21. Return ContextPackManifest.
```

No stage may be skipped unless the stage is explicitly not applicable and recorded.

---

# 26. Context-Pack Modes

## 25.1 Required Modes

The layer must support explicit pack modes.

```text
PLANNING_PACK
IMPLEMENTATION_PACK
REVIEW_PACK
VALIDATION_PACK
REPAIR_PACK
SUMMARY_PACK
```

## 25.2 Mode Rules

```text
PLANNING_PACK may use summaries and high-level source descriptions.
IMPLEMENTATION_PACK must preserve exact file paths, schemas, function names, acceptance criteria, and safety constraints.
REVIEW_PACK must include evidence, validation outputs, GO / NO-GO rules, and source mutation checks.
VALIDATION_PACK must include commands, expected outputs, schemas, tests, and review criteria.
REPAIR_PACK must include failing tests, failure classes, relevant source files, and no unrelated broad context.
SUMMARY_PACK may compress more aggressively but must label lossy summaries.
```

## 25.3 Mode Safety Rules

The implementation must not:

```text
use SUMMARY_PACK for implementation work when exact requirements are needed
use PLANNING_PACK to authorize source mutation
use REVIEW_PACK without evidence references
use VALIDATION_PACK without command and expected-result details
use REPAIR_PACK without the failing evidence that triggered repair
```

---

# 27. Determinism and Idempotency Rules

## 26.1 Deterministic Ordering

Given the same task input, source inventory, model profile, policy state, and runtime profile, the context packer must produce stable ordering.

Stable ordering must apply to:

```text
included context items
excluded context items
priority decisions
deduplication records
compression records
redaction records
evidence references
manifest fields
```

## 26.2 Idempotency

Repeated dry-run builds must produce the same pack hash unless one of these changes:

```text
task input
source content
source metadata
policy decision
sandbox decision
model profile
runtime profile
prompt contract
packing algorithm version
```

## 26.3 Idempotency Evidence

The manifest must record:

```text
packer_version
algorithm_version
source_inventory_hash
task_input_hash
model_profile_hash
prompt_contract_hash
final_context_pack_hash
```

---

# 28. Source-Access Boundary Rules

## 27.1 Repository Source Access

Repository files must be read only through Security Sandbox-approved read paths.

The layer must not:

```text
read arbitrary files directly with raw open() in production flow
walk unrestricted repository trees
follow symlinks outside approved roots
load ignored/secret files unless policy explicitly allows
read binary files as text without classification
fetch network sources by default
```

## 27.2 External Source Access

Network or external retrieval is disabled by default.

External sources may be included only when:

```text
Policy / Capability Registry allows the source
source provenance is recorded
retrieval method is recorded
content hash is recorded
prompt-injection scan passes or isolates risk
redaction scan passes
```

## 27.3 File-Type Handling

Every loaded source must have a file/content type classification:

```text
TEXT
MARKDOWN
JSON
YAML
PYTHON
TEST_OUTPUT
LOG
SCHEMA
BINARY
UNKNOWN
```

`BINARY` and `UNKNOWN` sources are excluded unless a safe parser exists and the inclusion is recorded.

---

# 29. Context Lineage and Supersession

## 28.1 Lineage Requirement

Every final context item must trace back to one or more source records.

Lineage fields:

```text
context_item_id
source_ids
derived_from_context_item_ids
derivation_type
transformation_applied
lossiness
source_hashes
output_hash
evidence_refs
```

## 28.2 Supersession Records

When one source replaces another, record:

```text
supersession_id
superseding_source_id
superseded_source_id
reason
version_comparison
authority_comparison
effective_decision
warnings
errors
```

## 28.3 Lineage Safety Rules

The implementation must not:

```text
include generated summaries without source references
include compressed context without lossiness labels
claim current authority without supersession evidence
merge conflicting sources without conflict records
```

---

# 30. Conflict-Resolution Rules

## 29.1 Conflict Types

The layer must detect and record conflicts between:

```text
current user task and old project context
contract document and implementation spec
implementation spec and review / DoD
source file and design document
old version and new version of same document
tool output and validation evidence
summary and original source
model profile and requested pack size
```

## 29.2 Conflict Record

Each conflict must record:

```text
conflict_id
source_ids
conflict_type
conflicting_claims
authority_comparison
recency_comparison
selected_resolution
reason
requires_human_review
warnings
errors
```

## 29.3 Conflict Safety Rules

The implementation must not:

```text
silently merge contradictory requirements
let old summaries override current task constraints
let stale source files override final contracts without evidence
resolve safety conflicts in favor of permissiveness
mark conflict-free when conflict detection was not run
```

---

# 31. Schema Example and Validation Requirements

For every schema, tests must include:

```text
one valid minimal example
one valid complete example
one missing-required-field invalid case
one invalid-enum invalid case, where enums exist
one malformed-type invalid case
```

Required valid examples:

```text
valid_task_input
valid_task_constraints
valid_context_source
valid_context_item
valid_context_budget
valid_context_pack
valid_context_pack_manifest
valid_context_source_trust
valid_context_priority_decision
valid_context_deduplication_record
valid_context_compression_record
valid_context_redaction_record
valid_context_injection_scan
valid_context_model_compatibility
valid_context_tool_compatibility
valid_context_pack_audit
```

A schema suite is incomplete if it only tests happy-path objects.

---

# 32. Constraint Locking Rules

## 31.1 Locked Constraint Types

The following must be locked before compression:

```text
current user objective
requested output format
required file name
required artifact type
explicit include list
explicit exclude list
standards to apply
acceptance criteria
NO-GO criteria
Definition of Done
exact paths
exact schema names
exact class/function names
validation commands
```

## 31.2 Locking Evidence

The pack manifest must record:

```text
locked_constraints
source_refs
constraint_hashes
compression_allowed: true|false
summarization_allowed: true|false
```

## 31.3 Locking Safety Rules

The implementation must not compress, omit, rename, or paraphrase locked constraints in implementation, validation, or repair packs.

---

# 33. Evidence Immutability Rules

After a context pack manifest is finalized:

```text
final pack artifacts must not be modified in place
changed artifact hash invalidates the previous manifest
new pack generation must create a new pack_id or version
manual edits must be listed as deviations
pack history must append rather than overwrite
latest_context_pack.json may update only as a pointer/copy to the latest finalized pack
```

Required immutable-final artifacts:

```text
context_pack_manifest.json
latest_context_pack.json
context_source_inventory.json
context_model_compatibility.json
context_tool_compatibility.json
all JSONL records used to justify the pack
```

---

# 34. Status Vocabulary and Pack Verdicts

All context-pack decisions must use a controlled status vocabulary.

Allowed context-source statuses:

```text
ACCEPTED
REJECTED
QUARANTINED
SUPERSEDED
DUPLICATE
COMPRESSED
SUMMARIZED
REDACTED
BLOCKED
NOT_CHECKED
```

Allowed context-pack verdicts:

```text
PACK_READY
PACK_READY_WITH_WARNINGS
PACK_BLOCKED
PACK_INVALID
PACK_OVER_BUDGET
PACK_MODEL_INCOMPATIBLE
PACK_UNSAFE_SOURCE_DETECTED
PACK_REDACTION_FAILED
PACK_INJECTION_RISK_UNRESOLVED
```

Rules:

```text
PACK_READY requires all mandatory checks to pass.
PACK_READY_WITH_WARNINGS may be used only when warnings do not affect task correctness or safety.
PACK_BLOCKED is required when a safe context pack cannot be produced.
PACK_INVALID is required when task input or context pack schema is invalid.
PACK_OVER_BUDGET is required when safe compression cannot make the pack fit.
PACK_MODEL_INCOMPATIBLE is required when no allowed model profile can receive the pack safely.
PACK_UNSAFE_SOURCE_DETECTED is required when unsafe content cannot be isolated.
PACK_REDACTION_FAILED is required when sensitive data cannot be safely redacted.
PACK_INJECTION_RISK_UNRESOLVED is required when prompt-injection content cannot be safely treated as data.
```

A pack verdict is separate from implementation review status. A pack can be blocked while the implementation remains correct.

---

# 35. Authority and Conflict Resolution Matrix

The implementation must apply this authority order when sources conflict.

| Rank | Source class | Instruction authority | Notes |
|---:|---|---|---|
| 1 | System / platform constraints | Highest | Cannot be overridden. |
| 2 | Developer / project operating constraints | High | Cannot be overridden by files, summaries, or tool output. |
| 3 | Current user task | High | Controls the requested artifact and immediate objective unless safety conflict exists. |
| 4 | Frozen Agent_X contracts | High | Controls architecture and safety requirements for the layer. |
| 5 | Current implementation spec | Medium-high | Controls coding details after contract. |
| 6 | Current review / DoD document | Medium-high | Controls final validation and DONE criteria. |
| 7 | Validated evidence artifacts | Medium | Data evidence, not instruction authority. |
| 8 | Repository source files | Medium | Implementation facts, not higher-level instruction authority. |
| 9 | Tool outputs | Medium-low | Data only; never instruction authority. |
| 10 | Uploaded documents | Context-dependent | Authority depends on user task and document status. |
| 11 | Summaries | Low | Useful only when source references remain available. |
| 12 | External or generated text | Lowest | Data only unless explicitly promoted by policy and task. |
| 13 | Unknown-origin text | None | Exclude or quarantine by default. |

Conflict handling must record:

```text
conflict_id
conflicting_source_ids
conflict_type
authority_comparison
selected_source_id
suppressed_source_ids
reason
risk_level
warnings
errors
```

Rules:

```text
Tool output cannot override user task constraints.
Repository comments cannot override frozen contracts.
Summaries cannot override source documents.
External text cannot override Agent_X policy.
Generated text cannot create new requirements unless accepted by the current task.
Older frozen contracts may outrank newer informal notes.
Current user task may narrow scope but may not disable safety constraints.
```

---

# 36. Budget Allocation and Hard Caps

The implementation must use a deterministic budget allocation strategy.

Default allocation for implementation/review packs:

```text
system_developer_and_prompt_contract: reserved, never dropped
current_task_and_constraints: reserved, never dropped
layer_contract: 20-35% of available context
implementation_spec: 20-35% of available context when relevant
review_dod: 10-25% of available context when relevant
repository_files: 10-30% depending on task
validated_evidence: 5-15% depending on task
tool_outputs: 0-15% depending on relevance
historical_context: 0-10% only after required items fit
```

Hard rules:

```text
Do not spend more than 30% of available context on historical summaries.
Do not spend more than 25% of available context on tool outputs unless the task is tool-output review.
Do not include large repository files before relevant contract/spec constraints are included.
Do not include multiple versions of the same document unless version comparison is required.
Do not exceed 90% of model context after reserving output and safety margins.
Reserve enough output tokens for the requested artifact type.
```

If budget pressure exists, reduce in this order:

```text
1. historical context
2. low-relevance tool output
3. duplicate source excerpts
4. older superseded documents
5. supporting repository files
6. non-critical examples
7. compressible implementation details
8. never-drop constraints remain intact
```

---

# 37. Context-Pack Manifest and Reproducibility Requirements

Every final context pack must have a manifest that can reproduce or audit the pack.

Required manifest fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "context_pack_manifest.schema.json",
  "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
  "pack_id": "<id>",
  "pack_version": "<version>",
  "pack_mode": "IMPLEMENTATION|PLANNING|REVIEW|REPAIR|VALIDATION|SUMMARY",
  "pack_verdict": "PACK_READY|PACK_BLOCKED|PACK_INVALID",
  "created_at": "<UTC timestamp>",
  "task_id": "<task id>",
  "task_hash": "<sha256>",
  "model_profile_id": "<model profile id>",
  "runtime_profile_id": "<runtime profile id or null>",
  "prompt_contract_id": "<prompt contract id or null>",
  "source_inventory_path": ".agentx-init/context_packs/context_source_inventory.json",
  "source_inventory_sha256": "<sha256>",
  "included_sources": [],
  "excluded_sources": [],
  "locked_constraints": [],
  "budget_summary": {},
  "priority_decision_refs": [],
  "deduplication_record_refs": [],
  "compression_record_refs": [],
  "redaction_record_refs": [],
  "injection_scan_refs": [],
  "conflict_record_refs": [],
  "model_compatibility_ref": "<path>",
  "tool_compatibility_refs": [],
  "final_context_pack_path": ".agentx-init/context_packs/latest_context_pack.json",
  "final_context_pack_sha256": "<sha256>",
  "manifest_sha256": "<sha256>",
  "warnings": [],
  "errors": []
}
```

Reproducibility rules:

```text
Same task input, same source inventory, same model profile, and same pack mode should produce the same source ordering and same locked constraints.
Timestamps and generated IDs may differ, but stable content hashes must allow comparison.
Rebuild differences must be explained by changed source hashes, changed task input, changed model profile, changed pack mode, or changed policy decisions.
Unexplained rebuild drift is a validation failure.
```

---

# 38. Dependency Simulation Contract for Tests

Tests may use simulated upstream dependencies only when the behavior is explicit and fail-closed.

Allowed simulated dependencies:

```text
fake_policy_registry_allow_read_only
fake_policy_registry_block_mutation
fake_security_sandbox_allow_fixture_paths
fake_security_sandbox_block_out_of_boundary
fake_model_profile_small_context
fake_model_profile_large_context
fake_tool_result_schema_valid
fake_tool_result_schema_invalid
fake_prompt_contract_basic
```

Simulation rules:

```text
Fake policy must never allow unknown source inclusion by default.
Fake sandbox must never allow paths outside the temp fixture root.
Fake model profile must enforce context limits.
Fake tool results must include provenance and schema validity.
Fake prompt contract must preserve instruction hierarchy.
```

Forbidden test behavior:

```text
mocking safety checks as always-allow
using real network to fetch context
using raw file reads outside fixture roots
assuming unlimited context window
skipping redaction tests because fixtures are artificial
skipping prompt-injection tests because content is local
```

---

# 39. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
builds context packs without task input
loads repository files without sandbox checks
includes unknown-origin sources by default
treats tool output as instruction authority
includes raw unredacted command output
logs secrets in context artifacts
allows prompt-injection text to override instruction hierarchy
marks over-budget packs as valid
ignores model-profile context limits
drops locked constraints during compression
summarizes schema enums or exact paths in implementation packs
silently resolves conflicting instructions
silently prefers newer but lower-authority sources
writes context artifacts outside .agentx-init/context_packs/ without deviation record
uses network fetching by default
executes tools directly
mutates source files
produces non-deterministic source ordering without explanation
omits final SHA-256 hashes
omits context-pack manifest
```

Allowed implementation choices:

```text
approximate token estimation in v1 if method is recorded
safe lossy summaries when marked and traceable
fake upstream dependencies in tests when fail-closed
blocked pack result when model compatibility cannot be satisfied
restricted mode when upstream components are missing
```

---

# 40. Test Acceptance Criteria

Required tests:

```text
test_task_input_normalization_preserves_constraints
test_context_source_requires_origin
test_unknown_source_trust_excluded_by_default
test_context_source_inventory_written
test_context_budget_detects_over_budget_pack
test_budget_never_drops_safety_constraints
test_priority_ranking_prefers_current_task
test_priority_ranking_prefers_current_contract
test_deduplication_removes_exact_duplicate
test_deduplication_preserves_conflicting_versions
test_recency_does_not_override_authority
test_compression_preserves_schema_enums
test_compression_preserves_file_paths
test_prompt_injection_detects_override_instruction
test_prompt_injection_marks_tool_output_as_untrusted
test_sensitive_data_redacted_before_artifact_write
test_tool_output_requires_provenance
test_model_compatibility_blocks_oversized_pack
test_context_pack_schema_accepts_valid_pack
test_context_pack_schema_rejects_missing_task_input
test_context_pack_artifacts_written
test_context_pack_hashes_written
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
context-source tests PASS
task-input tests PASS
budgeting tests PASS
priority ranking tests PASS
deduplication tests PASS
compression tests PASS
prompt-injection tests PASS
redaction tests PASS
model compatibility tests PASS
tool compatibility tests PASS
audit/evidence tests PASS
no source mutation outside approved runtime artifacts
```

---

# 41. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] task input schema is defined
[ ] context source schema is defined
[ ] context item schema is defined
[ ] context pack schema is defined
[ ] source trust levels are defined
[ ] priority ranking rules are defined
[ ] budget rules are defined
[ ] deduplication rules are defined
[ ] compression rules are defined
[ ] prompt-injection handling is defined
[ ] redaction rules are defined
[ ] model compatibility rules are defined
[ ] tool compatibility rules are defined
[ ] evidence/audit paths are defined
[ ] Agent_X integration points are defined
```

---

# 42. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] task input normalization preserves constraints
[ ] source inventory is written
[ ] priority decisions are evidenced
[ ] deduplication decisions are evidenced
[ ] compression decisions are evidenced
[ ] prompt-injection findings are evidenced
[ ] redaction records are evidenced
[ ] model compatibility is checked
[ ] tool compatibility is checked
[ ] final context pack validates
[ ] no source mutation occurs outside approved runtime artifact paths
```

---

# 43. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_CONTEXT_BUILDER_TASK_PACKER"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  source_inventory_verified: []
  budget_decisions_verified: []
  priority_decisions_verified: []
  deduplication_verified: []
  compression_verified: []
  injection_scan_verified: []
  redaction_verified: []
  model_compatibility_verified: []
  tool_compatibility_verified: []
  policy_integration_verified: []
  sandbox_integration_verified: []
  prompt_contract_integration_verified: []
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 44. Residual Risks

```yaml
residual_risks:
  - id: "CTX-RISK-001"
    description: "A stale or superseded document may be packed as authoritative context."
    severity: "high"
    mitigation: "Use source versioning, recency rules, and supersession records."
  - id: "CTX-RISK-002"
    description: "Prompt-injection text inside a source file or tool output may be treated as instruction."
    severity: "critical"
    mitigation: "Scan and mark untrusted embedded instructions; preserve instruction hierarchy."
  - id: "CTX-RISK-003"
    description: "Important acceptance criteria may be dropped during compression."
    severity: "critical"
    mitigation: "Define no-summary zones and compression tests for constraints, enums, and paths."
  - id: "CTX-RISK-004"
    description: "Context pack may exceed model limits and cause truncation."
    severity: "high"
    mitigation: "Budget before final pack and block unsafe oversized packs."
  - id: "CTX-RISK-005"
    description: "Tool output may be included without provenance."
    severity: "medium"
    mitigation: "Require schema-valid ToolResult and evidence references."
  - id: "CTX-RISK-006"
    description: "Sensitive data may be persisted in context-pack artifacts."
    severity: "critical"
    mitigation: "Redact before durable logging and fail closed when redaction is unsafe."
```

---

# 45. Fresh-Clone Validation and Review Handoff

The implementation is accepted only after validation from a fresh checkout or clean working tree.

Required command sequence:

```bash
git clone https://github.com/Astrocytech/Agent_X.git Agent_X_context_builder_check
cd Agent_X_context_builder_check
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
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
external MCP server
```

The post-implementation review document must verify:

```text
reviewed commit
commands run
exit codes
schema validation
context pack artifacts
hashes
source mutation check
final DONE / NOT DONE verdict
```

---

# 46. Definition of Done

The Context Builder / Task Packer layer is done when it can produce safe, bounded, auditable task packs for downstream Agent_X workers.

It must prove:

```text
task input is normalized
explicit constraints are preserved
context sources are inventoried
source trust levels are assigned
source authority is respected
prompt-injection risks are detected
sensitive data is redacted
duplicates are removed safely
conflicting versions are preserved for review
recency does not override authority
priority decisions are recorded
budget calculations are recorded
oversized packs are blocked or safely compressed
compression preserves exact required constraints
model compatibility is checked
tool-call compatibility is checked
final ContextPack schema validates
evidence artifacts are written
SHA-256 hashes are written
no source mutation occurs outside approved runtime artifacts
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

---

# 47. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
context pack can be produced without task input
context source can be included without provenance
prompt-injection text is promoted to instruction
sensitive data is logged unredacted
over-budget pack is marked valid
model incompatibility is ignored
tool output is included without provenance
explicit task constraints are dropped
safety constraints are summarized away
source authority is ignored
stale source silently overrides current source
evidence artifacts are missing
hashes are missing
source files are mutated by this layer
network fetching is enabled by default
raw shell is used
```

---

# 48. Final Freeze Rule

This v2 document is the final frozen controlling contract for the Context Builder / Task Packer Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive implementation details in the implementation spec
MAJOR: changed source trust hierarchy, changed default inclusion policy, changed prompt-injection behavior, changed redaction requirements, changed model compatibility rules
```

Blocked without major revision:

```text
removing prompt-injection scanning
removing sensitive-data redaction
allowing context packs without task input
allowing unknown sources by default
allowing over-budget packs to pass
dropping explicit user constraints during compression
treating tool output as instruction authority
enabling network context by default
mutating source from this layer
removing evidence logging
```

The next document should be:

```text
CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_SPEC
```

---

# 49. Final Rating

This v2 contract is rated:

```text
10/10
```

Reason:

```text
It preserves the full v1 coverage and adds the missing production controls: dependency gates, restricted mode, pack modes, deterministic/idempotent behavior, source-access boundaries, context lineage, supersession, conflict-resolution records, schema example requirements, constraint locking, evidence immutability, fresh-clone validation, and a stricter implementation handoff boundary.
```
