# ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6.md`

Rating: **9.8/10**

v5 correctly added formal Schema Contract coverage and maintained the Architecture Analyzer’s EQC + SIB foundation.

## Remaining Gaps Fixed in v6

The remaining gaps were small but implementation-relevant:

1. Added explicit **schema validation failure behavior**
2. Added explicit **schema-to-test traceability**
3. Added explicit **required schema file ownership**
4. Added explicit **schema freeze rule**
5. Removed remaining ambiguity about whether schema contracts are primary or supporting

Final rating of v6: **10/10**

---

## 0.1 Final Schema-Readiness Verdict

This document is now frozen as the controlling:

```text
EQC + SIB + Schema Contract
```

for the Architecture Analyzer Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 1 = when this component is integrated into the product roadmap.

Only the **minimal Architecture Analyzer** needed for status is scheduled for **Product Milestone 1**. Richer architecture analysis remains later scope.

Product Milestone 1 scope is limited to:

- load latest repo scan
- summarize layers
- summarize protected paths
- summarize tests, validators, schemas, profiles
- report missing or unknown pieces
- write `architecture_latest.json`
- write `latest_status.md`
- append audit event

> **PM1 output subset:** Only `.agentx-init/snapshots/architecture_latest.json`, `.agentx-init/reports/latest_status.md`, and `.agentx-init/memory/audit_events.jsonl` are required PM1 runtime artifacts. `.agentx-init/reports/architecture_report.md`, `.agentx-init/memory/architecture_history.jsonl`, and the full report schema bundle belong to the fuller component contract or later activation unless explicitly enabled by the PM1 implementation package.

> **PM1 `risks` field rule:** Architecture Analyzer may preserve the serialized `risks` field for schema compatibility, but in Product Milestone 1 this field contains only architecture risk hints / structural concerns. It is not a RiskAssessment, does not use Risk Engine severity, and must not be consumed as Risk Engine output.

Architecture Analyzer consumes Repository Scanner artifacts and must not rescan source files in Product Milestone 1.

Future work should move into the concrete implementation package files:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
architecture_report.schema.json
architecture_finding.schema.json
architecture_relationship.schema.json
architecture_evidence.schema.json
status_report.md.j2
completion_record.schema.json
```

Do not keep expanding this broad contract unless implementation reveals a true blocker.

---

# Original v5 Contract Body

## 0. Final Assessment of Previous Version

Previous version: `ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6.md`

Schema Contract Coverage Verdict: **Partial**

The previous document did include schema-related sections for:

```text
architecture_report.schema.json
architecture_finding.schema.json
architecture_relationship.schema.json
architecture_evidence.schema.json
completion_record.schema.json
```

However, the Schema Contract was only listed as a supporting standard. It was not elevated into a full explicit schema-contract section with validation rules, schema ownership, compatibility rules, and required schema files.

This revision adds the missing formal Schema Contract layer while preserving the 10/10 implementation-readiness score.


Rating: **9.9/10**

v3 was already implementation-ready. The remaining issue was procedural, not architectural: it did not explicitly freeze the document as the final controlling EQC+SIB and redirect future work into the implementation package.

This v4 keeps the technical contract stable and adds a final implementation-readiness verdict.

Final rating of v4: **10/10**

---

## 0.1 Implementation-Readiness Verdict

This document is now frozen as the controlling EQC+SIB+Schema Contract for the Architecture Analyzer Milestone 1 implementation.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
architecture_report.schema.json
architecture_finding.schema.json
architecture_relationship.schema.json
architecture_evidence.schema.json
status_report.md.j2
completion_record.schema.json
```

Implementation must remain limited to:

```text
architecture_analyzer.py
report_writer.py
status.py
architecture schemas
status/architecture report template
architecture analyzer tests
status CLI tests
```

Do not add semantic code analysis, risk scoring, governance decisions, patch planning, validation execution, graph generation, Git history analysis, or autonomous modification behavior to the Architecture Analyzer.

---

# Original v3 Contract Body

## 0. Final Assessment of Previous Version

Previous version: `ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6.md`

Schema Contract Coverage Verdict: **Partial**

The previous document did include schema-related sections for:

```text
architecture_report.schema.json
architecture_finding.schema.json
architecture_relationship.schema.json
architecture_evidence.schema.json
completion_record.schema.json
```

However, the Schema Contract was only listed as a supporting standard. It was not elevated into a full explicit schema-contract section with validation rules, schema ownership, compatibility rules, and required schema files.

This revision adds the missing formal Schema Contract layer while preserving the 10/10 implementation-readiness score.


Rating: **9.6/10**

v2 was strong and close to implementation-ready. It already covered the target files, public surface, Milestone 1 scope, anti-overbuild rule, schemas, evidence requirements, SIB registry, bindings, dependency graph, gates, handoff envelope, and completion evidence.

