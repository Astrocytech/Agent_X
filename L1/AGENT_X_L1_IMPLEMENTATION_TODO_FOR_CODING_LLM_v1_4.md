# Agent_X L1 Implementation TODO for a Coding LLM

**Document ID:** `AGENT-X-L1-IMPLEMENTATION-TODO-001`  
**Version:** `v1.4.0`  
**Status:** `ready-for-handoff`  
**Audience:** coding LLM agent, including weaker/smaller models such as Qwen/Gwen-style coding agents  
**Repository:** `https://github.com/Astrocytech/Agent_X`  
**Primary goal:** add the L1 control-plane scaffold and first safe implementation slice without damaging the existing L0 seed kernel.  
**Execution rule:** run Mode A only by default; do not run Mode B or Phase 9 in the same pass unless explicitly authorized in a separate task.

---

## 0. Rating of Previous TODO

Previous file rated: **9.8/10**.

The v1.3 file was close to handoff-ready, but it still left a few places where a weaker coding model could drift:

```text
1. Remaining L1 control documents 06-11 were described by a fill-in template instead of exact content.
2. Cross-checks were required, but there was no single Mode A validation script that a model could run repeatedly.
3. Source-standard discovery did not define an exact search order when the files are supplied beside the repo or already copied.
4. The TODO did not explicitly warn against shell here-doc mistakes when writing Markdown files that themselves contain fenced code blocks.
5. The bootstrap manifest did not require every created file category to be cross-checked against actual filesystem existence.
6. Final evidence did not require a single final validation log that links baseline, Mode A checks, git evidence, and cross-check files.
7. Placeholder sidecars could still be mistaken for validator-generated files unless the final decision table explicitly separated scaffold validation from release validation.
```

### Main gaps fixed in v1.4.0

```text
1. Added exact content requirements for remaining docs 06-11.
2. Added a mandatory Mode A bootstrap validation script.
3. Added deterministic source-standard discovery order.
4. Added safe file-writing rules for Markdown documents with nested code fences.
5. Added filesystem reconciliation for the bootstrap artifact manifest.
6. Added a final validation evidence bundle.
7. Strengthened the final status wording so Mode A VALIDATED means scaffold-valid only, not release-valid.
8. Added a no-release-claim rule for all placeholder ES/SIB/EQC/generated sidecars.
```

---

## 1. Read This First

You are not being asked to redesign Agent_X.

You are not being asked to make Agent_X autonomous.

You are not being asked to add model calls, network calls, shell access, live self-modification, or new L0 runtime behavior.

You are being asked to perform a bounded repository update that:

```text
1. preserves the current L0 seed kernel;
2. adds visible L1/L2 structure;
3. installs the five finalized L1 standards;
4. creates the L1 control-plane scaffold;
5. creates FIC/SIB/ES/EQC sidecars;
6. optionally implements UNIT-L1-001 Document Loader only after the scaffold is stable.
```

The safe outcome is more important than a large outcome.

If unsure, stop with `BLOCKED`.

---

## 2. Mandatory Operating Rules

### 2.1 Controlled final statuses

Your final status must be exactly one of:

```text
BLOCKED
NO_CHANGE
IMPLEMENTED_UNVALIDATED
VALIDATED
IMPLEMENTED_WITH_WAIVERS
REJECTED
```

Use `VALIDATED` only if every required check was actually run and passed.

Use `IMPLEMENTED_UNVALIDATED` if files were changed but one or more required checks were not run or did not pass.

Use `BLOCKED` if required context is missing, baseline checks fail, source standards are unavailable, or implementation would require guessing.

### 2.2 Never claim evidence you do not have

Do not write:

```text
passes
validated
complete
safe
working
```

unless you have command output or retained evidence.

### 2.3 L0 protection rules

Do not modify L0 behavior.

Do not weaken L0 governance.

Do not add shell, network, model calls, self-modification, or external tool execution to L0.

Do not make L0 import L1 or L2.

Do not make L0 depend on L1 documents, generated artifacts, FICs, SIB files, EQC files, ES files, or profiles.

### 2.4 No broad refactors

Do not reformat the whole repository.

Do not rename symbols unless required by path migration.

Do not delete advisory documents.

Do not collapse multiple phases into an uncontrolled rewrite.

### 2.5 Use exact paths

All paths in this TODO are repository-relative POSIX paths.

Do not invent alternative names.

Do not use absolute paths inside repository files.

### 2.6 Safe file-writing rule for Markdown

Several files in this TODO contain Markdown code fences inside Markdown examples. A weaker coding model must avoid malformed shell here-docs.

Preferred safe methods:

```text
1. Copy finalized standards as raw files, byte-for-byte.
2. Extract FIC-L1-001 using the provided Python extraction script.
3. For generated Markdown placeholders, use Python `Path.write_text(...)` or carefully quoted here-docs.
4. After writing each required Markdown file, run `test -s <path>` and inspect the first 20 lines.
```

Do not manually retype long standards.

Do not summarize a standard into a shorter file.

Do not create a Markdown file that ends in the middle of a code fence.

### 2.7 Deterministic bootstrap variables

Before writing evidence files, define one timestamp per run:

```bash
BOOTSTRAP_TS="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p L1/evidence/bootstrap
```

Use the same `BOOTSTRAP_TS` for all Mode A evidence files created in that run.

If the shell does not support this exact command, manually create a UTC timestamp in the same format and record it in the final response.

---

## 3. Execution Modes

There are two allowed modes.

### Mode A — Safe Additive L1 Scaffold

Use this mode first unless the user explicitly asked to move L0 files now.

Mode A creates:

```text
L1/
L2/
L1 standards
L1 docs
L1 FIC registry
L1 ES/SIB/EQC sidecars
L1 generated placeholders
```

Mode A does **not** move existing root `CODE/`, `tests/seed_l0/`, `scripts/`, or L0 authority files.

Mode A is safer for a weaker coding model.

### Mode B — Root-Visible L0 Migration

Use this mode only after Mode A passes and the baseline L0 proof commands pass.

Mode B moves existing L0 files into:

```text
L0/CODE/
L0/tests/seed_l0/
L0/scripts/
L0/docs/
L0/manifests/
```

Mode B must preserve root Makefile commands.

### Current recommended sequence

```text
1. Run Phase 0.
2. Run Mode A: Phases 1A through 8.
3. Run all proof commands.
4. Only then decide whether to run Mode B: Phase 2B.
5. Only after that, optionally run Phase 9 for UNIT-L1-001.
```

### Single-pass safe completion boundary

For a weaker coding model, the safest successful completion is:

```text
Mode A only: Phases 0 through 8A, then Phase 10 README update and final validation.
```

Do not run Mode B or Phase 9 in the same pass unless the user explicitly requested that extended scope.


---

## 4. Source Documents Required

The implementation packet must include these five finalized L1 standards as source files.

Expected source filenames:

```text
AGENT_X_L1_EQC_FIC_v0_6.md
AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md
AGENT_X_L1_LIGHTWEIGHT_EQC_SIB_v0_5.md
AGENT_X_L1_LIGHTWEIGHT_EQC_ES_v0_5.md
AGENT_X_L1_LIGHTWEIGHT_EQC_v0_5.md
```

### Source-standard discovery order

Look for the five source files in this order:

```text
1. repository root
2. `./input/`
3. `./docs/`
4. `./L1/standards_source/`
5. current working directory supplied by the execution harness
```

If the same source filename exists in multiple locations, stop and report:

```text
STATUS: BLOCKED
Reason: DUPLICATE_SOURCE_STANDARD_CANDIDATES
```

Do not choose between duplicate candidates by guessing.

They must be placed into the repository as:

```text
L1/standards/AGENT_X_L1_EQC_FIC.md
L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW.md
L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB.md
L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_ES.md
L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC.md
```

Do not summarize them.

Do not rewrite them.

Do not rename them after placement.

### Input package manifest

Before copying, record this source-standard intake map in completion evidence:

```yaml
source_standard_input_manifest:
  required:
    - source: "AGENT_X_L1_EQC_FIC_v0_6.md"
      target: "L1/standards/AGENT_X_L1_EQC_FIC.md"
    - source: "AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md"
      target: "L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW.md"
    - source: "AGENT_X_L1_LIGHTWEIGHT_EQC_SIB_v0_5.md"
      target: "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB.md"
    - source: "AGENT_X_L1_LIGHTWEIGHT_EQC_ES_v0_5.md"
      target: "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_ES.md"
    - source: "AGENT_X_L1_LIGHTWEIGHT_EQC_v0_5.md"
      target: "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC.md"
```

