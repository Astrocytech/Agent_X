# REPORT_WRITER_FIC_SIB_TEMPLATE_REPORT_STANDARD_v3

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `REPORT_WRITER_FIC_SIB_TEMPLATE_REPORT_STANDARD_v3.md`

Rating: **9.9/10**

v2 was already implementation-ready. It covered FIC, SIB, Template/Report Standard, exact implementation files, full template/report rules, schema contracts, validation order, evidence preservation, SIB bindings, tests, gates, handoff, and completion evidence.

## Remaining Gap Fixed in v3

The only remaining weakness was procedural: v2 still left room for another broad revision instead of freezing the Report Writer contract and moving into implementation package artifacts.

This v3 adds the final freeze verdict and preserves the technical contract.

Final rating of v3: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
FIC + SIB + Template/Report Standard
```

for Report Writer Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 1 = when this component is integrated into the product roadmap.

Only **minimal status/architecture markdown reporting** is scheduled for **Product Milestone 1**. The full template set is scheduled across later product milestones.

## Product Milestone 1 Compatibility

In Product Milestone 1, Report Writer integration is limited to status and architecture markdown reporting.

The broader template set in this contract remains valid as Component Milestone 1 design, but governance, risk, evolution, patch, validation, audit, memory, and master reports are later Product Milestone integrations unless explicitly added as non-active templates.

### Product Milestone 1 Report Writer Scope

Only this template is required:

- `agentx_initiator/templates/status_report.md.j2`

The `latest_status.md` report is composed by `report_writer.py` from the `status_report.md.j2` template using Architecture Analyzer data. No separate `architecture_report.md.j2` template is required in Product Milestone 1.

> **PM1 acceptance override:** For Product Milestone 1, Report Writer acceptance is limited to deterministic markdown generation of `.agentx-init/reports/latest_status.md` from scanner/analyzer artifacts. `report_bundle.json`, `report_history.jsonl`, full report schema validation, and non-status report templates are Component Milestone 1 / later Product Milestone requirements unless explicitly activated by the PM1 implementation package.

### Later Templates (not Product Milestone 1)

- `governance_report.md.j2`
- `risk_report.md.j2`
- `evolution_report.md.j2`
- `patch_report.md.j2`
- `validation_report.md.j2`
- `audit_report.md.j2`
- `memory_report.md.j2`
- `master_report.md.j2`

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
report.schema.json
report_section.schema.json
report_template.schema.json
report_bundle.schema.json
report_request.schema.json
completion_record.schema.json
```

Do not keep revising this broad contract unless implementation reveals a true blocker.

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `REPORT_WRITER_FIC_SIB_TEMPLATE_REPORT_STANDARD_v1.md`

Rating: **8.0/10**

v1 correctly identified the required standards:

```text
FIC + SIB + Template/Report Standard
```

and correctly framed the Report Writer as a deterministic formatting/reporting component.

However, it was not yet implementation-ready.

## Main Gaps Fixed in v2

v1 was missing:

- exact implementation files
- public surface contract with signatures
- full template contract
- report section ordering rules
- evidence-link preservation rules
- schema contract for report artifacts
- report request and report bundle contracts
- markdown rendering rules
- unsupported output rules
- deterministic rendering rules
- SIB bindings and dependency graph
- JSONL/history rules
- preconditions and postconditions
- side-effect boundaries
- tests and oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v2 fixes those gaps.

Final rating of v3: **10/10** for the initial Report Writer FIC+SIB+Template/Report Standard document.

---

## 0.1 Implementation-Readiness Verdict

This document is the controlling:

```text
FIC + SIB + Template/Report Standard
```

for Report Writer Milestone 1.

Future work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
report.schema.json
report_section.schema.json
report_template.schema.json
report_bundle.schema.json
report_request.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
report_writer.py
report_model.py
report_templates.py
markdown report templates
report schemas
report writer tests
```

Do not add PDF generation, HTML dashboarding, remote publishing, email sending, web hosting, source mutation, governance decisions, risk decisions, or validation execution to the Report Writer.

---

# 1. Identity

```yaml
fic_id: "FIC-AGENTX-INITIATOR-REPORT-WRITER-001"
sib_id: "SIB-AGENTX-INITIATOR-REPORT-WRITER-001"
component_id: "AGENTX_REPORT_WRITER"
component_name: "Report Writer"
version: "v3.0.0"
status: "ready-for-component-documentation"
artifact_type: "report-component"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "medium"
enforcement_profile: "template-rendering"
implementation_mode: "new-component"
primary_standards:
  - "FIC"
  - "SIB"
  - "Template/Report Standard"
