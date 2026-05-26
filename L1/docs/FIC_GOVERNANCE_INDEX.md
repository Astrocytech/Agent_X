# FIC Governance Index

This index defines the root FIC-governance document set for Agent_X L1.

## Root Governance Documents

| File | Purpose |
| --- | --- |
| `00_L1_SYSTEM_GOAL.md` | Defines the top-level Agent_X governance goal, non-goals, authority, constraints, lifecycle expectations, and acceptance conditions. |

| `03_L1_WHOLE_SYSTEM_PSEUDOCODE.md` | Defines the whole-system governed workflow before decomposition into FIC units. |

| `05_L1_SHARED_TYPES_AND_INTERFACES.md` | Defines shared statuses, records, contracts, interface vocabulary, lifecycle semantics, and traceability types used by FIC units. |

## Authority Chain

Governed implementation should follow this chain:

```text
L1/docs/00_L1_SYSTEM_GOAL.md
  -> L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md
  -> L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md
  -> L1/fic/<unit-specific-fic>.md
  -> implementation files
  -> tests
  -> validation evidence
  -> review
```

## Relationship to `L1/fic/`

The files in `L1/docs/` are root governance documents.

The files in `L1/fic/` are bounded implementation-unit FIC contracts derived from the root governance documents.

A unit FIC should cite the root governance documents that authorize it.

## Relationship to Older L1 Documents

This index identifies the root FIC-governance document set currently used for L1 FIC workflow adoption:

- `00_L1_SYSTEM_GOAL.md`
- `03_L1_WHOLE_SYSTEM_PSEUDOCODE.md`
- `05_L1_SHARED_TYPES_AND_INTERFACES.md`

Older or differently numbered L1 documents may remain as supporting/background governance material unless they are explicitly cited as current authority by this index or by a unit-level FIC.

If an older L1 document conflicts with the current root FIC-governance set, the conflict must be resolved by review before implementation proceeds.

## Authority Rule

If a FIC unit conflicts with these root governance documents, the FIC unit must be revised or marked blocked.

Existing code is evidence of current implementation state, but it does not override these governance documents.

## Placement Rule

Do not duplicate these root governance documents under:

```text
DOCUMENTS/FIC/
L2/
repo root
docs/fic/
```

## Archived Legacy Documents

Earlier L1 root-like documents are archived under:

```text
L1/docs/archive/standards-root-duplicates/
```

The active root governance documents are:

- `L1/docs/00_L1_SYSTEM_GOAL.md`
- `L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md`
- `L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md`
- `L1/docs/FIC_GOVERNANCE_INDEX.md`

If archived material is needed, it must be migrated into an active root governance document through an explicit reviewed document update.

## Standards Rule

Reference standards such as EQC, EQC-FIC, EQC-SIB, and the Pseudocode-to-FIC-to-Code workflow remain standards until adopted by project-specific L1 governance documents or FIC units.

## Runtime Effect

These documents are governance artifacts only. They introduce no runtime behavior by themselves.