### Stop condition

If any of the five source standard files are unavailable, stop.

Return:

```text
STATUS: BLOCKED
Reason: SOURCE_STANDARD_MISSING
Missing file(s): <list>
```

---

## 5. Current Repository Reality to Detect

Before editing, inspect the repository.

Run:

```bash
pwd
git status --short
find . -maxdepth 2 -type d | sort
ls -la
```

Then classify the current layout.

### Layout A — current root L0 layout

This layout has:

```text
CODE/
tests/seed_l0/
scripts/
requirements/
CAPABILITY_MANIFEST.yaml
SEED_INVARIANTS.yaml
SEED_PACKAGE_MANIFEST.yaml
SEED_ACCEPTANCE.md
PUBLIC_CONTRACT_POLICY.md
EXTENSION_ABI.md
EVOLUTION_ACCEPTANCE.md
DOCUMENTS/
Makefile
pyproject.toml
README.md
```

### Layout B — already migrated layout

This layout already has:

```text
L0/CODE/
L0/tests/seed_l0/
L0/scripts/
L1/
L2/
```

### Rule

If the repo is Layout A, use Mode A first.

If the repo is Layout B, do not move L0 again.

If the repo is mixed, stop with:

```text
STATUS: BLOCKED
Reason: MIXED_LAYER_LAYOUT
```

A simple `L0/README.md` placeholder plus historical root L0 files is allowed in Mode A and is not mixed layout. Any duplicate active runtime directories, duplicate manifests, or duplicate test roots without migration notes are mixed layout.

---

## 6. Phase 0 — Baseline Verification

### Goal

Prove the repository works before editing.

### Commands

Run:

```bash
make install
make seed-boot
make prove-seed
make run
```

### Evidence capture

Save command output to:

```text
runtime_artifacts/l1_baseline_checks.log
```

After `L1/evidence/bootstrap/` exists, copy the same log to:

```text
L1/evidence/bootstrap/<UTC_TIMESTAMP>_baseline_checks.log
```

Timestamp format for filenames:

```text
YYYYMMDDTHHMMSSZ
```

### Stop condition

If any baseline command fails:

```text
STOP.
STATUS: BLOCKED
Reason: BLOCKED_BASELINE_FAIL
Do not reorganize the repo.
```

---

# MODE A — SAFE ADDITIVE L1 SCAFFOLD

---

## 7. Phase 1A — Create Visible Layer Folders Without Moving L0

### Goal

Create visible root `L1/` and `L2/` safely.

Create `L0/` only as a placeholder if the repo is still Layout A.

### Commands

```bash
mkdir -p L0 L1 L2
mkdir -p L1/evidence/bootstrap
```

### Create `L0/README.md`

```markdown
# Agent_X L0

L0 is the governed seed kernel.

In this repository state, L0 files may still exist at the historical root paths until the explicit L0 migration phase is performed.

L0 must remain minimal, proofable, and independently runnable.

L0 must not import L1 or L2.

Root Makefile commands must continue to prove L0:

- make seed-boot
- make prove-seed
- make run
```

### Create `L1/README.md`

```markdown
# Agent_X L1

L1 is the external evolution/controller layer for Agent_X.

L1 converts high-level improvement goals into bounded, FIC-governed implementation units.

L1 may inspect L0 contracts and proof outputs, but it must not mutate L0 without an explicit L0-impact FIC, proof plan, rollback plan, and review gate.
```

### Create `L2/README.md`

```markdown
# Agent_X L2

L2 is reserved for future specialization profiles and blueprints.

L2 must not be required by L0.

L2 must not become runtime behavior until a governed L1/L2 integration contract exists.
```

### Checks

Run:

```bash
make seed-boot
make prove-seed
make run
```

---

## 8. Phase 2A — Add the Five L1 Standards

### Goal

Place finalized L1 standards into the repo.

### Tasks

Create:

```bash
mkdir -p L1/standards
```

Copy source files exactly:

```text
AGENT_X_L1_EQC_FIC_v0_6.md
  -> L1/standards/AGENT_X_L1_EQC_FIC.md

AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md
  -> L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW.md

AGENT_X_L1_LIGHTWEIGHT_EQC_SIB_v0_5.md
  -> L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB.md

AGENT_X_L1_LIGHTWEIGHT_EQC_ES_v0_5.md
  -> L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_ES.md

AGENT_X_L1_LIGHTWEIGHT_EQC_v0_5.md
  -> L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC.md
```

### Verification

Run:

```bash
test -s L1/standards/AGENT_X_L1_EQC_FIC.md
test -s L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW.md
test -s L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB.md
test -s L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_ES.md
test -s L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC.md
grep -q "AGENT-X-L1-EQC-FIC-001" L1/standards/AGENT_X_L1_EQC_FIC.md
grep -q "AGENT-X-L1-WORKFLOW-001" L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW.md
grep -q "AGENT_X-L1-SIB-001" L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB.md
grep -q "AGENT-X-L1-EQC-ES-001" L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_ES.md
grep -q "AGENT_X_L1_LIGHTWEIGHT_EQC" L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC.md
make prove-seed
```

If a grep check fails, stop with `SOURCE_STANDARD_CONTENT_MISMATCH`.

### Byte-preservation check

After copying each standard, record source and target byte counts and SHA-256 digests in:

```text
L1/evidence/bootstrap/<UTC_TIMESTAMP>_source_standard_copy_manifest.yaml
```

Minimum record:

```yaml
source_standard_copy_manifest:
  status: "PASS|FAIL"
  items:
    - source: "AGENT_X_L1_EQC_FIC_v0_6.md"
      target: "L1/standards/AGENT_X_L1_EQC_FIC.md"
      source_sha256: "<hex>"
      target_sha256: "<hex>"
      byte_preserved: true
```

If any target digest differs from the source digest, stop with:

```text
STATUS: BLOCKED
Reason: SOURCE_STANDARD_COPY_DRIFT
```

---

## 9. Phase 3A — Create L1 Control Documents

### Goal

Create the minimal non-empty L1 document set.

### Directories

```bash
mkdir -p L1/docs
```

### Required files

```text
L1/docs/00_L1_SYSTEM_GOAL.md
L1/docs/01_L1_BACKGROUND.md
L1/docs/02_L1_ARCHITECTURE_CONTRACT.md
L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md
L1/docs/04_L1_UNIT_DAG.md
L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md
L1/docs/06_L1_VALIDATION_PLAN.md
L1/docs/07_L1_RISK_LEDGER.md
L1/docs/08_L1_TRACEABILITY_MATRIX.md
L1/docs/09_L1_CODING_AGENT_HANDOFF_RULES.md
L1/docs/10_L1_FAILURE_LEARNING_LOG.md
L1/docs/11_L1_REVIEW_GATE.md
```

### `00_L1_SYSTEM_GOAL.md`

```markdown
# L1 System Goal

**Document ID:** `AX-L1-DOC-GOAL-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

L1 is the controlled external evolution layer for Agent_X.

Its purpose is to convert high-level improvement goals into bounded, reviewable, testable implementation units without allowing uncontrolled changes to the L0 governed seed kernel.

L1 reads repository state, plans small changes, produces FIC-governed implementation packets, validates evidence, and records completion results.

L1 does not replace L0, bypass L0 governance, or perform uncontrolled autonomous self-modification.
```

### `01_L1_BACKGROUND.md`

```markdown
# L1 Background

**Document ID:** `AX-L1-DOC-BG-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

Agent_X currently provides a governed L0 seed kernel. L1 exists as an external document-first control plane for planning, FIC generation, validation, evidence capture, and bounded implementation handoff.

L1 is not a runtime replacement for L0. L1 is not an autonomous self-modification loop. L1 is a scaffold for safe external evolution.

## TODO

- Expand background only when additional repository evidence requires it.
```

### `02_L1_ARCHITECTURE_CONTRACT.md`

```markdown
# L1 Architecture Contract

**Document ID:** `AX-L1-DOC-ARCH-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Boundary Rules

- L0 must not import L1 or L2.
- L1 may inspect L0 public contracts and proof outputs.
- L1 must not modify L0 without an explicit L0-impact FIC, proof plan, rollback plan, and review gate.
- L2 is reserved for specialization profiles and blueprints.
- Generated artifacts are validator-owned unless a FIC explicitly authorizes manual maintenance.

## Root Layers

```text
L0 = governed seed kernel
L1 = external evolution/controller layer
L2 = future specialization profiles and blueprints
```
```

### `03_L1_WHOLE_SYSTEM_PSEUDOCODE.md`

```markdown
# L1 Whole-System Pseudocode