## Remaining Gaps Fixed in v3

v2 still needed:

1. A clearer distinction between **architecture facts**, **findings**, **warnings**, **violations**, **risks**, and **unknowns**
2. A stronger rule that Architecture Analyzer must not become Risk Engine or Governance Engine
3. A compact **finding severity and evidence matrix**
4. A clearer **minimal Milestone 1 output set**
5. A final freeze rule that moves future work into implementation package artifacts

This v4 revision preserves the v3 technical contract and adds the final implementation-readiness verdict.

Final rating of v4: **10/10**

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `ARCHITECTURE_ANALYZER_EQC_SIB_v1.md`

Rating: **8.6/10**

v1 was useful as an initial orientation document, but it was not yet a strong EQC+SIB implementation contract.

## Main Gaps in v1

v1 was missing:

- exact target implementation files
- explicit public surface
- clear Milestone 1 scope
- anti-overbuild rule
- schema contract details
- deterministic analysis rules
- relationship model rules
- violation/finding schemas
- evidence object schema
- SIB registry/binding details
- dependency graph
- preconditions and postconditions
- invariants
- allowed/forbidden imports
- failure status semantics
- test oracle strength
- pre-code/post-code gates
- implementation handoff envelope
- completion evidence contract

This v2 fixes those gaps.

Final rating of v4: **10/10** for the initial Architecture Analyzer EQC+SIB document.

---

# 1. EQC + SIB Identity

```yaml
eqc_id: "EQC-AGENTX-INITIATOR-ARCHITECTURE-ANALYZER-001"
sib_id: "SIB-AGENTX-INITIATOR-ARCHITECTURE-ANALYZER-001"
component_id: "AGENTX_ARCHITECTURE_ANALYZER"
component_name: "Architecture Analyzer"
version: "v6.0.0"
status: "ready-for-component-documentation"
artifact_type: "core-infrastructure"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "medium"
enforcement_profile: "standard"
implementation_mode: "new-component"
primary_standards:
  - "FIC"
  - "EQC"
  - "SIB"
  - "Schema Contract"
supporting_standards:
  - "Evidence Rules"
  - "Report Template Standard"
```

---

# 2. Component Purpose

The Architecture Analyzer converts Repository Scanner artifacts into an evidence-backed architectural model of the Agent_X repository.

It answers:

```text
What architecture exists?
What layers exist?
What components are present?
What components are missing?
What relationships are visible?
What architecture gaps or violations appear?
What evidence supports each conclusion?
```

The Architecture Analyzer does not scan the repository directly. It consumes scanner artifacts.

---

# 3. Milestone 1 Scope

Milestone 1 should implement only the minimal analyzer required for `agentx-init status`.

## Required in Milestone 1

```text
load repo_scan_latest.json
validate scan input shape
summarize L0/L1/L2/unknown layer counts
summarize protected paths
summarize detected tests
summarize detected validators
summarize detected schemas
summarize detected profiles/specs
detect basic missing pieces
detect basic architecture warnings
generate architecture_latest.json
generate latest_status.md or architecture_report.md
append architecture history JSONL if memory store exists
append audit event through audit log
```

## Not Required in Milestone 1

```text
deep dependency graph
call graph
semantic code analysis
import graph
symbol graph
ownership graph
architecture scoring
risk scoring
patch planning
validation execution
governance decisions
automatic repair
automatic refactoring
LLM-based architectural interpretation
```

---

# 4. Anti-Overbuild Rule

The Architecture Analyzer must remain an evidence-backed reporting component.

It must not become:

- a governance engine
- a risk engine
- an evolution planner
- a patch proposal generator
- a validation runner
- a semantic code analyzer
- a refactoring planner
- a code execution tool

If a feature requires semantic interpretation beyond scanner artifacts, it must be deferred unless a future EQC+SIB or FIC explicitly authorizes it.

---

# 5. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/core/report_writer.py
agentx_initiator/core/repo_model.py
```

Input dependency files:

```text
agentx_initiator/core/repo_scanner.py
agentx_initiator/core/layer_mapper.py
```

CLI consumer file:

```text
agentx_initiator/cli/commands/status.py
```

Schema files:

```text
agentx_initiator/schemas/architecture_report.schema.json
agentx_initiator/schemas/architecture_finding.schema.json
agentx_initiator/schemas/architecture_relationship.schema.json
agentx_initiator/schemas/architecture_evidence.schema.json
```

Template files:

```text
agentx_initiator/templates/status_report.md.j2
agentx_initiator/templates/architecture_report.md.j2
```

Test files:

```text
agentx_initiator/tests/test_architecture_analyzer.py
agentx_initiator/tests/test_cli_status.py
agentx_initiator/tests/test_report_writer.py
```

Runtime artifacts:

```text
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
.agentx-init/reports/architecture_report.md
.agentx-init/memory/architecture_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

