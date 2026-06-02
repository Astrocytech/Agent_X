# LAYER_MAPPER_FIC_SIB_EQC_CONTRACT

> **Alignment Patch Note:** This document was created during the Product Milestone 1 alignment synchronization pass.  
> It fills the missing Layer Mapper component contract gap.  
> No technical rework, schema changes, or authority-boundary changes beyond the contract definition were made.

## 0.1 Identity

```yaml
fic_id: "FIC-AGENTX-INITIATOR-LAYER-MAPPER-001"
sib_id: "SIB-AGENTX-INITIATOR-LAYER-MAPPER-001"
eqc_id: "EQC-AGENTX-INITIATOR-LAYER-MAPPER-001"
component_id: "AGENTX_LAYER_MAPPER"
component_name: "Layer Mapper"
version: "v1.0.0"
status: "ready-for-milestone-1-implementation"
artifact_type: "core-analysis"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "low"
enforcement_profile: "standard"
implementation_mode: "new-component"
primary_standards:
  - "FIC"
  - "SIB"
  - "EQC"
supporting_standards:
  - "Audit Rules"
```

## 0.2 Final Freeze Verdict

This document is now frozen as the controlling FIC+SIB+EQC contract for the Layer Mapper Component Milestone 1 implementation.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 1 = when this component is integrated into the product roadmap.

Layer Mapper is scheduled for **Product Milestone 1**.

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
EQC.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## Purpose

Layer Mapper classifies repository paths as L0, L1, L2, or unknown and identifies protected paths for scanner, architecture, and governance use.

---

## Authority Boundary

Classification only. No source mutation. No governance decision.

---

## Inputs

- Normalized repository paths
- Optional scanner file/directory records from Repository Scanner

---

## Outputs

- Layer classification records (path → L0/L1/L2/unknown)
- Protected-path classification records (path → protected/unprotected)

Both outputs are internal helper maps consumed by Repository Scanner and Architecture Analyzer. They are not independently serialized as runtime artifacts in Product Milestone 1.

---

## Target Implementation File

```
agentx_initiator/core/layer_mapper.py
```

---

## Public Surface Contract

```
classify_layer(path: Path) -> str                    # Returns "L0", "L1", "L2", or "unknown"
is_protected_path(path: Path) -> bool                # Returns True for protected paths
build_layer_map(paths: list[Path]) -> dict           # Returns {path: layer} mapping
build_protected_path_map(paths: list[Path]) -> dict  # Returns {path: protected/unprotected} mapping
```

---

## Schemas

May reuse `layer_map.schema.json` and `protected_path_map.schema.json` from the Repository Scanner / shared schema set.

No separate Layer Mapper schema is required in Product Milestone 1.

---

## Required Standards

- **Primary:** SIB
- **Required:** FIC, EQC
- **Conditional:** None

---

## Core Rules

- L0 paths are always protected.
- Governance and standards paths are protected.
- Unknown classification is allowed and must not be coerced.
- Classification must be deterministic (same input → same output).
- Layer Mapper must not mutate files.
- Layer Mapper must not execute commands.
- Layer Mapper must not decide governance outcomes.
- Layer Mapper must not walk the filesystem independently unless explicitly passed paths.
- Layer Mapper must classify unknown when evidence is insufficient.

---

## Negative Space Contract

Layer Mapper does not:

- Walk the filesystem on its own
- Write files or artifacts
- Execute commands or subprocesses
- Make governance decisions
- Score risk
- Plan evolution steps
- Parse source code semantics
- Mutate repository state
- Track history
- Emit audit events directly (consumers own their audit trail)

---

## Dependency Contract

Layer Mapper depends on:

```text
- Path utility functions (path normalization)
```

**Dependency direction:** Layer Mapper must not import Repository Scanner. Repository Scanner may import Layer Mapper for layer classification during scan. This prevents circular dependency in PM1.

Layer Mapper optionally receives pre-scanned file records from Repository Scanner through a data parameter, not through a reverse import.

Layer Mapper may be consumed by:

```text
- Repository Scanner
- Architecture Analyzer
- Config / Paths
```

Layer Mapper may share `layer_map.schema.json` and `protected_path_map.schema.json` with Repository Scanner.

---

## Layer Vocabulary

Layer Mapper is the shared authority for L0/L1/L2/unknown vocabulary. Repository Scanner uses this vocabulary when classifying files during scan. Both components must use the same layer vocabulary.

| Layer | Description | Examples |
|---|---|---|
| L0 | Protected foundational/governance material | `L0/`, `DOCUMENTS/standards/`, `governance/`, root-level protected standards |
| L1 | Infrastructure, validators, implementation-control, and Initiator-controlled support | `L1/`, `agentx_initiator/`, `validators/`, `tools/`, `scripts/` |
| L2 | Profiles, blueprints, integration specs, evaluation specs, and specialization documents | `L2/`, `profiles/`, `blueprints/`, `integration_specs/`, `evaluation_specs/` |
| unknown | Unrecognized or ambiguous path | any path not matching L0/L1/L2 patterns |

---

## Determinism Contract

- Same path + same context → same classification every time.
- Protected-path classification is deterministic.
- Layer Mapper has no mutable state that affects classification.
- Classification logic must be testable without filesystem access.

---

## Preconditions

- Input paths are normalized (absolute or relative to repo root).
- If scanner records are provided, they are valid per `repo_scan.schema.json`.

---

## Postconditions

- Every input path has a classification: L0, L1, L2, or unknown.
- Every input path has a protected/unprotected determination.
- No files are created, modified, or deleted.
- No commands were executed.
- No governance decisions were produced.

---

## Invariants

- L0 is always protected.
- Classification results are reproducible.
- Adding unrecognized paths never produces false layer matches.
- Empty input → empty output (no crash, no classification).

---

## Acceptance Criteria

- All valid paths return a recognized layer or unknown.
- All L0 paths return protected = true.
- Determinism holds across 3 consecutive calls with the same input.
- Empty input returns empty dicts, not errors.
- Layer Mapper import and function calls succeed without network, config, or filesystem.

---

## Test Oracle Strength

- Each classification function has a deterministic oracle: expected output for a representative sample of L0, L1, L2, and unknown paths.
- Protected-path oracle covers all L0 paths, a sample of L1/L2 paths, and unknown paths.
- Determinism oracle: assert identical output for repeated calls.
- Empty input oracle: assert empty dicts returned.
- No-mutation oracle: assert no file writes, no subprocess calls.

---

## Core Test List

```
test_l0_paths_are_protected
test_l1_paths_classify_as_l1
test_l2_paths_classify_as_l2
test_unknown_paths_remain_unknown
test_classification_is_deterministic
test_layer_mapper_has_no_source_mutation
test_protected_path_map_is_deterministic
test_layer_mapper_returns_valid_records_for_empty_input
test_layer_mapper_classifies_unknown_on_insufficient_evidence
test_layer_mapper_does_not_walk_filesystem_independently
test_layer_mapper_does_not_execute_commands
test_layer_mapper_does_not_make_governance_decisions
```

---

## Implementation Handoff Envelope

```yaml
target_file: agentx_initiator/core/layer_mapper.py
public_surface:
  - classify_layer(path: Path) -> str
  - is_protected_path(path: Path) -> bool
  - build_layer_map(paths: list[Path]) -> dict
  - build_protected_path_map(paths: list[Path]) -> dict
shared_schemas:
  - layer_map.schema.json
  - protected_path_map.schema.json
test_file: agentx_initiator/tests/test_layer_mapper.py
completion_record: TASK_CONTRACT.md, IMPLEMENTATION_HANDOFF.yaml, completion_record.schema.json
```

---

## Completion Evidence Contract

Implementation is complete when:

- All public-surface functions exist and match the signatures above.
- All core tests pass.
- Determinism is confirmed.
- No file mutation, no command execution, no governance output.
- No filesystem walking unless paths are explicitly passed.
- Schema validation confirms output format.
- `completion_record.schema.json` is populated.