**Document ID:** `AX-L1-DOC-PS-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

```text
Procedure L1_EvolveOnce(goal):

1. Load L0 repository state.
2. Load L1 control documents.
3. Verify document authority and freshness.
4. Classify the requested goal.
5. Determine whether the goal affects L0, L1, L2, docs, tests, tooling, or generated artifacts.
6. If the goal is too broad, split it into bounded units.
7. Build or update the unit DAG.
8. Select one implementation unit.
9. Create or update the EQC-FIC document for the selected unit.
10. Validate the FIC against the pre-code gate.
11. If validation fails, return BLOCKED with reasons.
12. Freeze approved inputs in the semantic lockfile.
13. Build a bounded implementation handoff packet.
14. Allow implementation only inside declared permitted files.
15. Run declared checks and proof commands.
16. Collect evidence.
17. Produce completion record.
18. Produce review packet.
19. Update traceability matrix.
20. If implementation failed or drift occurred, update failure-learning log.
21. Return controlled status.
```

Allowed statuses:

```text
READY_FOR_IMPLEMENTATION
BLOCKED
NO_CHANGE
IMPLEMENTED_UNVALIDATED
VALIDATED
IMPLEMENTED_WITH_WAIVERS
REJECTED
```
```

### `04_L1_UNIT_DAG.md`

```markdown
# L1 Unit DAG

**Document ID:** `AX-L1-DOC-DAG-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

| Unit ID | Name | Responsibility | Depends On |
|---|---|---|---|
| `UNIT-L1-001` | Document Loader | Load approved L1 control documents safely and deterministically. | none |
| `UNIT-L1-002` | Repo State Reader | Inspect allowed repository paths and produce repo-state summary. | `UNIT-L1-001` |
| `UNIT-L1-003` | Goal Classifier | Classify requested goal by affected layer and risk. | `UNIT-L1-001`, `UNIT-L1-002` |
| `UNIT-L1-004` | Unit Planner | Convert a goal into bounded implementation units. | `UNIT-L1-003` |
| `UNIT-L1-005` | FIC Generator | Produce or update FIC documents from unit definitions. | `UNIT-L1-004` |
| `UNIT-L1-006` | FIC Validator | Validate FIC readiness before implementation. | `UNIT-L1-005` |
| `UNIT-L1-007` | Handoff Packet Builder | Build bounded implementation packets for coding agents. | `UNIT-L1-006` |
| `UNIT-L1-008` | Proof/Check Runner | Run declared validation commands and capture outputs. | `UNIT-L1-007` |
| `UNIT-L1-009` | Evidence Collector | Normalize and store validation evidence. | `UNIT-L1-008` |
| `UNIT-L1-010` | Completion Record Writer | Produce structured completion records. | `UNIT-L1-009` |
| `UNIT-L1-011` | Traceability Updater | Update requirement-to-code-to-test mappings. | `UNIT-L1-010` |
| `UNIT-L1-012` | Failure-Learning Updater | Record failures and add workflow controls. | `UNIT-L1-010` |

Rules:

- The DAG must remain acyclic.
- One unit must not own another unit's public surface.
- One unit must not write another unit's generated artifacts.
- L0 edits are prohibited unless a separate L0-impact FIC authorizes them.
```

### `05_L1_SHARED_TYPES_AND_INTERFACES.md`

```markdown
# L1 Shared Types and Interfaces

**Document ID:** `AX-L1-DOC-IFACE-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

Initial shared types:

```text
DocumentRecord
RepoStateSummary
GoalClassification
ImplementationUnitPlan
FicDraft
FicValidationResult
SemanticLockfile
HandoffPacket
CheckRunResult
EvidenceRecord
CompletionRecord
ReviewPacket
TraceabilityUpdate
FailureLearningEntry
```

## DocumentRecord

```text
DocumentRecord(path: str, content: str, size_bytes: int, sha256: str, exists: bool = True)
```

Rules:

- Immutable value record.
- `path` is normalized POSIX-style relative path.
- `sha256` is a lowercase 64-character hex digest of raw bytes.
```

### Exact content for remaining docs

Do not leave these files blank. Use the following exact minimal purposes.

#### `06_L1_VALIDATION_PLAN.md`

```markdown
# L1 Validation Plan

**Document ID:** `AX-L1-DOC-VAL-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Purpose

This document defines the initial validation gates for L1 scaffold work.

## Required Checks

- `make seed-boot`
- `make prove-seed`
- `make run`
- source-standard byte-preservation check
- ES cross-check evidence
- SIB cross-check evidence
- EQC cross-check evidence
- bootstrap artifact manifest existence check

## TODO

- Replace bootstrap checks with executable validators after the first L1 validator exists.
```

#### `07_L1_RISK_LEDGER.md`

```markdown
# L1 Risk Ledger

**Document ID:** `AX-L1-DOC-RISK-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Purpose

This document records known L1 scaffold risks.

## Current Risks

| Risk ID | Description | Severity | Status |
|---|---|---:|---|
| `RISK-L1-001` | Bootstrap sidecars are placeholders and are not release evidence. | medium | open |
| `RISK-L1-002` | Executable ES/SIB/EQC validators do not exist yet. | medium | open |

## Rule

Open risks must be listed in the final response and must not be hidden by a `VALIDATED` scaffold status.
```

#### `08_L1_TRACEABILITY_MATRIX.md`

```markdown
# L1 Traceability Matrix

**Document ID:** `AX-L1-DOC-TRACE-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

| Goal ID | Pseudocode ID | Unit ID | FIC ID | Target File | Test File | Status |
|---|---|---|---|---|---|---|
| `GOAL-L1-001` | `PS-L1-001` | `UNIT-L1-001` | `FIC-L1-001` | `L1/controller/document_loader.py` | `L1/tests/test_document_loader.py` | `ready-for-code` |

## Rule

No implementation behavior may be accepted without an owning FIC row.
```

#### `09_L1_CODING_AGENT_HANDOFF_RULES.md`

```markdown
# L1 Coding Agent Handoff Rules

**Document ID:** `AX-L1-DOC-HANDOFF-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Purpose

This document defines the default handoff rules for coding agents.

## Rules

- Implement only the selected FIC unit.
- Do not edit outside permitted files.
- Do not edit L0 unless an explicit L0-impact FIC authorizes it.
- Stop with `BLOCKED` when required context is missing.
- Produce completion evidence for every implementation attempt.
```

#### `10_L1_FAILURE_LEARNING_LOG.md`

```markdown
# L1 Failure-Learning Log

**Document ID:** `AX-L1-DOC-FAIL-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Purpose

This document records failures and the control improvements added to prevent recurrence.

## Entries

No implementation failures recorded yet.
```

#### `11_L1_REVIEW_GATE.md`

```markdown
# L1 Review Gate

**Document ID:** `AX-L1-DOC-REVIEW-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Purpose

This document defines the initial review gate for L1 scaffold and implementation work.

## Review Rules

- Scaffold validation is not release validation.
- Placeholder generated files are not release evidence.
- `VALIDATED` may be used for Mode A only when all Mode A checks pass.
- Implementation acceptance requires a completion record and review packet.
```

---

## 10. Phase 4A — Create L1 FIC Registry and FIC Files

### Directories

```bash
mkdir -p L1/fic/units
```

### `L1/fic/index.fic.yaml`

Create:

```yaml
fic_registry_version: "v1.0"
portfolio_id: "AGENT_X_L1"
files:
  - fic_id: "FIC-L1-001"
    unit_id: "UNIT-L1-001"
    fic_path: "L1/fic/units/FIC-L1-001-document-loader.md"
    target_file: "L1/controller/document_loader.py"
    status: "ready-for-code"
    version: "v0.6.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
    permitted_files:
      - "L1/controller/document_loader.py"
      - "L1/tests/test_document_loader.py"
  - fic_id: "FIC-L1-002"
    unit_id: "UNIT-L1-002"
    fic_path: "L1/fic/units/FIC-L1-002-repo-state-reader.md"
    target_file: "L1/controller/repo_state_reader.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-003"
    unit_id: "UNIT-L1-003"
    fic_path: "L1/fic/units/FIC-L1-003-goal-classifier.md"
    target_file: "L1/controller/goal_classifier.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-004"
    unit_id: "UNIT-L1-004"
    fic_path: "L1/fic/units/FIC-L1-004-unit-planner.md"
    target_file: "L1/controller/unit_planner.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-005"
    unit_id: "UNIT-L1-005"
    fic_path: "L1/fic/units/FIC-L1-005-fic-generator.md"
    target_file: "L1/controller/fic_generator.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-006"
    unit_id: "UNIT-L1-006"
    fic_path: "L1/fic/units/FIC-L1-006-fic-validator.md"
    target_file: "L1/controller/fic_validator.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-007"
    unit_id: "UNIT-L1-007"
    fic_path: "L1/fic/units/FIC-L1-007-handoff-packet-builder.md"
    target_file: "L1/controller/handoff_packet_builder.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-008"
    unit_id: "UNIT-L1-008"
    fic_path: "L1/fic/units/FIC-L1-008-proof-check-runner.md"
    target_file: "L1/controller/proof_check_runner.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-009"
    unit_id: "UNIT-L1-009"
    fic_path: "L1/fic/units/FIC-L1-009-evidence-collector.md"
    target_file: "L1/controller/evidence_collector.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-010"
    unit_id: "UNIT-L1-010"
    fic_path: "L1/fic/units/FIC-L1-010-completion-record-writer.md"
    target_file: "L1/controller/completion_record_writer.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-011"
    unit_id: "UNIT-L1-011"
    fic_path: "L1/fic/units/FIC-L1-011-traceability-updater.md"
    target_file: "L1/controller/traceability_updater.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
  - fic_id: "FIC-L1-012"
    unit_id: "UNIT-L1-012"
    fic_path: "L1/fic/units/FIC-L1-012-failure-learning-updater.md"
    target_file: "L1/controller/failure_learning_updater.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
```

### Create `FIC-L1-001-document-loader.md`

Extract the full first concrete FIC from the standard file. Do not manually summarize the FIC. Use this exact script from the repository root:

```bash
python - <<'PY_FIC_EXTRACT'
from pathlib import Path
src = Path('L1/standards/AGENT_X_L1_EQC_FIC.md')
dst = Path('L1/fic/units/FIC-L1-001-document-loader.md')
text = src.read_text(encoding='utf-8')
start_marker = '# FIC-L1-001: L1 Document Loader'
start = text.find(start_marker)
if start < 0:
    raise SystemExit('FIC-L1-001 heading not found in EQC-FIC standard')
end = text.find('\n# FIC-L1-002', start + len(start_marker))
if end < 0:
    end = len(text)
content = text[start:end].strip() + '\n'
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(content, encoding='utf-8', newline='\n')
print(f'wrote {dst} with {len(content)} chars')
PY_FIC_EXTRACT
```

Do not shorten the FIC.

Do not rewrite the FIC.

### Create placeholder FICs 002–012

For each draft FIC file, use:

```markdown
# FIC-L1-00X: <Name>

**fic_id:** `FIC-L1-00X`  
**unit_id:** `UNIT-L1-00X`  
**version:** `v0.1.0`  
**status:** `draft`  
**target_file:** `L1/controller/<name>.py`

Draft placeholder. Not ready for coding.
```

### Verification

```bash
test -s L1/fic/index.fic.yaml
test -s L1/fic/units/FIC-L1-001-document-loader.md
grep -q "FIC-L1-001: L1 Document Loader" L1/fic/units/FIC-L1-001-document-loader.md
grep -q 'status: "ready-for-code"' L1/fic/index.fic.yaml
make prove-seed
```

---

## 11. Phase 5A — Create ES Sidecars

### Directories

```bash
mkdir -p L1/ecosystem/ecosystem-schemas
```

### Files

```text
L1/ecosystem/ecosystem-registry.yaml
L1/ecosystem/ecosystem-graph.yaml
L1/ecosystem/ecosystem-validation-log.md
L1/ecosystem/ecosystem-error-codes.yaml
L1/ecosystem/ecosystem-schemas/.gitkeep
```

### `ecosystem-registry.yaml`

Create a registry containing at least these documents:

```text
AX-L1-DOC-GOAL-001
AX-L1-DOC-BG-001
AX-L1-DOC-ARCH-001
AX-L1-DOC-PS-001
AX-L1-DOC-DAG-001
AX-L1-DOC-IFACE-001
AX-L1-DOC-VAL-001
AX-L1-DOC-RISK-001
AX-L1-DOC-TRACE-001
AX-L1-DOC-HANDOFF-001
AX-L1-DOC-FAIL-001
AX-L1-DOC-REVIEW-001
AX-L1-DOC-FICREG-001
AX-L1-DOC-FIC-001
AX-L1-DOC-STD-FIC-001
AX-L1-DOC-STD-WORKFLOW-001
AX-L1-DOC-STD-SIB-001
AX-L1-DOC-STD-ES-001
AX-L1-DOC-STD-EQC-001
```

Use this row shape:

```yaml
ecosystem_registry_version: "v0.5"
portfolio_id: "AGENT_X_L1"
documents:
  - doc_id: "AX-L1-DOC-GOAL-001"
    title: "L1 System Goal"
    type: "system-goal"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    version: "v0.1.0"
    status: "active"
    owner: "l1-control-plane"
    layer: 0
    authority_level: "constitutional"
    functional_digest: "sha256:<pending>"
    metadata_digest: "sha256:<pending>"
    depends_on: []
    recognized_by: []
    governs:
      - "AX-L1-DOC-ARCH-001"
      - "AX-L1-DOC-PS-001"
    allow_empty: false
    generated_from: null
    last_validated_utc: null
    source_of_truth_owner: "AX-L1-DOC-GOAL-001"
```

Do not leave registered paths missing.

### `ecosystem-graph.yaml`

Every registry document must appear as a node.

Minimum graph rules:

```yaml
ecosystem_graph_version: "v0.5"
portfolio_id: "AGENT_X_L1"
root_doc_id: "AX-L1-DOC-GOAL-001"
nodes:
  - doc_id: "AX-L1-DOC-GOAL-001"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    type: "system-goal"
    layer: 0
edges:
  - src: "AX-L1-DOC-GOAL-001"
    type: "GOVERNS"
    dst: "AX-L1-DOC-ARCH-001"
    payload: {}
```

Add nodes for all registry entries.

Add enough `GOVERNS` or `USES` edges so active documents are reachable from `AX-L1-DOC-GOAL-001`.

### `ecosystem-error-codes.yaml`

Include at least:

```yaml
error_codes:
  AX_ES_PATH_NOT_FOUND: "Registered document path does not exist."
  AX_ES_EMPTY_DOCUMENT: "Registered document is empty and not marked AllowEmpty."
  AX_ES_MISSING_VERSION_MARKER: "Document does not declare matching version marker."
  AX_ES_DUPLICATE_DOC_ID: "Two registry entries use the same DocID."
  AX_ES_DUPLICATE_PATH: "Two active documents use the same path."
  AX_ES_CYCLE_DETECTED: "Functional dependency graph contains a cycle."
  AX_ES_ORPHAN_DOCUMENT: "Active document is not reachable from root."
  AX_ES_STALE_DOCUMENT: "Document depends on a changed dependency and was not revalidated."
```

### ES cross-check evidence file

Record ES registry/graph checks in:

```text
L1/evidence/bootstrap/<UTC_TIMESTAMP>_es_cross_checks.yaml
```

Minimum checks:

```yaml
es_cross_checks:
  status: "PASS|FAIL"
  checks:
    - id: "ES-CHECK-001"
      description: "every registry path exists and is non-empty"
      result: "PASS|FAIL"
    - id: "ES-CHECK-002"
      description: "every graph node exists in registry"
      result: "PASS|FAIL"
    - id: "ES-CHECK-003"
      description: "every graph edge src/dst exists as a graph node"
      result: "PASS|FAIL"
    - id: "ES-CHECK-004"
      description: "all active documents are reachable from AX-L1-DOC-GOAL-001 by functional edges"
      result: "PASS|FAIL"
    - id: "ES-CHECK-005"
      description: "no registered path points outside L1/ except allowed root README/L0 placeholder references"
      result: "PASS|FAIL"
```

If any ES cross-check fails, stop with `BLOCKED_ES_CROSS_CHECK_FAIL`.

---

## 12. Phase 6A — Create SIB Sidecars

### Directories

```bash
mkdir -p L1/sib/sib-schemas
```

### Files

```text
L1/sib/sib-registry.yaml
L1/sib/sib-doc-registry.yaml
L1/sib/sib-bindings.yaml
L1/sib/sib-graph.yaml
L1/sib/sib-validation-log.md
L1/sib/sib-error-codes.yaml
L1/sib/sib-waivers.yaml
L1/sib/sib-schemas/.gitkeep
```

### `sib-registry.yaml`

Create:

```yaml
sib_registry_version: "v0.5"
portfolio_id: "AGENT_X_L1"
artifacts:
  - art_id: "ART-L1-001"
    global_art_id: "AGENT_X_L1::ART-L1-001"
    title: "L1 document loader"
    type: "implementation"
    layer: "L1"
    file_path: "L1/controller/document_loader.py"
    version: "v0.1.0"
    status: "planned"
    owner: "l1-controller"
    governed_by_fic: "AGENT_X_L1::FIC-L1-001"
    implements_unit: "AGENT_X_L1::UNIT-L1-001"
    canonicalization_tier: "T1"
    functional_digest: null
    public_surface_digest: null
    metadata_digest: null
    functional_state_digest: null
    tests:
      - "AGENT_X_L1::TEST-L1-001"
    completion_records: []
    review_packets: []
    public_surface:
      - "DEFAULT_MAX_DOCUMENT_BYTES"
      - "DocumentRecord"
      - "DocumentLoaderError"
      - "DocumentRootError"
      - "DocumentPathError"
      - "DocumentLoadError"
      - "load_document"
      - "load_documents"
    declared_dependencies:
      strict:
        - "python:dataclasses"
        - "python:pathlib"
        - "python:hashlib"
        - "python:typing"
      optional: []
      dynamic_patterns: []
```

### `sib-doc-registry.yaml`

Create at least:

```yaml
sib_doc_registry_version: "v0.5"
portfolio_id: "AGENT_X_L1"
objects:
  - object_id: "GOAL-L1-001"
    global_id: "AGENT_X_L1::GOAL-L1-001"
    object_type: "goal"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    version: "v0.1.0"
    status: "active"
    owner: "l1-control-plane"
    functional_digest: null
    metadata_digest: null
  - object_id: "UNIT-L1-001"
    global_id: "AGENT_X_L1::UNIT-L1-001"
    object_type: "pseudocode-unit"
    path: "L1/docs/04_L1_UNIT_DAG.md#UNIT-L1-001"
    version: "v0.1.0"
    status: "active"
    owner: "l1-control-plane"
    functional_digest: null
    metadata_digest: null
  - object_id: "FIC-L1-001"
    global_id: "AGENT_X_L1::FIC-L1-001"
    object_type: "fic-document"
    path: "L1/fic/units/FIC-L1-001-document-loader.md"
    version: "v0.6.0"
    status: "ready-for-code"
    owner: "l1-control-plane"
    functional_digest: null
    metadata_digest: null
```

### `sib-bindings.yaml`

Create:

```yaml
sib_bindings_version: "v0.5"
portfolio_id: "AGENT_X_L1"
bindings:
  - binding_id: "BIND-L1-001"
    unit_id: "AGENT_X_L1::UNIT-L1-001"
    goal_refs:
      - "AGENT_X_L1::GOAL-L1-001"
    pseudocode_refs:
      - "AGENT_X_L1::PS-L1-001"
    fic_id: "AGENT_X_L1::FIC-L1-001"
    implementation_artifacts:
      - "AGENT_X_L1::ART-L1-001"
    test_artifacts:
      - "AGENT_X_L1::TEST-L1-001"
    evidence_artifacts: []
    binding_strength: "HARD"
    minimum_status_for_acceptance: "validated"
    minimum_equivalence: "E1"
```

### `sib-graph.yaml`

Create:

```yaml
sib_graph_version: "v0.5"
portfolio_id: "AGENT_X_L1"
nodes:
  - id: "AGENT_X_L1::ART-L1-001"
    kind: "implementation"
    layer: "L1"
    status: "planned"
  - id: "AGENT_X_L1::FIC-L1-001"
    kind: "fic-document"
    layer: "L1"
    status: "ready-for-code"
  - id: "AGENT_X_L1::TEST-L1-001"
    kind: "test"
    layer: "L1"
    status: "planned"
edges:
  - src: "AGENT_X_L1::ART-L1-001"
    type: "IMPLEMENTS"
    dst: "AGENT_X_L1::FIC-L1-001"
  - src: "AGENT_X_L1::TEST-L1-001"
    type: "VALIDATES"
    dst: "AGENT_X_L1::ART-L1-001"
```

### `sib-error-codes.yaml`

Create:

```yaml
error_codes:
  - code: "SIB_MISSING_PRIMARY_BINDING"
    severity: "error"
    message: "Artifact has no primary HARD FIC binding."
    blocking: true
  - code: "SIB_PATH_ESCAPES_ROOT"
    severity: "error"
    message: "Artifact path escapes repository root."
    blocking: true
  - code: "SIB_PUBLIC_SURFACE_MISMATCH"
    severity: "error"
    message: "Implementation public surface does not match governing FIC."
    blocking: true
```

### `sib-waivers.yaml`

Create:

```yaml
waivers: []
```

### SIB cross-checks

Before leaving Phase 6A, confirm:

```text
[ ] every binding unit_id exists in sib-doc-registry.yaml
[ ] every binding fic_id exists in sib-doc-registry.yaml
[ ] every binding implementation artifact exists in sib-registry.yaml
[ ] every graph node exists in registry or doc-registry
[ ] every graph edge src/dst exists as a node
[ ] ART-L1-001 public surface matches FIC-L1-001 public surface
```

### SIB cross-check evidence file

Record the SIB cross-check results in:

```text
L1/evidence/bootstrap/<UTC_TIMESTAMP>_sib_cross_checks.yaml
```

Use this shape:

```yaml
sib_cross_checks:
  status: "PASS|FAIL"
  checks:
    - id: "SIB-CHECK-001"
      description: "every binding unit_id exists in sib-doc-registry.yaml"
      result: "PASS|FAIL"
    - id: "SIB-CHECK-002"
      description: "every binding fic_id exists in sib-doc-registry.yaml"
      result: "PASS|FAIL"
    - id: "SIB-CHECK-003"
      description: "every binding implementation artifact exists in sib-registry.yaml"
      result: "PASS|FAIL"
    - id: "SIB-CHECK-004"
      description: "every graph node exists in registry or doc-registry"
      result: "PASS|FAIL"
    - id: "SIB-CHECK-005"
      description: "every graph edge src/dst exists as a node"
      result: "PASS|FAIL"
    - id: "SIB-CHECK-006"
      description: "ART-L1-001 public surface matches FIC-L1-001"
      result: "PASS|FAIL"
```

If any SIB cross-check fails, stop with `BLOCKED_SIB_CROSS_CHECK_FAIL`.

---

## 13. Phase 7A — Create EQC Sidecars

### Directories

```bash
mkdir -p L1/eqc/manifests L1/eqc/procedures L1/eqc/operators L1/eqc/traces L1/eqc/tests L1/eqc/schemas
```

### Required files

```text
L1/eqc/manifests/l1-eqc-manifest.yaml
L1/eqc/procedures/L1_EvolveOnce.eqc.md
L1/eqc/procedures/L1_ValidateFICBundle.eqc.md
L1/eqc/operators/classify_goal.eqc.md
L1/eqc/operators/decide_readiness.eqc.md
L1/eqc/traces/l1-validation-trace.schema.yaml
L1/eqc/tests/goal-classifier.test-vectors.yaml
L1/eqc/schemas/.gitkeep
```

### `l1-eqc-manifest.yaml`

```yaml
l1_eqc_manifest:
  manifest_version: "v0.5"
  portfolio_id: "AGENT_X_L1"
  procedures:
    - procedure_id: "EQC-PROC-L1-EVOLVE-ONCE"
      path: "L1/eqc/procedures/L1_EvolveOnce.eqc.md"
      version: "v0.1.0"
      operators:
        - "L1.ClassifyGoal_v1"
        - "L1.DecideReadiness_v1"
    - procedure_id: "EQC-PROC-L1-VALIDATE-FIC-BUNDLE"
      path: "L1/eqc/procedures/L1_ValidateFICBundle.eqc.md"
      version: "v0.1.0"
      operators:
        - "L1.DecideReadiness_v1"
  operators:
    - name: "L1.ClassifyGoal_v1"
      path: "L1/eqc/operators/classify_goal.eqc.md"
      version: "v0.1.0"
      category: "classification"
      purity: "pure"
    - name: "L1.DecideReadiness_v1"
      path: "L1/eqc/operators/decide_readiness.eqc.md"
      version: "v0.1.0"
      category: "readiness"
      purity: "pure"
```

### Placeholder EQC procedure/operator files

Each Markdown EQC file must contain:

```markdown
# <Title>

Spec Version: AGENT_X_L1_LIGHTWEIGHT_EQC-v0.5.0

```yaml
eqc_header:
  eqc_schema: "agent-x-l1-lightweight-eqc/v0.5"
  doc_id: "EQC-L1-PLACEHOLDER"
  title: "<Title>"
  artifact_type: "procedure-spec"
  version: "v0.1.0"
  status: "draft"
  layer: "L1"
  owner: "Agent_X L1"
  governed_unit_ids: []
  related_fic_ids: []
  related_sib_art_ids: []
  related_es_doc_ids: []
  last_updated_utc: "1970-01-01T00:00:00Z"
```

Bootstrap placeholder. Not release evidence.
```

For operator files, set `artifact_type: "operator-spec"`.

### EQC cross-checks

Before leaving Phase 7A, confirm:

```text
[ ] every manifest procedure path exists
[ ] every manifest operator path exists
[ ] every EQC Markdown file has the Spec Version marker
[ ] every placeholder says Not release evidence
```

### EQC cross-check evidence file

Record EQC checks in:

```text
L1/evidence/bootstrap/<UTC_TIMESTAMP>_eqc_cross_checks.yaml
```

Use this shape:

```yaml
eqc_cross_checks:
  status: "PASS|FAIL"
  checks:
    - id: "EQC-CHECK-001"
      description: "every manifest procedure path exists"
      result: "PASS|FAIL"
    - id: "EQC-CHECK-002"
      description: "every manifest operator path exists"
      result: "PASS|FAIL"
    - id: "EQC-CHECK-003"
      description: "every EQC Markdown file has the Spec Version marker"
      result: "PASS|FAIL"
    - id: "EQC-CHECK-004"
      description: "every placeholder says Not release evidence"
      result: "PASS|FAIL"
```

If any EQC cross-check fails, stop with `BLOCKED_EQC_CROSS_CHECK_FAIL`.

---

## 14. Phase 8A — Create Generated Placeholders

### Directories

```bash
mkdir -p L1/generated L1/evidence
```

### Files

```text
L1/generated/fic_bundle_manifest.yaml
L1/generated/unit_dag.yaml
L1/generated/semantic_lockfile.yaml
L1/generated/requirement_coverage_matrix.yaml
L1/generated/readiness_report.md
L1/generated/validation_report.md
L1/generated/review_packet.md
L1/generated/release_candidate_report.md
L1/evidence/.gitkeep
```

### YAML placeholder header

Use:

```yaml
generated_from: "manual-bootstrap@v1.4.0"
status: "placeholder-not-release-evidence"
release_evidence: false
```

### Markdown placeholder header

Use:

```markdown
# <Report Name>

**Generated-From:** `manual-bootstrap@v1.4.0`  
**Status:** `placeholder-not-release-evidence`  
**Release Evidence:** `false`

This file is a bootstrap placeholder. It must be regenerated by a validator before release-candidate status.
```

### Checks

Run:

```bash
find L1 -type f -size 0 -print
make seed-boot
make prove-seed
make run
git status --short
git diff --stat
```

If `find` prints files other than intentional `.gitkeep`, fix them.

Generated placeholders are not release evidence.

---

## 14.5 Phase 8B — Create Bootstrap Artifact Manifest

### Goal

Create one machine-readable manifest listing the files created by Mode A. This helps a weaker coding model prove what it changed without relying on prose.

Create:

```text
L1/generated/bootstrap_artifact_manifest.yaml
```

Minimum content:

```yaml
bootstrap_artifact_manifest_version: "v1.4.0"
status: "mode-a-bootstrap-not-release-evidence"
release_evidence: false
created_by: "manual-bootstrap@v1.4.0"
mode: "Mode A safe additive scaffold"
required_checks_recorded: true
artifacts:
  standards:
    - "L1/standards/AGENT_X_L1_EQC_FIC.md"
    - "L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW.md"
    - "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB.md"
    - "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_ES.md"
    - "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC.md"
  control_docs:
    - "L1/docs/00_L1_SYSTEM_GOAL.md"
    - "L1/docs/01_L1_BACKGROUND.md"
    - "L1/docs/02_L1_ARCHITECTURE_CONTRACT.md"
    - "L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md"
    - "L1/docs/04_L1_UNIT_DAG.md"
    - "L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md"
    - "L1/docs/06_L1_VALIDATION_PLAN.md"
    - "L1/docs/07_L1_RISK_LEDGER.md"
    - "L1/docs/08_L1_TRACEABILITY_MATRIX.md"
    - "L1/docs/09_L1_CODING_AGENT_HANDOFF_RULES.md"
    - "L1/docs/10_L1_FAILURE_LEARNING_LOG.md"
    - "L1/docs/11_L1_REVIEW_GATE.md"
  fic:
    - "L1/fic/index.fic.yaml"
    - "L1/fic/units/FIC-L1-001-document-loader.md"
  ecosystem:
    - "L1/ecosystem/ecosystem-registry.yaml"
    - "L1/ecosystem/ecosystem-graph.yaml"
  sib:
    - "L1/sib/sib-registry.yaml"
    - "L1/sib/sib-bindings.yaml"
    - "L1/sib/sib-graph.yaml"
  eqc:
    - "L1/eqc/manifests/l1-eqc-manifest.yaml"
  generated_placeholders:
    - "L1/generated/semantic_lockfile.yaml"
    - "L1/generated/validation_report.md"
    - "L1/generated/readiness_report.md"
validation_note: "This manifest records scaffold artifacts only. It is not release evidence."
```

### Required check

Run:

```bash
test -s L1/generated/bootstrap_artifact_manifest.yaml
grep -q 'mode-a-bootstrap-not-release-evidence' L1/generated/bootstrap_artifact_manifest.yaml
```

---

## 14.6 Phase 8C — Create and Run Mode A Bootstrap Validator

Create:

```text
L1/generated/bootstrap_validate_mode_a.py
```

Minimum behavior:

```text
- check required standards exist and are non-empty;
- check required L1 docs exist and are non-empty;
- check FIC registry exists;
- check FIC-L1-001 exists and contains `FIC-L1-001: L1 Document Loader`;
- check ES/SIB/EQC sidecar files exist;
- check generated placeholders contain `placeholder-not-release-evidence` where applicable;
- check bootstrap artifact manifest exists;
- check README does not claim Mode B migration or Phase 9 implementation unless those phases ran.
```

Use only Python standard library.

Run:

```bash
python L1/generated/bootstrap_validate_mode_a.py | tee "L1/evidence/bootstrap/${BOOTSTRAP_TS}_mode_a_bootstrap_validator.log"
```

If the script exits nonzero, stop with:

```text
STATUS: BLOCKED
Reason: MODE_A_BOOTSTRAP_VALIDATOR_FAIL
```

The script itself is bootstrap evidence only. It is not a future release validator.

---

## 14.7 Phase 8D — Final Validation Evidence Bundle

Create:

```text
L1/evidence/bootstrap/<UTC_TIMESTAMP>_final_validation_bundle.yaml
```

Minimum content:

```yaml
final_validation_bundle:
  version: "v1.4.0"
  mode: "Mode A safe additive scaffold"
  release_evidence: false
  baseline_log: "runtime_artifacts/l1_baseline_checks.log"
  source_standard_copy_manifest: "L1/evidence/bootstrap/<UTC_TIMESTAMP>_source_standard_copy_manifest.yaml"
  es_cross_checks: "L1/evidence/bootstrap/<UTC_TIMESTAMP>_es_cross_checks.yaml"
  sib_cross_checks: "L1/evidence/bootstrap/<UTC_TIMESTAMP>_sib_cross_checks.yaml"
  eqc_cross_checks: "L1/evidence/bootstrap/<UTC_TIMESTAMP>_eqc_cross_checks.yaml"
  bootstrap_validator_log: "L1/evidence/bootstrap/<UTC_TIMESTAMP>_mode_a_bootstrap_validator.log"
  bootstrap_artifact_manifest: "L1/generated/bootstrap_artifact_manifest.yaml"
  git_status_short: "captured in final response or evidence log"
  git_diff_stat: "captured in final response or evidence log"
  decision: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
```

This bundle prevents the final answer from being disconnected from the evidence files.

---

# MODE B — OPTIONAL L0 FOLDER MIGRATION

---

## 15. Phase 2B — Move Existing L0 Files Under `L0/`

Run this phase only if all are true:

```text
[ ] Phase 0 passed.
[ ] Mode A scaffold passed.
[ ] git status is understood.
[ ] The user wants the final root-visible L0 layout now.
[ ] You can run all L0 proof commands after the move.
```

### Pre-move safety

Run:

```bash
git status --short
make seed-boot
make prove-seed
make run
```

