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
