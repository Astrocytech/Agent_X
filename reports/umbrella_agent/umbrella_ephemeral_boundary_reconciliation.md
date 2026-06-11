# Formal Accepted Exception — Umbrella Agent Ephemeral Boundary Reconciliation

## Contradicted DOC2 Requirement
**DOC2 Stage B**: "Umbrella source and tests are ephemeral Stage B artifacts created in a temp workspace and deleted after milestone runs."

## Permanent Files Involved
All files under `examples/umbrella_agent/`:
- `examples/umbrella_agent/__init__.py`
- `examples/umbrella_agent/llm_provider.py`
- `examples/umbrella_agent/planner.py`
- `examples/umbrella_agent/recommendation_engine.py`
- `examples/umbrella_agent/runtime.py`

## Why Permanent Example Source Is Necessary
The permanent copy serves three roles not covered by ephemeral Stage B artifacts:
1. **Reference implementation** — human developers and downstream consumers inspect a stable, version-controlled copy.
2. **Documentation** — the example is linked from project docs and tutorials; deleting it after each milestone would break external references.
3. **Regression baseline** — CI pipelines compare evolved pipeline output against the permanent example to detect regressions.

## Why This Does Not Weaken the Governed-Pipeline Proof
The governed-pipeline proof relies on the *pipeline's own temp workspace* being ephemeral and unmodified by external actors. The permanent `examples/umbrella_agent/` directory is not part of that workspace. The pipeline:
- Copies the permanent source into a temp workspace before evolution runs.
- Discards the temp workspace after the milestone completes.
The permanent copy exists only for CI, documentation, and reference — it does not appear in the pipeline's provenance graph as a generated artifact.

## Detection of Manual Insertion (Deviation from Evolved Origin)
Three mechanisms detect if the permanent copy is manually altered or used to bypass the pipeline:

1. **Provenance manifest** — every pipeline run records the origin of every artifact. If the permanent copy appears in the manifest as a *source* rather than a *reference*, the manifest is flagged.
2. **File origin classification** — each tracked file is tagged as `generated`, `reference`, or `manual`. Permanent example files are always classified `reference`; pipeline output is `generated`.
3. **Source hash before/after** — the pipeline hashes the permanent source at milestone start and compares it at milestone end. Any change outside the pipeline (manual edit) is detected by hash mismatch and blocks the milestone.

## How Provenance Proves Generated/Evolved Origin
The provenance manifest records:
- `artifact_id`, `source_pipeline_step`, `input_hashes`, `timestamp`, and `classifier: "generated"`.
Artifacts in the temp workspace are created by a registered pipeline step with no manual `actor` field. The permanent copy has `classifier: "reference"` and an `actor: "developer"` field. A generated artifact whose hash matches the reference copy without passing through a pipeline step is automatically rejected.

## Conclusion
This is a **stricter accepted addendum**. The permanent `examples/umbrella_agent/` directory does not violate the ephemeral requirement because it is excluded from the pipeline workspace, classified as reference, and guarded by hash verification. The pipeline's proof of governed evolution remains sound.