If `git status --short` shows unrelated uncommitted changes, stop unless those changes are your current scaffold changes and are expected.

### Directories

```bash
mkdir -p L0/manifests L0/docs L0/tests
```

### Use `git mv` when possible

Move:

```bash
git mv CODE L0/CODE
git mv scripts L0/scripts
mkdir -p L0/tests
git mv tests/seed_l0 L0/tests/seed_l0

git mv CAPABILITY_MANIFEST.yaml L0/manifests/CAPABILITY_MANIFEST.yaml
git mv SEED_INVARIANTS.yaml L0/manifests/SEED_INVARIANTS.yaml
git mv SEED_PACKAGE_MANIFEST.yaml L0/manifests/SEED_PACKAGE_MANIFEST.yaml

git mv SEED_ACCEPTANCE.md L0/docs/SEED_ACCEPTANCE.md
git mv PUBLIC_CONTRACT_POLICY.md L0/docs/PUBLIC_CONTRACT_POLICY.md
git mv EXTENSION_ABI.md L0/docs/EXTENSION_ABI.md
```

Move external evolution acceptance to L1:

```bash
git mv EVOLUTION_ACCEPTANCE.md L1/docs/EVOLUTION_ACCEPTANCE.md
```

If `git mv` fails because the file already moved, inspect before continuing. Do not duplicate.

### Handle examples/extensions

If the repo contains:

```text
examples/extensions/
```

then preserve it. Do not delete it.

Preferred current-stage handling:

```text
Keep examples/extensions/ at root unless a later FIC moves it.
```

Do not move examples/extensions into L0 unless tests or README prove it belongs to L0.

### Update Makefile paths

Preserve root command names:

```bash
make install
make seed-boot
make prove-seed
make run
make clean
```

Expected path updates:

```makefile
seed-boot:
	python -m compileall L0/CODE

prove-seed:
	pytest L0/tests/seed_l0

run:
	python L0/CODE/main.py
```

If the actual entrypoint differs, inspect existing Makefile and update only paths.

### Update path references

Search:

```bash
grep -R "CODE" -n README.md Makefile pyproject.toml L0 L1 tests . 2>/dev/null | head -200
grep -R "tests/seed_l0" -n README.md Makefile pyproject.toml L0 L1 . 2>/dev/null | head -200
grep -R "CAPABILITY_MANIFEST.yaml" -n README.md Makefile pyproject.toml L0 L1 . 2>/dev/null | head -200
grep -R "SEED_INVARIANTS.yaml" -n README.md Makefile pyproject.toml L0 L1 . 2>/dev/null | head -200
```

Update only references that are broken by the move.

### Required checks

Run:

```bash
python -m compileall L0/CODE
pytest L0/tests/seed_l0 -q
make seed-boot
make prove-seed
make run
```

### Stop condition

If a check fails, fix path references only.

Do not change L0 semantics.

If you cannot fix path references without semantic edits:

```text
STATUS: BLOCKED
Reason: L0_MIGRATION_PATH_BREAK
```

---

## 16. Phase 9 — Optional First Implementation Slice: UNIT-L1-001

Do this only if Phases 0–8A pass and the user explicitly allows implementation beyond scaffold.

If Mode B was performed, Phase 2B checks must also pass.

### Goal

Implement:

```text
UNIT-L1-001 Document Loader
```

### Permitted files

Only these files may be created or modified:

```text
L1/controller/__init__.py
L1/controller/document_loader.py
L1/tests/__init__.py
L1/tests/test_document_loader.py
L1/evidence/FIC-L1-001/<UTC_TIMESTAMP>_completion_record.yaml
L1/evidence/FIC-L1-001/<UTC_TIMESTAMP>_review_packet.md
```

Do not edit other files during Phase 9.

### Required public surface

`L1/controller/document_loader.py` must expose exactly:

```text
DEFAULT_MAX_DOCUMENT_BYTES
DocumentRecord
DocumentLoaderError
DocumentRootError
DocumentPathError
DocumentLoadError
load_document
load_documents
```

It must define `__all__` exactly matching that list.

### Required behavior

Implement exactly what `L1/fic/units/FIC-L1-001-document-loader.md` says.

Key requirements:

```text
- root must be str or pathlib.Path
- root must exist and resolve to a directory
- root symlink to a directory is allowed after resolution
- path must be relative
- absolute paths are rejected
- path traversal is rejected
- symlink escape is rejected
- file must exist
- file must be regular
- raw bytes must not exceed max_bytes
- max_bytes must be int >= 0
- bool max_bytes is invalid
- max_bytes=0 allows only empty files
- bytes must decode as UTF-8
- sha256 is computed from raw bytes
- DocumentRecord is frozen/immutable
- load_documents preserves input order and multiplicity
- duplicate paths produce duplicate records
- failure in load_documents raises and returns no partial result
- no network
- no shell
- no L0 import
- no L2 import
- no hidden mutable global state
```

### Required tests

Create tests for all of these:

```text
valid document load
returned relative POSIX path
sha256 computed from raw bytes
DocumentRecord immutability
missing root
root is file
root as pathlib.Path
root symlink allowed if it resolves to directory
negative max_bytes
bool max_bytes rejected
max_bytes=0 with empty file succeeds
max_bytes=0 with non-empty file fails
non-string path
empty path
absolute path
path traversal
symlink escape
missing file
directory path instead of file
oversized file
invalid UTF-8
load_documents preserves order
load_documents preserves duplicates
load_documents rejects non-list input
load_documents fails on one bad path without partial return
no forbidden imports
__all__ matches expected public surface
```

### Required checks

Run:

```bash
python -m compileall L1/controller
pytest L1/tests/test_document_loader.py -q
make seed-boot
make prove-seed
make run
```

### Completion record

Create:

```text
L1/evidence/FIC-L1-001/<UTC_TIMESTAMP>_completion_record.yaml
```

Minimum content:

```yaml
completion_record:
  status: "VALIDATED"
  unit_id: "UNIT-L1-001"
  fic_id: "FIC-L1-001"
  fic_version: "v0.6.0"
  target_file: "L1/controller/document_loader.py"
  files_inspected:
    - "L1/fic/units/FIC-L1-001-document-loader.md"
  files_changed:
    - "L1/controller/document_loader.py"
    - "L1/tests/test_document_loader.py"
  tests_created_or_updated:
    - "L1/tests/test_document_loader.py"
  checks_run:
    - command: "python -m compileall L1/controller"
      result: "pass"
    - command: "pytest L1/tests/test_document_loader.py -q"
      result: "pass"
    - command: "make seed-boot"
      result: "pass"
    - command: "make prove-seed"
      result: "pass"
    - command: "make run"
      result: "pass"
  checks_not_run: []
  semantic_diff:
    behavior_added:
      - "Added L1 document-loading utility governed by FIC-L1-001."
    behavior_removed: []
    behavior_changed: []
    behavior_preserved:
      - "L0 proof commands preserved."
    public_surface_added:
      - "DEFAULT_MAX_DOCUMENT_BYTES"
      - "DocumentRecord"
      - "DocumentLoaderError"
      - "DocumentRootError"
      - "DocumentPathError"
      - "DocumentLoadError"
      - "load_document"
      - "load_documents"
    public_surface_removed: []
    public_surface_changed: []
    dependency_changes:
      - "Added stdlib-only L1 imports: dataclasses, pathlib, hashlib, typing."
    compatibility_impact: "backward_compatible"
  deviations_from_fic: []
  unresolved_unknowns: []
  residual_risks: []
  waivers_used: []
```

If any required check is not run or fails, do not set status to `VALIDATED`.

### Review packet

Create:

```text
L1/evidence/FIC-L1-001/<UTC_TIMESTAMP>_review_packet.md
```

Minimum content:

```markdown
# Review Packet — FIC-L1-001 Document Loader

**Review ID:** `REV-L1-001`  
**Unit ID:** `UNIT-L1-001`  
**FIC ID:** `FIC-L1-001`  
**Decision:** `accepted` only if all required checks passed.

## Files Changed

- `L1/controller/document_loader.py`
- `L1/tests/test_document_loader.py`

## Public Surface Diff

Added exactly the public surface declared by FIC-L1-001. No extra public surface accepted.

## Dependency Diff

Stdlib-only dependencies: `dataclasses`, `hashlib`, `pathlib`, `typing`.

## L0 Impact

No L0 behavior change. L0 proof commands rerun.

## Checks

List each command and result.

## Residual Risks

None, unless a required check was not run.
```

---

## 17. Phase 10 — Root README Update

### Goal

Update root README to explain visible layers. Do this after Mode A scaffold exists.