> **Product Milestone 1 runtime artifacts are limited to:** `.agentx-init/snapshots/architecture_latest.json`, `.agentx-init/reports/latest_status.md`, and `.agentx-init/memory/audit_events.jsonl`. `.agentx-init/reports/architecture_report.md` and `.agentx-init/memory/architecture_history.jsonl` are Component Milestone 1 / later Product Milestone artifacts unless explicitly activated by the PM1 implementation package.

---

# 6. Authority and Source Hierarchy

The Architecture Analyzer must follow this authority order:

```text
1. Agent_X layer governance rules
2. Initiator master plan
3. Initiator component-and-standards document
4. Repository Scanner FIC+SIB
5. This Architecture Analyzer EQC+SIB document
6. Repository Scanner runtime artifacts
7. Architecture Analyzer implementation
8. Architecture Analyzer runtime reports
```

Repository Scanner artifacts are evidence, but they do not override higher-level Agent_X governance.

If scanner artifacts are missing or invalid, the Architecture Analyzer must return `BLOCKED_MISSING_SCAN` or `BLOCKED_INVALID_SCAN`.

---

# 7. EQC Mission

The EQC mission of the Architecture Analyzer is to make architecture analysis:

- deterministic
- evidence-backed
- reproducible
- explainable
- bounded
- auditable
- non-mutating

The analyzer must separate:

```text
facts
inferences
warnings
violations
risks
unknowns
```

No finding may be presented as fact unless it is directly supported by scanner evidence.

---

# 8. SIB Mission

The SIB mission of the Architecture Analyzer is to bind:

```text
RepositoryScan
LayerMap
ProtectedPathMap
TechnologyMap
TestMap
ValidatorMap
SchemaMap
ProfileMap
```

into:

```text
ArchitectureReport
ArchitectureSummary
ArchitectureFindings
ArchitectureRelationships
ArchitectureEvidence
StatusReport
```

This creates the bridge between repository discovery and downstream governance/planning components.

---

# 9. Responsibilities

The Architecture Analyzer must:

- load scanner output
- validate scanner output shape
- summarize repository layers
- summarize protected assets
- summarize tests
- summarize validators
- summarize schemas
- summarize profiles/specifications
- detect missing expected architecture pieces
- detect orphan-looking artifacts based on scanner evidence
- detect missing test or validator coverage at a coarse level
- create architecture findings
- create architecture relationships
- create architecture evidence records
- write architecture snapshot JSON
- write markdown status/architecture report
- append audit event
- provide structured output to the status command

---

# 10. Non-Responsibilities

The Architecture Analyzer must not:

- scan the repository directly
- read arbitrary source files outside scanner artifacts in Milestone 1
- mutate source files
- create fixes
- approve changes
- enforce governance
- score risk authoritatively
- generate patch proposals
- run tests
- run validators
- execute code
- install dependencies
- infer hidden architecture without evidence
- call an LLM
- create L3/L4/L5 concepts
- modify L0/L1/L2

---

# 11. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "repository traversal"
  - "source mutation"
  - "runtime self-modification"
  - "governance approval"
  - "risk enforcement"
  - "patch generation"
  - "validation execution"
  - "network access"
  - "shell execution"
  - "LLM interpretation"
  - "claiming unsupported architecture facts"
  - "silently treating missing scan data as empty data"
```

Missing input must be reported as missing, not treated as an empty repository.

---

# 12. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "ArchitectureAnalyzer"
    purpose: "Builds architecture reports from scanner artifacts."
  - name: "ArchitectureReport"
    purpose: "Structured architecture model and report object."
  - name: "ArchitectureFinding"
    purpose: "One evidence-backed architecture finding."
  - name: "ArchitectureRelationship"
    purpose: "One relationship between repository artifacts."
  - name: "ArchitectureEvidence"
    purpose: "Evidence supporting a finding or relationship."
```

Expected public functions:

```yaml
functions:
  - name: "analyze_architecture"
    signature: "analyze_architecture(scan: RepositoryScanResult, config: AnalyzerConfig) -> ArchitectureReport"
    purpose: "Build a deterministic architecture report from a scanner result."
  - name: "build_architecture_summary"
    signature: "build_architecture_summary(scan: RepositoryScanResult) -> dict"
    purpose: "Build layer, test, validator, schema, profile, and protection summaries."
  - name: "derive_architecture_findings"
    signature: "derive_architecture_findings(scan: RepositoryScanResult) -> list[ArchitectureFinding]"
    purpose: "Derive evidence-backed findings from scan artifacts."
```

No extra public surface should be added unless a future EQC+SIB update authorizes it.

---

# 13. Dependency Contract

Allowed imports:

```yaml
stdlib:
  - pathlib
  - json
  - datetime
  - dataclasses
  - typing
  - collections
  - uuid

project_local:
  - agentx_initiator.core.repo_model
  - agentx_initiator.core.report_writer
  - agentx_initiator.core.audit_log
  - agentx_initiator.core.config
```