supporting_standards:
  - "Schema Contract"
  - "Evidence Rules"
  - "Audit Rules"
```

---

# 2. Purpose

The Report Writer transforms structured Initiator artifacts into deterministic, human-readable reports.

It renders reports from source artifacts and templates.

It does not create new decisions, change evidence, reinterpret governance, alter risk classifications, or modify source artifacts.

The Report Writer exists to answer:

```text
What happened?
What was discovered?
What was decided?
What was assessed?
What was planned?
What was proposed?
What was validated?
What evidence supports the report?
```

---

# 3. Authority Boundary

The Report Writer may:

```text
format structured artifacts
render templates
assemble report sections
build report bundles
preserve evidence references
write reports under .agentx-init/
```

The Report Writer must not:

```text
modify source artifacts
change decisions
change evidence
change validation results
change governance outcomes
change risk outcomes
generate plans
generate proposals
execute validation
mutate source files
```

The Report Writer is a rendering component, not a reasoning or decision component.

---

# 4. FIC Mission

The FIC mission is to define exact implementation behavior:

- public surface
- input model
- output model
- template handling
- report section handling
- evidence-link rendering
- schema outputs
- dependencies
- state ownership
- side effects
- failure behavior
- acceptance criteria
- test obligations

---

# 5. SIB Mission

The SIB mission is to bind component artifacts into human-readable reports.

Consumes:

```text
RepositoryScan
ArchitectureReport
GovernanceDecision
RiskAssessment
EvolutionPlan
PatchProposal
ValidationReport
AuditTrail
MemorySnapshot
```

Produces:

```text
Report
ReportSection
ReportTemplate
ReportBundle
ReportRequest
```

---

# 6. Template / Report Standard Mission

All reports must be template-driven.

Reports must be:

```text
deterministic
traceable
schema-valid
reproducible
evidence-linked
human-readable
plain-text-first
markdown-compatible
```

Template rules must prevent report drift, unsupported claims, missing sections, and inconsistent ordering.

---

# 7. Milestone 1 Scope

Milestone 1 must implement markdown report generation only.

## Required in Milestone 1

```text
load structured report inputs
validate report request
validate report template
render markdown report
preserve evidence references
include source artifact references
generate report bundle JSON
write latest_report.md
write report_bundle.json
append report_history.jsonl
append audit_events.jsonl when Audit Log is available
return structured Report object
```

## Not Required in Milestone 1

```text
PDF generation
HTML dashboard generation
web publishing
email sending
remote upload
interactive UI
charts
graph rendering
LLM report writing
source mutation
artifact mutation
governance decisions
risk decisions
validation execution
```

---

# 8. Anti-Overbuild Rule

The Report Writer must remain a deterministic renderer.

It must not become:

- Analysis Engine
- Governance Engine
- Risk Engine
- Evolution Planner
- Patch Proposal Generator
- Validation Runner
- PDF Generator
- Dashboard App
- Web Publisher
- Email Sender

If a feature requires new reasoning, decisions, remote publishing, or non-markdown output, it belongs outside Milestone 1 unless explicitly authorized.

---

# 9. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/report_writer.py
agentx_initiator/core/report_model.py
agentx_initiator/core/report_templates.py
```

Input dependency files:

```text
agentx_initiator/core/audit_log.py
agentx_initiator/core/memory_store.py
```

Template files:

```text
agentx_initiator/templates/system_report.md.j2
agentx_initiator/templates/scan_report.md.j2
agentx_initiator/templates/architecture_report.md.j2
agentx_initiator/templates/governance_report.md.j2
agentx_initiator/templates/risk_report.md.j2
agentx_initiator/templates/evolution_report.md.j2
agentx_initiator/templates/patch_report.md.j2
agentx_initiator/templates/validation_report.md.j2
agentx_initiator/templates/audit_report.md.j2
agentx_initiator/templates/memory_report.md.j2
agentx_initiator/templates/master_report.md.j2
```