### Add near top

```markdown
## Layer Layout

Agent_X is organized into visible layers:

- `L0/` — governed seed kernel and proof suite.
- `L1/` — external evolution/controller control plane and implementation workflow.
- `L2/` — future specialization profiles and blueprints.

L0 remains independently runnable and proofable. L1 may inspect L0 contracts and proof results, but L0 must not import or depend on L1 or L2.
```

If Mode A was used and L0 files remain at historical root paths, add this clarification:

```markdown
The current repository may still retain some L0 files at historical root paths until the explicit L0 migration phase is completed. The root Makefile remains the authority for L0 proof commands.
```

Do not claim all L0 files are under `L0/` unless Mode B completed and checks passed.

Do not remove existing README content unless it is factually wrong after path migration.

### Checks

Run:

```bash
make prove-seed
```

---

## 17.5 Mandatory Mode A Stop Boundary

After Mode A, Phase 10, and final validation checks, stop and report.

Do not continue into Mode B or Phase 9 unless the user separately and explicitly authorizes one of these exact scopes:

```text
RUN_MODE_B_L0_MIGRATION
RUN_PHASE_9_DOCUMENT_LOADER_IMPLEMENTATION
```

For Mode A-only completion, the correct final status is:

```text
VALIDATED
```

only if all required Mode A checks passed.

If Mode A files were created but some checks were not run, use:

```text
IMPLEMENTED_UNVALIDATED
```

If any required Mode A check failed and could not be fixed without guessing, use:

```text
BLOCKED
```

### README no-false-claim checklist

Before finalizing the README update, verify:

```text
[ ] README does not say all L0 files live under L0/ unless Mode B passed.
[ ] README does not say UNIT-L1-001 is implemented unless Phase 9 passed.
[ ] README does not say generated placeholders are release evidence.
[ ] README does not say validators exist unless actual validator scripts were created.
[ ] README keeps existing L0 quick-start commands accurate.
```

---

## 18. Final Validation Checklist

Before reporting success, verify:

```text
[ ] Baseline L0 checks were run before changes.
[ ] L1/ exists.
[ ] L2/ exists.
[ ] L0/README.md exists.
[ ] Root Makefile commands still work.
[ ] L0 does not import L1.
[ ] L0 does not import L2.
[ ] Five L1 standards are present under L1/standards/.
[ ] L1 docs exist and are non-empty.
[ ] L1 FIC registry exists.
[ ] FIC-L1-001 full document exists and is ready-for-code.
[ ] Placeholder FICs 002–012 exist and are draft.
[ ] L1 ES sidecars exist.
[ ] L1 SIB sidecars exist.
[ ] L1 EQC sidecars exist.
[ ] Generated placeholder files exist and are marked not release evidence.
[ ] Registry entries do not point to missing files.
[ ] Graph edges do not point to missing nodes.
[ ] SIB bindings do not point to missing IDs.
[ ] EQC manifest paths exist.
[ ] If Mode B ran, L0 files moved under L0/ and proof commands pass.
[ ] If document loader was implemented, its tests pass.
[ ] `make seed-boot` passes.
[ ] `make prove-seed` passes.
[ ] `make run` passes.
[ ] Completion record exists if implementation was done.
[ ] Review packet exists if implementation was accepted.
[ ] bootstrap artifact manifest exists and is marked not release evidence.
[ ] source-standard copy manifest exists.
[ ] ES/SIB/EQC cross-check evidence files exist.
[ ] Mode A bootstrap validator script exists and was run.
[ ] final validation evidence bundle exists.
[ ] git status --short was captured.
[ ] git diff --stat was captured.
```

### Extra import boundary check

Run:

```bash
grep -R "from L1\|import L1\|from L2\|import L2" -n L0 CODE 2>/dev/null || true
```

If this shows an actual L0 import of L1 or L2, block acceptance.

---

## 18.6 Final Status Decision Table

Use this table exactly.

| Condition | Final status |
|---|---|
| Mode A completed, all required checks passed, no Phase 9 implementation attempted | `VALIDATED` |
| Mode A files created but any required check not run | `IMPLEMENTED_UNVALIDATED` |
| Mode A blocked before file changes | `BLOCKED` |
| Mode A blocked after partial file changes | `IMPLEMENTED_UNVALIDATED` with blockers listed |
| Phase 9 implemented and all required tests/proofs passed | `VALIDATED` |
| Phase 9 implemented but any required test/proof failed or was not run | `IMPLEMENTED_UNVALIDATED` or `REJECTED` depending on whether code remains |
| No files changed because repo already matched this TODO and checks passed | `NO_CHANGE` |

For Mode A-only `VALIDATED`, write this exact clarification in the final response:

```text
Mode A scaffold validated. This is not release-candidate validation, and placeholder sidecars are not release evidence.
```


---

## 19. Final Response Format for the Coding LLM

Respond exactly in this structure:

```text
STATUS: VALIDATED | IMPLEMENTED_UNVALIDATED | BLOCKED | NO_CHANGE | REJECTED | IMPLEMENTED_WITH_WAIVERS

EXECUTION MODE:
- Mode A safe additive scaffold | Mode B L0 migration | Phase 9 document loader implementation

SUMMARY:
- ...

FILES CREATED:
- ...

FILES CHANGED:
- ...

CHECKS RUN:
- command: ...
  result: pass|fail|not-run
  evidence: ...

GIT EVIDENCE:
- git status --short: captured | not-run
- git diff --stat: captured | not-run

L0 IMPACT:
- none | described

L1 ARTIFACTS CREATED:
- ...

UNRESOLVED RISKS:
- ...

DEVIATIONS FROM TODO:
- ...

BLOCKERS:
- ...
```

Do not add a vague next-step recommendation in place of evidence.

---

## 20. Weaker Coding Model Rules

Use this simplified execution order if you are a weaker coding model:

```text
1. Inspect repo layout.
2. Run baseline commands.
3. If baseline fails, stop BLOCKED.
4. Create L0/L1/L2 readmes.
5. Copy five standards exactly.
6. Create L1 docs.
7. Create FIC registry.
8. Extract FIC-L1-001 using the provided Python script.
9. Create draft FIC placeholders.
10. Create ES sidecars.
11. Create SIB sidecars.
12. Create EQC sidecars.
13. Create generated placeholders.
14. Update README with layer layout.
15. Create bootstrap artifact manifest.
16. Create and run Mode A bootstrap validator.
17. Create final validation evidence bundle.
18. Run checks.
19. Capture git status and diff stat.
20. Stop. Do not run Mode B or Phase 9.
19. Report using the required format.
```

Hard rules:

```text
1. Do not be creative.
2. Follow phases in order.
3. Start with Mode A, not Mode B.
4. Do not move L0 unless explicitly executing Phase 2B.
5. Do not skip proof commands.
6. Do not edit L0 behavior.
7. Do not implement multiple units at once.
8. Prefer BLOCKED over guessing.
9. Keep all paths exactly as specified.
10. Keep all statuses exactly from the controlled vocabulary.
11. Do not add dependencies.
12. Do not claim tests passed unless you ran them.
13. Do not hide failed checks.
14. Do not summarize standards; copy them exactly.
15. Do not accept generated placeholders as release evidence.
16. Do not treat this TODO as permission to make architectural improvements.
17. Do not browse for new requirements.
18. Do not use old conversation context as authority over files.
```

If uncertain, stop with:

```text
STATUS: BLOCKED
Reason: <specific missing fact or failed check>
```

---

## 21. Minimum Acceptable Completion

Minimum acceptable completion is **Mode A, Phases 0–8A plus Phase 10 README update**:

```text
- Baseline proof commands ran.
- L1/L2 visible folders exist.
- L0 README placeholder exists.
- L1 standards are present.
- L1 control docs exist.
- L1 FIC registry and FIC-L1-001 exist.
- L1 ES/SIB/EQC sidecars exist.
- Generated placeholders are marked not release evidence.
- Root README explains layers without falsely claiming migration completed.
- Mode A bootstrap validator ran.
- Final validation evidence bundle exists.
- L0 proof commands still pass.
```

Stronger acceptable completion includes **Phase 9**:

```text
- UNIT-L1-001 document loader implemented.
- Tests for document loader pass.
- L0 proof commands still pass.
- Completion evidence exists.
- Review packet exists.
```

Full layout completion includes **Mode B**:

```text
- Existing root L0 files moved under L0/.
- Makefile paths updated.
- README paths updated.
- L0 proof commands still pass.
```

Do not start Phase 9 or Mode B unless Mode A is stable.