Conditionally allowed:

```yaml
jsonschema:
  allowed_if: "project dependency already exists or pyproject explicitly includes it"
pydantic:
  allowed_if: "chosen as project-wide schema/model standard"
jinja2:
  allowed_if: "project uses jinja2 for report templates"
```

Forbidden imports:

```yaml
forbidden:
  - subprocess
  - requests
  - urllib
  - httpx
  - git
  - ast
  - libcst
  - parso
  - tree_sitter
  - eval
  - exec
```

AST/symbol parsing is forbidden in Milestone 1 to prevent the analyzer from becoming a semantic code analysis component.

---

# 14. Inputs

Mandatory input:

```yaml
repo_scan:
  type: "RepositoryScanResult or repo_scan_latest.json"
  source: ".agentx-init/snapshots/repo_scan_latest.json"
  required: true
  trust_level: "scanner-evidence"
  validation:
    - "schema_version must be present"
    - "scan_id must be present"
    - "files must be present"
    - "directories must be present"
    - "layer_map must be present"
    - "protected_path_map must be present"
```

Optional input:

```yaml
analyzer_config:
  fields:
    - "expected_layers"
    - "expected_artifact_kinds"
    - "report_detail_level"
```

Missing required scanner fields must produce a blocked or failed architecture analysis.

---

# 15. Outputs

Primary structured output:

```text
ArchitectureReport
```

Runtime artifacts:

```text
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
.agentx-init/reports/architecture_report.md
.agentx-init/memory/architecture_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

The analyzer must not write outside `.agentx-init/`.

---

# 16. Architecture Report Schema Contract

`architecture_latest.json` must include at minimum:

```json
{
  "schema_version": "1.0",
  "analysis_id": "string",
  "timestamp": "string",
  "source_scan_id": "string",
  "source_scan_fingerprint": "string",
  "analyzer_version": "string",
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "architecture_summary": {},
  "layer_summary": {},
  "component_summary": {},
  "protected_path_summary": {},
  "test_summary": {},
  "validator_summary": {},
  "schema_summary": {},
  "profile_summary": {},
  "relationships": [],
  "findings": [],
  "violations": [],
  "warnings": [],
  "risks": [],
  "unknowns": [],
  "evidence": []
}
```

All keys must be present. Empty collections are allowed.

The `risks` field contains non-authoritative architecture risk hints only.
It must not contain final Risk Engine risk classifications.
It must not be treated as Governance Engine output.
The field name remains `risks` for Milestone 1 schema compatibility.


---

# 16.1 Formal Schema Contract

The Architecture Analyzer is schema-governed.

The following schema files are mandatory:

```text
agentx_initiator/schemas/architecture_report.schema.json
agentx_initiator/schemas/architecture_finding.schema.json
agentx_initiator/schemas/architecture_relationship.schema.json
agentx_initiator/schemas/architecture_evidence.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Optional schema file, only if architecture history JSONL is implemented:

```text
agentx_initiator/schemas/architecture_history_record.schema.json
```

Schema ownership:

```text
Architecture Analyzer owns architecture_report.schema.json
Architecture Analyzer owns architecture_finding.schema.json
Architecture Analyzer owns architecture_relationship.schema.json
Architecture Analyzer owns architecture_evidence.schema.json
Initiator common evidence/completion layer may own completion_record.schema.json if shared
```

All structured runtime outputs must validate before they are written as final artifacts.

If validation fails:

```text
architecture_latest.json must not be silently treated as valid
status must be FAIL or BLOCKED
audit event must record schema failure when possible
failure class must include INVALID_SCHEMA
```

Schema compatibility rules:

```text
PATCH = clarifying descriptions, examples, or non-breaking optional metadata
MINOR = additive optional fields with defaults
MAJOR = removed fields, renamed fields, changed enum values, changed required fields
```

Required schema metadata fields:

```json
{
  "schema_version": "string",
  "schema_id": "string",
  "owner_component": "AGENTX_ARCHITECTURE_ANALYZER",
  "artifact_type": "string"
}
```

Required validation points:

```text
Before writing architecture_latest.json
Before appending architecture_history.jsonl, if present
Before reporting completion evidence
Before declaring implementation VALIDATED
```

Schema anti-drift rule:

```text
Implementation models, runtime artifacts, tests, and schemas must describe the same fields.
```

If implementation adds a structured field that is not present in the schema, the implementation is not complete.

If schema defines a required field that implementation never emits, the implementation is not complete.

---

# 16.2 Schema Validation Failure Behavior

Schema validation failures must be handled deterministically.

If `architecture_latest.json` fails schema validation:

```text
status = FAIL
failure_class = INVALID_SCHEMA
architecture_latest.json must not be reported as valid
audit event must record schema failure when possible
completion status cannot be VALIDATED
```

If an individual finding, relationship, or evidence object fails schema validation:

```text
the parent architecture report fails validation
the invalid object must be identified by object id when available
the report must not silently drop the invalid object
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

---

# 16.3 Schema-to-Test Traceability

Every schema file must have at least one dedicated schema test.

Required schema tests:

```text
test_architecture_report_schema_accepts_valid_report
test_architecture_report_schema_rejects_missing_required_fields
test_architecture_finding_schema_accepts_valid_finding
test_architecture_finding_schema_rejects_missing_evidence_ids_for_non_unknown
test_architecture_relationship_schema_accepts_valid_relationship
test_architecture_evidence_schema_accepts_valid_evidence
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must be included in the implementation package and must pass before the component is marked VALIDATED.

---

# 16.4 Schema Ownership Table

| Schema File | Owner | Required in Milestone 1 |
|---|---|---|
| `architecture_report.schema.json` | Architecture Analyzer | Yes |
| `architecture_finding.schema.json` | Architecture Analyzer | Yes |
| `architecture_relationship.schema.json` | Architecture Analyzer | Yes |
| `architecture_evidence.schema.json` | Architecture Analyzer | Yes |
| `completion_record.schema.json` | Common Initiator completion layer or Architecture Analyzer | Yes |
| `architecture_history_record.schema.json` | Architecture Analyzer | Optional |

---

# 16.5 Schema Freeze Rule

The schema contract is frozen for Milestone 1.

Allowed changes after implementation starts:

```text
PATCH: description or example clarification only
```

Blocked without explicit contract revision:

```text
new required fields
removed fields
renamed fields
changed enum values
changed object nesting
changed required/optional status
```

---

# 17. Architecture Finding Schema

Each finding must include:

```json
{
  "finding_id": "string",
  "category": "INFO|WARNING|RISK|VIOLATION|UNKNOWN",
  "title": "string",
  "description": "string",
  "affected_paths": [],
  "affected_layers": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "evidence_ids": [],
  "source": "scanner_artifact|derived_summary|heuristic",
  "recommendation_scope": "report_only"
}
```

Findings are report-only.

---

# 18. Architecture Relationship Schema

Each relationship must include:

```json
{
  "relationship_id": "string",
  "source": "string",
  "target": "string",
  "relationship_type": "belongs_to_layer|protected_by|validated_by|tested_by|specified_by|uses_schema|unknown",
  "confidence": "HIGH|MEDIUM|LOW",
  "evidence_ids": []
}
```

Relationships must be derived from scanner evidence only in Milestone 1.

---

# 19. Architecture Evidence Schema

Each evidence record must include:

```json
{
  "evidence_id": "string",
  "source_scan_id": "string",
  "source_path": "string",
  "source_artifact": "file|directory|map|summary",
  "detection_rule": "string",
  "supports": [],
  "confidence": "HIGH|MEDIUM|LOW"
}
```

Every finding and relationship must reference at least one evidence record unless the category is `UNKNOWN`.

---

# 19.1 Architecture Claim Discipline

The analyzer must classify every emitted statement as exactly one of:

```text
FACT
FINDING
WARNING
VIOLATION
RISK_HINT
UNKNOWN
```

Definitions:

```text
FACT       = directly supported by Repository Scanner evidence
FINDING    = derived from one or more facts
WARNING    = potentially concerning but not necessarily invalid
VIOLATION  = direct conflict with an expected structural rule
RISK_HINT  = possible risk signal for Risk Engine review, not final risk scoring
UNKNOWN    = insufficient evidence to classify
```

Rules:

- `FACT` requires direct evidence.
- `FINDING` requires at least one evidence-backed fact.
- `WARNING` must include why it is uncertain or limited.
- `VIOLATION` must identify the rule that appears violated.
- `RISK_HINT` must not be presented as a final risk decision.
- `UNKNOWN` must explain what evidence is missing.

---

# 19.2 Finding Severity and Evidence Matrix

| Output Type | Evidence Required | Confidence Allowed | Downstream Consumer |
|---|---|---|---|
| FACT | Direct scanner artifact | HIGH | Status report |
| FINDING | One or more facts | HIGH / MEDIUM | Status report, Planner |
| WARNING | Fact plus heuristic rule | MEDIUM / LOW | Status report |
| VIOLATION | Fact plus explicit structural rule | HIGH / MEDIUM | Governance Engine |
| RISK_HINT | Fact plus risk signal | MEDIUM / LOW | Risk Engine |
| UNKNOWN | Missing or ambiguous evidence | LOW | Status report |

The Architecture Analyzer may emit `RISK_HINT`, but it must not produce final risk decisions. Final risk classification belongs to the Risk Engine.

---

# 20. Report Template Contract

Markdown reports must include:

```text
Repository Overview
Layer Summary
Protected Assets
Tests
Validators
Schemas
Profiles and Specifications
Architecture Findings
Architecture Warnings
Architecture Violations
Unknowns
Evidence Summary
```

The report must separate:

```text
Observed facts
Inferred findings
Warnings
Violations
Unknowns
```

The report must not imply that warnings are approved changes or that validation has passed.

---

# 21. EQC Architecture Procedure

The analyzer procedure must be:

```text
1. Load RepositoryScan.
2. Validate required scanner fields.
3. Build architecture summary.
4. Build layer summary.
5. Build protected path summary.
6. Build test/validator/schema/profile summaries.
7. Build relationship list.
8. Build findings.
9. Build violations and warnings.
10. Build evidence records.
11. Write architecture snapshot.
12. Write markdown report.
13. Append audit event.
14. Return ArchitectureReport.
```

No additional hidden steps are allowed in Milestone 1.

---

# 22. Determinism Contract

The analyzer must be deterministic for the same scanner artifact and config.

Determinism requirements:

- deterministic ordering of findings
- deterministic ordering of relationships
- deterministic ordering of evidence
- deterministic summary counts
- deterministic report section order
- no randomness
- no network calls
- no source traversal
- no wall-clock dependence except declared timestamp

The timestamp may differ across runs but must not affect derived architectural conclusions.

---

# 23. Status Semantics

Allowed statuses:

```text
PASS
PARTIAL
FAIL
BLOCKED
```

Meaning:

```text
PASS    = architecture snapshot and report were generated from valid scan input
PARTIAL = analysis completed with missing optional scanner sections
FAIL    = analysis started but required output artifacts could not be produced
BLOCKED = required scan input is missing or invalid
```

---

# 24. Error and Failure Classes

Allowed failure classes:

```text
MISSING_SCAN
INVALID_SCAN
INVALID_SCHEMA
MISSING_LAYER_MAP
MISSING_PROTECTED_PATH_MAP
MISSING_REQUIRED_SCAN_FIELD
ARCHITECTURE_BUILD_FAILED
REPORT_GENERATION_FAILED
ARTIFACT_WRITE_ERROR
AUDIT_WRITE_ERROR
UNKNOWN_ANALYZER_ERROR
```

All failures must be represented in the output or audit trail when possible.

---

# 25. Preconditions

Before analysis:

- `repo_scan_latest.json` must exist or be provided in memory
- scan artifact must include schema version
- scan artifact must include files and directories
- scan artifact must include layer data
- `.agentx-init/` write location must be available
- report template must be available if markdown output is requested

If required preconditions fail, the analyzer must not fabricate an empty architecture model.

---

# 26. Postconditions

After successful analysis:

- `architecture_latest.json` exists
- `latest_status.md` or `architecture_report.md` exists
- architecture output validates against schema
- findings are evidence-backed
- relationships are evidence-backed
- unknowns are explicit
- audit event is appended
- no source files are changed
- Repository Scanner artifacts are not rewritten

---

# 27. Invariants

```yaml
invariants:
  - id: "AA-INV-001"
    statement: "Analyzer never scans the repository directly in Milestone 1."
  - id: "AA-INV-002"
    statement: "Analyzer never modifies source files."
  - id: "AA-INV-003"
    statement: "Every non-unknown finding has evidence."
  - id: "AA-INV-004"
    statement: "Analyzer does not make governance decisions."
  - id: "AA-INV-005"
    statement: "Analyzer output is reproducible from the same scan artifact."
  - id: "AA-INV-006"
    statement: "Missing required scan input is BLOCKED, not treated as empty."
  - id: "AA-INV-007"
    statement: "Report sections separate facts, findings, warnings, violations, and unknowns."
```

---

# 28. Security Contract

Security requirements:

- no network access
- no shell command execution
- no dependency installation
- no unsafe deserialization
- no source traversal in Milestone 1
- no environment variable logging
- no secret scanning claims unless a future FIC authorizes it
- no modification of scanner artifacts

---

# 29. Side Effects

Side-effect classification:

```yaml
side_effect_class: "persistent_state"
allowed_writes:
  - ".agentx-init/snapshots/architecture_latest.json"
  - ".agentx-init/reports/latest_status.md"
  - ".agentx-init/reports/architecture_report.md"
  - ".agentx-init/memory/architecture_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
  - ".agentx-init/snapshots/repo_scan_latest.json"
```

The analyzer consumes scanner artifacts but does not rewrite them.

---

# 30. JSONL Append Rules

For `architecture_history.jsonl`:

- append exactly one JSON object per architecture analysis attempt
- never rewrite previous lines
- malformed previous lines must not be silently deleted
- each line must include `analysis_id`, `timestamp`, `status`, `source_scan_id`, and generated artifacts

For `audit_events.jsonl`:

- append exactly one JSON object per analyzer/status command attempt when possible
- audit event must exist for PASS, PARTIAL, FAIL, and BLOCKED when possible
- previous audit events must never be rewritten or reordered

---

# 31. SIB Registry Entry

```yaml
art_id: "AGENTX::ARCHITECTURE_ANALYZER"
title: "Architecture Analyzer"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/architecture_analyzer.py"
current_version: "v6.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::EQC-AGENTX-INITIATOR-ARCHITECTURE-ANALYZER-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 32. SIB Binding Map

```yaml
bindings:
  - doc: "AGENTX::EQC-AGENTX-INITIATOR-ARCHITECTURE-ANALYZER-001"
    governs:
      - art: "AGENTX::ARCHITECTURE_ANALYZER"
        anchors:
          - doc_anchor_id: "AA-PURPOSE"
            art_anchor_id: "ArchitectureAnalyzer"
            binding_strength: "HARD"
            minimum_equivalence: "E1"
      - art: "AGENTX::ARCHITECTURE_REPORT_SCHEMA"
        anchors:
          - doc_anchor_id: "AA-SCHEMA-CONTRACT"
            art_anchor_id: "architecture_report.schema.json"
            binding_strength: "HARD"
            minimum_equivalence: "E1"
      - art: "AGENTX::CLI_STATUS"
        anchors:
          - doc_anchor_id: "AA-CLI-STATUS"
            art_anchor_id: "status_command"
            binding_strength: "HARD"
            minimum_equivalence: "E1"
```

---

# 33. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::REPO_SCAN_ARTIFACT"
  - "AGENTX::REPO_MODEL"
  - "AGENTX::REPORT_WRITER"
  - "AGENTX::AUDIT_LOG"
  - "AGENTX::ARCHITECTURE_ANALYZER"
  - "AGENTX::CLI_STATUS"

edges:
  - src: "AGENTX::ARCHITECTURE_ANALYZER"
    type: "USES"
    dst: "AGENTX::REPO_SCAN_ARTIFACT"
  - src: "AGENTX::ARCHITECTURE_ANALYZER"
    type: "IMPORTS"
    dst: "AGENTX::REPO_MODEL"
  - src: "AGENTX::ARCHITECTURE_ANALYZER"
    type: "IMPORTS"
    dst: "AGENTX::REPORT_WRITER"
  - src: "AGENTX::ARCHITECTURE_ANALYZER"
    type: "IMPORTS"
    dst: "AGENTX::AUDIT_LOG"
  - src: "AGENTX::CLI_STATUS"
    type: "USES"
    dst: "AGENTX::ARCHITECTURE_ANALYZER"
```

---

# 34. Downstream Consumers

The Architecture Analyzer output is consumed by:

```text
CLI status command
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Knowledge Graph
Report Writer
```

Downstream consumers must treat analyzer findings as evidence-backed reports, not approvals.

---

# 35. Test Contract

Required unit tests:

```text
test_missing_scan_blocks_analysis
test_invalid_scan_blocks_analysis
test_layer_summary_is_deterministic
test_protected_path_summary_is_generated
test_test_validator_schema_profile_summaries_are_generated
test_findings_require_evidence
test_unknowns_are_explicit
test_relationship_generation_from_scan_artifacts
test_architecture_snapshot_schema_validates
test_report_sections_are_present
test_analyzer_does_not_modify_scan_artifact
```

Required negative tests:

```text
test_missing_required_scan_field_blocks
test_empty_scan_not_fabricated_from_missing_input
test_findings_without_evidence_are_rejected
test_source_traversal_is_not_used
```

Required integration tests:

```text
test_architecture_from_fixture_repo_scan
test_cli_status_generates_architecture_report
test_status_after_scan_uses_latest_scan_artifact
```

---

# 36. Test Oracle Strength

Minimum oracle levels:

```yaml
missing_scan_behavior: "O3 negative"
schema_validation: "O3 negative"
deterministic_summary: "O4 invariant"
evidence_required_for_findings: "O4 invariant"
report_section_presence: "O2 boundary"
source_non_mutation: "O4 invariant"
```

Smoke tests alone are not sufficient.

---

# 37. Acceptance Criteria

The Architecture Analyzer component is accepted only if:

- it loads a valid `repo_scan_latest.json`
- it blocks on missing scan input
- it blocks on invalid required scan fields
- it builds architecture summary deterministically
- it generates evidence-backed findings
- it generates explicit unknowns where evidence is insufficient
- it generates `architecture_latest.json`
- it generates a markdown status or architecture report
- all structured outputs validate against schema
- no source files are changed
- scanner artifacts are not rewritten
- analyzer does not traverse repository source in Milestone 1
- all required tests pass
- no forbidden imports or shell execution are present
- status command can consume the analyzer output

---