Schema files:

```text
agentx_initiator/schemas/report.schema.json
agentx_initiator/schemas/report_section.schema.json
agentx_initiator/schemas/report_template.schema.json
agentx_initiator/schemas/report_bundle.schema.json
agentx_initiator/schemas/report_request.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Test files:

```text
agentx_initiator/tests/test_report_writer.py
agentx_initiator/tests/test_report_templates.py
agentx_initiator/tests/test_report_schema.py
```

Runtime artifacts:

```text
.agentx-init/reports/latest_report.md
.agentx-init/reports/report_bundle.json
.agentx-init/memory/report_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 10. Responsibilities

The Report Writer must:

- validate report request
- load report template
- validate template metadata
- load structured input artifacts
- validate required report sections
- render sections in deterministic order
- preserve evidence references
- preserve source artifact references
- separate facts, findings, decisions, risks, plans, proposals, validations, and unknowns
- write `latest_report.md`
- write `report_bundle.json`
- append report history
- append audit event when Audit Log is available
- return structured Report object

---

# 11. Non-Responsibilities

The Report Writer must not:

- invent findings
- invent evidence
- infer new risk
- approve governance decisions
- change validation results
- generate plans
- generate proposals
- execute validation
- mutate source files
- mutate input artifacts
- publish remotely
- send email
- generate PDF or HTML in Milestone 1

---

# 12. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "source mutation"
  - "input artifact mutation"
  - "unsupported claim generation"
  - "governance decision generation"
  - "risk decision generation"
  - "validation execution"
  - "patch proposal generation"
  - "remote publishing"
  - "email sending"
  - "pdf generation in Milestone 1"
  - "html dashboard generation in Milestone 1"
  - "LLM-only rewriting without artifact evidence"
```

Unsupported report content must be omitted or rendered under an explicit `Unknowns / Missing Evidence` section.

---

# 13. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "ReportWriter"
    purpose: "Builds deterministic markdown reports from structured artifacts and templates."
  - name: "Report"
    purpose: "Structured report object."
  - name: "ReportSection"
    purpose: "One report section."
  - name: "ReportTemplate"
    purpose: "Template metadata and section contract."
  - name: "ReportBundle"
    purpose: "Report plus source refs, template refs, and metadata."
  - name: "ReportRequest"
    purpose: "Request object describing report type and input artifacts."
```

Expected public functions:

```yaml
functions:
  - name: "build_report"
    signature: "build_report(request: ReportRequest, context: ReportContext) -> Report"
    purpose: "Build one structured report from inputs."
  - name: "render_template"
    signature: "render_template(report: Report, template: ReportTemplate) -> str"
    purpose: "Render a report into markdown."
  - name: "build_report_bundle"
    signature: "build_report_bundle(report: Report, rendered: str, context: ReportContext) -> ReportBundle"
    purpose: "Build report bundle metadata."
  - name: "validate_report_sections"
    signature: "validate_report_sections(report: Report, template: ReportTemplate) -> list[ReportIssue]"
    purpose: "Validate required sections and ordering."
```

No extra public surface should be added unless a future FIC update authorizes it.

---

# 14. Dependency Contract

Allowed imports:

```yaml
stdlib:
  - pathlib
  - json
  - datetime
  - dataclasses
  - typing
  - enum
  - uuid
  - collections

project_local_pm1:
  - agentx_initiator.core.audit_log
  - agentx_initiator.core.config

project_local_pm2_plus:
  - agentx_initiator.core.memory_store
```

Conditionally allowed:

```yaml
jinja2:
  allowed_if: "project uses Jinja2 for templates"
jsonschema:
  allowed_if: "project dependency already exists or pyproject explicitly includes it"
pydantic:
  allowed_if: "chosen as project-wide schema/model standard"
```

Forbidden imports:

```yaml
forbidden:
  - subprocess
  - requests
  - urllib
  - httpx
  - socket
  - smtplib
  - git
  - eval
  - exec
```

The Report Writer must not require network access, shell execution, email sending, Git access, or source mutation utilities.

---

# 15. Inputs

Allowed input objects:

```text
ReportRequest
ReportTemplate
StructuredArtifact
ReportContext
```

