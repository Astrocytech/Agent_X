# Input/Output Pairing Integrity Contract

## Purpose
Define rules and procedures for maintaining the integrity of input/output pairings in the BenchCore benchmark pack. Ensures that every output can be traced back to its originating input and that misalignments are detected and flagged.

## Source
BENCHCORE-DOC-027

## Pairing Rules
1. **One-to-one mapping**: Each input must produce exactly one output record. One-input-to-multi-output scenarios (e.g., log parsing) are explicitly documented and must include a `parent_input_id` reference.
2. **Bidirectional traceability**: Every output record must contain an `input_id` field referencing the source input. Every input that has been processed must have at least one corresponding output.
3. **Determinism requirement**: Given the same input and same configuration, the output must be identical across runs (benchmark reproducibility requirement).

## Alignment Check
- An alignment check compares the set of processed input IDs against the set of output `input_id` references.
- The check passes if and only if:
  - Every processed input ID appears at least once in the output set.
  - Every output `input_id` references a valid processed input.
- For one-input-to-multi-output scenarios, additional validation ensures that the count of outputs per input matches the documented expected count.

## Misalignment Detection
| Condition | Detection | Severity |
|-----------|-----------|----------|
| Output `input_id` references a non-existent input | Orphan output | ERROR |
| Input has been processed but no output exists | Missing output | ERROR |
| Input produces fewer/more outputs than expected | Count mismatch | WARN |
| Output content differs from expected under identical conditions | Non-determinism | ERROR |

## Remediation
- Orphan outputs are quarantined, not discarded, for forensic analysis.
- Missing outputs trigger reprocessing of the parent input.
- Count mismatches trigger a full alignment re-check and are logged for review.

## Dependencies
- Input and output records indexed by UUID
- No live database, network, or production system dependencies