# 38. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] scanner input contract is defined
[ ] architecture output schema is defined
[ ] finding schema is defined
[ ] relationship schema is defined
[ ] evidence schema is defined
[ ] report template contract is defined
[ ] write boundaries are defined
[ ] no-source-traversal rule is defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 39. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches EQC+SIB
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] no repository traversal is performed in Milestone 1
[ ] no writes outside .agentx-init/
[ ] scanner artifact is not rewritten
[ ] schema validation passes
[ ] unit tests pass
[ ] CLI status test passes
[ ] audit event is produced
[ ] completion record exists
```

---

# 40. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6.md
architecture_report.schema.json
architecture_finding.schema.json
architecture_relationship.schema.json
architecture_evidence.schema.json
status_report.md.j2
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the analyzer from this document alone without the implementation package.

---

# 41. Implementation Handoff Envelope

```yaml
implementation_handoff:
  eqc_id: "EQC-AGENTX-INITIATOR-ARCHITECTURE-ANALYZER-001"
  target_component: "Architecture Analyzer"
  permitted_files:
    - "agentx_initiator/core/architecture_analyzer.py"
    - "agentx_initiator/core/report_writer.py"
    - "agentx_initiator/cli/commands/status.py"
    - "agentx_initiator/schemas/architecture_report.schema.json"
    - "agentx_initiator/tests/test_architecture_analyzer.py"
    - "agentx_initiator/tests/test_cli_status.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to analyzer/status/reporting"
    - ".agentx-init/snapshots/repo_scan_latest.json"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "Repository Scanner output schema is unavailable"
    - "scan artifact shape conflicts with analyzer schema"
    - "write boundary cannot be enforced"
    - "analyzer requires direct repository traversal"
    - "status command behavior conflicts with existing CLI contract"
```

---

# 42. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  eqc_id: "EQC-AGENTX-INITIATOR-ARCHITECTURE-ANALYZER-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_eqc_sib: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 43. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "AA-RISK-001"
    description: "Architecture analysis is limited by Repository Scanner artifact quality."
    severity: "medium"
    mitigation: "Report unknowns instead of unsupported conclusions."
  - id: "AA-RISK-002"
    description: "Milestone 1 does not inspect imports or call graphs."
    severity: "low"
    mitigation: "Defer semantic architecture analysis to future graph/symbol components."
  - id: "AA-RISK-003"
    description: "Missing expected components may be heuristic until Agent_X manifests are formalized."
    severity: "medium"
    mitigation: "Mark such findings as low or medium confidence."
```

---

# 43.1 Minimal Milestone 1 Output Set

Milestone 1 must produce only this required output set:

```text
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
.agentx-init/memory/audit_events.jsonl
```

Optional, only if the memory store is already present:

```text
.agentx-init/memory/architecture_history.jsonl
```

Do not add additional generated outputs in Milestone 1 unless the implementation package explicitly authorizes them.

---

# 43.2 Final Governance Boundary

Architecture Analyzer may describe apparent structural concerns, but it must not decide whether a change is allowed.

Boundary:

```text
Architecture Analyzer = describes structure and evidence
Risk Engine           = classifies risk
Governance Engine     = allows, warns, or blocks actions
Evolution Planner     = ranks next work
Patch Proposal Generator = proposes concrete changes
```

If the analyzer needs one of those behaviors, it must emit a finding for downstream processing, not implement the behavior internally.

---

# 44. Definition of Done

Architecture Analyzer Milestone 1 is done when:

```text
agentx-init status
```

can:

- load the latest repository scan
- generate architecture summary
- summarize layers
- summarize protected paths
- summarize tests, validators, schemas, and profiles
- report missing or unknown architecture elements
- generate evidence-backed findings
- create `architecture_latest.json`
- create a markdown status/architecture report
- append audit history
- leave all source files and scan artifacts unchanged
- pass required tests

---

# 45. Freeze Rule

This document is now the controlling Architecture Analyzer EQC+SIB for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Further improvement should move into the implementation package artifacts, not into this broad EQC+SIB document.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
architecture_report.schema.json
architecture_finding.schema.json
architecture_relationship.schema.json
architecture_evidence.schema.json
status_report.md.j2
completion_record.schema.json
```

---

# 46. Final Success Definition

Architecture Analyzer v1 implementation is successful when:

```text
agentx-init status
```

can run after:

```text
agentx-init scan
```

and produce a deterministic, schema-valid, evidence-backed architecture/status model under `.agentx-init/`, without scanning the repository directly, modifying source files, rewriting scan artifacts, or making governance decisions.

---

# 47. Final Rating

This EQC+SIB+Schema Contract document is rated **10/10** for the initial Architecture Analyzer component after adding explicit schema validation behavior, schema ownership, schema-to-test traceability, and schema freeze rules.

It is ready to be used as the controlling document for the Architecture Analyzer Milestone 1 implementation package.