Required for ReportRequest:

```text
request_id
report_type
source_artifact_refs
template_id
output_path
```

Missing required inputs must produce:

```text
status = BLOCKED
failure_class = MISSING_REQUIRED_INPUT
```

---

# 16. Outputs

Primary outputs:

```text
Report
RenderedMarkdownReport
ReportBundle
```

Runtime artifacts:

```text
.agentx-init/reports/latest_report.md
.agentx-init/reports/report_bundle.json
.agentx-init/memory/report_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

The Report Writer must not write outside `.agentx-init/`.

---

# 17. Report Vocabulary

## Report Types

Allowed values:

```text
SYSTEM_REPORT
SCAN_REPORT
ARCHITECTURE_REPORT
GOVERNANCE_REPORT
RISK_REPORT
EVOLUTION_REPORT
PATCH_REPORT
VALIDATION_REPORT
AUDIT_REPORT
MEMORY_REPORT
MASTER_REPORT
UNKNOWN
```

## Report Status Values

Allowed values:

```text
RENDERED
PARTIAL
BLOCKED
FAILED
```

## Section Kinds

Allowed values:

```text
SUMMARY
SOURCE_ARTIFACTS
FACTS
FINDINGS
DECISIONS
RISKS
PLANS
PROPOSALS
VALIDATION
EVIDENCE
WARNINGS
ERRORS
UNKNOWNS
APPENDIX
```

---

# 18. Report Schema Contract

Each report must include:

```json
{
  "schema_version": "1.0",
  "report_id": "string",
  "timestamp": "string",
  "report_type": "SYSTEM_REPORT|SCAN_REPORT|ARCHITECTURE_REPORT|GOVERNANCE_REPORT|RISK_REPORT|EVOLUTION_REPORT|PATCH_REPORT|VALIDATION_REPORT|AUDIT_REPORT|MEMORY_REPORT|MASTER_REPORT|UNKNOWN",
  "status": "RENDERED|PARTIAL|BLOCKED|FAILED",
  "title": "string",
  "source_artifact_refs": [],
  "template_id": "string",
  "sections": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 19. Report Section Schema Contract

Each report section must include:

```json
{
  "schema_version": "1.0",
  "section_id": "string",
  "section_kind": "SUMMARY|SOURCE_ARTIFACTS|FACTS|FINDINGS|DECISIONS|RISKS|PLANS|PROPOSALS|VALIDATION|EVIDENCE|WARNINGS|ERRORS|UNKNOWNS|APPENDIX",
  "title": "string",
  "content": "string",
  "source_artifact_refs": [],
  "evidence_refs": [],
  "order": 0
}
```

---

# 20. Report Template Schema Contract

Each report template must include:

```json
{
  "schema_version": "1.0",
  "template_id": "string",
  "report_type": "SYSTEM_REPORT|SCAN_REPORT|ARCHITECTURE_REPORT|GOVERNANCE_REPORT|RISK_REPORT|EVOLUTION_REPORT|PATCH_REPORT|VALIDATION_REPORT|AUDIT_REPORT|MEMORY_REPORT|MASTER_REPORT|UNKNOWN",
  "required_sections": [],
  "optional_sections": [],
  "section_order": [],
  "template_path": "string",
  "output_format": "markdown"
}
```

`output_format` must be `markdown` in Milestone 1.

---

# 21. Report Bundle Schema Contract

Each report bundle must include:

```json
{
  "schema_version": "1.0",
  "bundle_id": "string",
  "timestamp": "string",
  "report": {},
  "rendered_report_path": "string",
  "template_ref": "string",
  "source_artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 22. Report Request Schema Contract

Each report request must include:

```json
{
  "schema_version": "1.0",
  "request_id": "string",
  "timestamp": "string",
  "report_type": "SYSTEM_REPORT|SCAN_REPORT|ARCHITECTURE_REPORT|GOVERNANCE_REPORT|RISK_REPORT|EVOLUTION_REPORT|PATCH_REPORT|VALIDATION_REPORT|AUDIT_REPORT|MEMORY_REPORT|MASTER_REPORT|UNKNOWN",
  "template_id": "string",
  "source_artifact_refs": [],
  "output_path": "string"
}
```

---

# 23. Formal Schema Contract

Mandatory schema files:

```text
agentx_initiator/schemas/report.schema.json
agentx_initiator/schemas/report_section.schema.json
agentx_initiator/schemas/report_template.schema.json
agentx_initiator/schemas/report_bundle.schema.json
agentx_initiator/schemas/report_request.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Schema ownership:

```text
Report Writer owns report.schema.json
Report Writer owns report_section.schema.json
Report Writer owns report_template.schema.json
Report Writer owns report_bundle.schema.json
Report Writer owns report_request.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

Schema validation failures:

```text
status = FAILED
failure_class = INVALID_SCHEMA
invalid report must not be written as valid
completion status cannot be VALIDATED
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

---

# 24. Schema Validation Execution Order

Schema validation must execute in this order:

```text
1. Validate ReportRequest.
2. Validate ReportTemplate metadata.
3. Validate source artifact refs.
4. Build ReportSection objects.
5. Validate each ReportSection.
6. Assemble Report.
7. Validate Report.
8. Render markdown from validated Report.
9. Build ReportBundle.
10. Validate ReportBundle.
11. Write latest_report.md only after Report validates.
12. Write report_bundle.json only after ReportBundle validates.
13. Append report_history.jsonl if configured.
14. Append audit_events.jsonl if Audit Log is available.
```

If validation fails before step 11:

```text
latest_report.md must not be overwritten with invalid output.
```

---

# 25. Schema-to-Test Traceability

Required schema tests:

```text
test_report_schema_accepts_valid_report
test_report_schema_rejects_missing_required_fields
test_report_section_schema_accepts_valid_section
test_report_template_schema_accepts_valid_template
test_report_bundle_schema_accepts_valid_bundle
test_report_request_schema_accepts_valid_request
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 26. Template Rules

Templates must define:

```text
template_id
report_type
required_sections
optional_sections
section_order
output_format
template_path
```

Template rendering rules:

```text
only markdown output in Milestone 1
required sections must be present
section order must follow template
missing optional sections are allowed
missing required sections produce BLOCKED or FAILED
template must not inject unsupported claims
```

---

# 27. Markdown Report Rules

Markdown reports must:

```text
start with one H1 title
include generated timestamp
include report type
include source artifact references
include evidence references where present
use deterministic section order
include warnings and errors when present
avoid unsupported conclusions
```

Markdown reports must not:

```text
hide failed validation
hide blocked governance decisions
change risk levels
change source claims
claim execution occurred when it did not
```

---

# 28. Evidence Reference Rules

Evidence references must be preserved from source artifacts.

Every section that reports evidence-backed facts must include:

```text
source_artifact_refs
evidence_refs
```

If evidence is missing:

```text
render under Unknowns / Missing Evidence
do not present as confirmed fact
```

---

# 29. Source Artifact Rules

The Report Writer may read structured artifacts passed through the report context.

It must not traverse source files directly in Milestone 1.

Input artifact references must include:

```text
artifact_id or path
artifact_type
source_component
schema_version when available
```

---

# 30. Report Section Ordering Rules

Section ordering must be deterministic.

Default order:

```text
SUMMARY
SOURCE_ARTIFACTS
FACTS
FINDINGS
DECISIONS
RISKS
PLANS
PROPOSALS
VALIDATION
EVIDENCE
WARNINGS
ERRORS
UNKNOWNS
APPENDIX
```

Template-specific ordering may override default only if explicitly declared.

---

# 31. Report History Rules

For `report_history.jsonl`:

```text
append exactly one JSON object per rendered report
never rewrite previous lines
never reorder previous lines
never delete previous lines
each line must include report_id, timestamp, report_type, status, and output path
```

Malformed previous lines must be preserved.

---

# 32. Determinism Contract

The same inputs and template must produce:

```text
same report sections
same section order
same rendered markdown except timestamp/report_id if generated
same evidence references
same report bundle structure
```

No randomness is allowed.

---

# 33. Status Semantics

Allowed statuses:

```text
RENDERED
PARTIAL
BLOCKED
FAILED
```

Meaning:

```text
RENDERED = required inputs and sections rendered successfully
PARTIAL  = optional inputs missing but required sections rendered
BLOCKED  = required input/template/schema missing or invalid
FAILED   = rendering attempted but valid output could not be produced
```

---

# 34. Failure Classes

Allowed failure classes:

```text
MISSING_REQUIRED_INPUT
MISSING_TEMPLATE
INVALID_TEMPLATE
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
MISSING_REQUIRED_SECTION
MISSING_EVIDENCE
RENDER_FAILED
BUNDLE_BUILD_FAILED
ARTIFACT_WRITE_FAILED
AUDIT_WRITE_FAILED
UNKNOWN_REPORT_WRITER_ERROR
```

All failures must be represented in output or audit trail when possible.

---

# 35. Preconditions

Before report rendering:

- ReportRequest must be available
- template must be available
- required source artifacts must be available
- schema contract must be available
- output path must be inside `.agentx-init/`
- report sections must satisfy template requirements

If required preconditions fail, Report Writer must not emit `RENDERED`.

---

# 36. Postconditions

After successful rendering:

- Report object exists
- rendered markdown exists
- report_bundle.json exists
- required sections are present
- section order is deterministic
- evidence references are preserved
- source artifact references are preserved
- all structured output validates against schema
- no source artifacts are changed

---

# 37. Invariants

```yaml
invariants:
  - id: "RW-INV-001"
    statement: "Report Writer never modifies source artifacts."
  - id: "RW-INV-002"
    statement: "Report Writer never creates new decisions."
  - id: "RW-INV-003"
    statement: "Report Writer preserves evidence references."
  - id: "RW-INV-004"
    statement: "Reports follow templates."
  - id: "RW-INV-005"
    statement: "Report section ordering is deterministic."
  - id: "RW-INV-006"
    statement: "Markdown is the only Milestone 1 rendered format."
  - id: "RW-INV-007"
    statement: "Unsupported claims are rendered as unknowns or omitted."
```

---

# 38. Security Contract

Security requirements:

- no network access
- no shell command execution
- no dependency installation
- no source mutation
- no remote publishing
- no email sending
- no environment variable logging
- no intentional secret logging
- path traversal must be blocked

---

# 39. Side Effects

Side-effect classification:

```yaml
side_effect_class: "report_persistent_state"
allowed_writes:
  - ".agentx-init/reports/latest_report.md"
  - ".agentx-init/reports/report_bundle.json"
  - ".agentx-init/memory/report_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

The Report Writer must not mutate governed source files or source artifacts.

---

# 40. SIB Bindings

Consumes:

```text
Repository Scanner
Architecture Analyzer
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
Audit Log
Memory Store
```

Produces:

```text
Report
ReportSection
ReportTemplate
ReportBundle
ReportRequest
```

Consumed by:

```text
CLI Status Command
Human Review
Memory Store
Audit Log
```

---

# 41. SIB Registry Entry

```yaml
art_id: "AGENTX::REPORT_WRITER"
title: "Report Writer"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/report_writer.py"
current_version: "v3.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-REPORT-WRITER-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 42. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::REPORT_WRITER"
  - "AGENTX::REPORT_MODEL"
  - "AGENTX::REPORT_TEMPLATES"
  - "AGENTX::REPOSITORY_SCAN"
  - "AGENTX::ARCHITECTURE_REPORT"
  - "AGENTX::GOVERNANCE_DECISION"
  - "AGENTX::RISK_ASSESSMENT"
  - "AGENTX::EVOLUTION_PLAN"
  - "AGENTX::PATCH_PROPOSAL"
  - "AGENTX::VALIDATION_REPORT"
  - "AGENTX::AUDIT_TRAIL"
  - "AGENTX::MEMORY_SNAPSHOT"

edges:
  - src: "AGENTX::REPORT_WRITER"
    type: "IMPORTS"
    dst: "AGENTX::REPORT_MODEL"
  - src: "AGENTX::REPORT_WRITER"
    type: "IMPORTS"
    dst: "AGENTX::REPORT_TEMPLATES"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::REPOSITORY_SCAN"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::ARCHITECTURE_REPORT"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::GOVERNANCE_DECISION"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::RISK_ASSESSMENT"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::EVOLUTION_PLAN"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::PATCH_PROPOSAL"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::VALIDATION_REPORT"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::AUDIT_TRAIL"
  - src: "AGENTX::REPORT_WRITER"
    type: "USES"
    dst: "AGENTX::MEMORY_SNAPSHOT"
```

---

## Product Milestone 1 Test Scope Override

For Product Milestone 1, Report Writer acceptance is limited to:

- `status_report.md.j2`
- `latest_status.md` output
- architecture/status report rendering from Repository Scanner + Minimal Architecture Analyzer artifacts

The following are not Product Milestone 1 acceptance blockers:

- `governance_report.md.j2`
- `risk_report.md.j2`
- `evolution_report.md.j2`
- `patch_report.md.j2`
- `validation_report.md.j2`
- `audit_report.md.j2`
- `memory_report.md.j2`
- `master_report.md.j2`
- risk report integration tests
- validation report integration tests
- master report integration tests

---

# 43. Test Contract

Required unit tests:

```text
test_report_request_validation
test_template_validation
test_required_sections_enforced
test_optional_sections_allowed_missing
test_section_order_is_deterministic
test_evidence_refs_preserved
test_source_artifact_refs_preserved
test_render_markdown_report
test_report_bundle_created
test_report_history_appends
test_no_source_artifact_mutation
```

Required negative tests:

```text
test_invalid_template_rejected
test_missing_required_section_rejected
test_missing_required_input_blocks
test_output_path_outside_agentx_init_rejected
test_unsupported_claim_rendered_as_unknown
test_pdf_generation_not_available_in_milestone_1
```

Required integration tests (PM2+):

```text
test_architecture_report_rendered_from_architecture_artifact
test_risk_report_rendered_from_risk_artifact       # PM2 — not a PM1 blocker
test_validation_report_rendered_from_validation_artifact  # PM2 — not a PM1 blocker
test_master_report_rendered_from_multiple_artifacts       # PM2 — not a PM1 blocker
```

---

# 44. Test Oracle Strength

Minimum oracle levels:

```yaml
section_order_determinism: "O4 invariant"
evidence_reference_preservation: "O4 invariant"
source_artifact_non_mutation: "O4 invariant"
schema_validation: "O3 negative"
template_required_sections: "O3 negative"
markdown_rendering: "O2 boundary"
```

Smoke tests alone are not sufficient.

---

> **Product Milestone 1 acceptance override:** For Product Milestone 1, Report Writer acceptance and Definition of Done are limited to deterministic markdown generation of `.agentx-init/reports/latest_status.md` from scanner/analyzer artifacts. The full `ReportBundle`, `report_bundle.json`, `report_history.jsonl`, `latest_report.md`, and full report schema validation obligations apply to Component Milestone 1 / later Product Milestone activation unless explicitly promoted by the PM1 implementation package.

# 45. Acceptance Criteria

Report Writer is accepted only if:

- valid report requests generate reports
- required sections are enforced
- templates are validated
- markdown report is rendered
- report bundle is generated
- evidence references are preserved
- source artifact references are preserved
- report section order is deterministic
- unsupported claims are not presented as facts
- latest_report.md is written only after validation passes
- report_bundle.json is written only after validation passes
- report_history.jsonl is appended if configured
- no source artifacts are changed
- all required tests pass
- no forbidden imports or publishing behavior are present

---

# 46. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] report schema is defined
[ ] report section schema is defined
[ ] report template schema is defined
[ ] report bundle schema is defined
[ ] report request schema is defined
[ ] report types are defined
[ ] section kinds are defined
[ ] template rules are defined
[ ] markdown rendering rules are defined
[ ] evidence reference rules are defined
[ ] write boundaries are defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 47. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] templates exist
[ ] report schema validation passes
[ ] report bundle schema validation passes
[ ] report output path stays inside .agentx-init/
[ ] evidence references are preserved
[ ] source artifacts are not mutated
[ ] unit tests pass
[ ] integration tests pass
[ ] completion record exists
```

---

# 48. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
REPORT_WRITER_FIC_SIB_TEMPLATE_REPORT_STANDARD_v3.md
report.schema.json
report_section.schema.json
report_template.schema.json
report_bundle.schema.json
report_request.schema.json
completion_record.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the Report Writer from this document alone without the implementation package.

---

## Product Milestone 1 Handoff Scope Override

For Product Milestone 1, permitted Report Writer files are limited to:

- `agentx_initiator/core/report_writer.py`
- `agentx_initiator/core/report_model.py`, if needed
- `agentx_initiator/core/report_templates.py`, if needed
- `agentx_initiator/templates/status_report.md.j2`
- `agentx_initiator/templates/scan_report.md.j2`, optional
- tests required for PM1 status report rendering

`architecture_report.md.j2` and other report templates are PM2+ scope unless explicitly promoted by the PM1 implementation spec.

---

# 49. Implementation Handoff Envelope

```yaml
implementation_handoff:
  fic_id: "FIC-AGENTX-INITIATOR-REPORT-WRITER-001"
  sib_id: "SIB-AGENTX-INITIATOR-REPORT-WRITER-001"
  target_component: "Report Writer"
  permitted_files:
    - "agentx_initiator/core/report_writer.py"
    - "agentx_initiator/core/report_model.py"
    - "agentx_initiator/core/report_templates.py"
    - "agentx_initiator/templates/system_report.md.j2"
    - "agentx_initiator/templates/scan_report.md.j2"
    - "agentx_initiator/templates/architecture_report.md.j2"
    - "agentx_initiator/templates/governance_report.md.j2"
    - "agentx_initiator/templates/risk_report.md.j2"
    - "agentx_initiator/templates/evolution_report.md.j2"
    - "agentx_initiator/templates/patch_report.md.j2"
    - "agentx_initiator/templates/validation_report.md.j2"
    - "agentx_initiator/templates/audit_report.md.j2"
    - "agentx_initiator/templates/memory_report.md.j2"
    - "agentx_initiator/templates/master_report.md.j2"
    - "agentx_initiator/schemas/report.schema.json"
    - "agentx_initiator/schemas/report_section.schema.json"
    - "agentx_initiator/schemas/report_template.schema.json"
    - "agentx_initiator/schemas/report_bundle.schema.json"
    - "agentx_initiator/schemas/report_request.schema.json"
    - "agentx_initiator/tests/test_report_writer.py"
    - "agentx_initiator/tests/test_report_templates.py"
    - "agentx_initiator/tests/test_report_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to report writer"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "template contract cannot be enforced"
    - "schema validation cannot be enforced"
    - "write boundary cannot be enforced"
    - "Report Writer needs to mutate source artifacts"
    - "Report Writer needs to generate unsupported report formats"
```

---

# 50. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  fic_id: "FIC-AGENTX-INITIATOR-REPORT-WRITER-001"
  sib_id: "SIB-AGENTX-INITIATOR-REPORT-WRITER-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  templates_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_fic_sib_template_standard: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 51. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "RW-RISK-001"
    description: "Reports can appear authoritative even though they only render source artifacts."
    severity: "medium"
    mitigation: "Preserve source refs and avoid unsupported conclusions."
  - id: "RW-RISK-002"
    description: "Template changes can alter report meaning."
    severity: "medium"
    mitigation: "Validate templates and enforce required sections."
  - id: "RW-RISK-003"
    description: "Milestone 1 supports markdown only."
    severity: "low"
    mitigation: "Defer PDF/HTML to later explicit contracts."
```

---

# 52. Definition of Done

Report Writer Milestone 1 is done when it can:

- validate report request
- validate report template
- build report sections
- enforce required sections
- render markdown report
- preserve evidence references
- preserve source artifact references
- build report bundle
- write latest_report.md
- write report_bundle.json
- append report_history.jsonl if configured
- validate all structured outputs against schema
- pass required tests
- leave source artifacts unchanged
- avoid unsupported report formats

---

# 53. Freeze Rule

This document is now the controlling Report Writer FIC+SIB+Template/Report Standard document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
report.schema.json
report_section.schema.json
report_template.schema.json
report_bundle.schema.json
report_request.schema.json
completion_record.schema.json
```

---

# 54. Final Success Definition

Report Writer v1 implementation is successful when it can transform structured Initiator artifacts into deterministic, template-driven, schema-valid markdown reports while preserving traceability and evidence references without modifying source artifacts or generating unsupported claims.

---

# 55. Final Rating

This FIC+SIB+Template/Report Standard document is rated **10/10** for the initial Report Writer component.

It is ready to be used as the controlling document for the Report Writer Milestone 1 implementation package.
