# Functional Runtime MVP Proof Pipeline

## Overview

The `prove-functional-runtime-mvp` Makefile target runs the full
Functional Runtime MVP proof pipeline. It executes in 6 phases:

### Phase 1: Setup
- Clean `.agentx-init/reports/`
- Generate `PROOF_RUN_ID`
- Acquire serial executor lock (prevents concurrent runs)
- Record git commit, working tree status, and full Git provenance

### Phase 2: Generate
- Compile check (all Python source)
- Run MVP test suite (validators + scenarios)
- Snapshot baseline transcript
- Collect initial proof (`collect_mvp_proof.py`)
- Generate reports (`generate_mvp_reports.py`)

### Phase 3: Validate
Run all validators under `tools/agentx_evolve/validators/`:
- Specialized validators (gap discovery, replay, reuse map, source safety)
- Runtime safety validators (anti-false-PASS, self-promotion, event log, state, path safety, runtime safety)
- Cross-domain validators (cross-report, corrective coverage, clean checkout, artifact safety, execution integrity, provenance, security, completeness, lifecycle, infrastructure, determinism, meta quality)
- Domain coverage validators (advanced, deep, enterprise, aspirational)

### Phase 4: Freeze
- Validate transcript (all commands now recorded)
- Rebuild reports with complete transcript
- Rebuild traceability matrix (no forced PASS) and validate
- Final freeze — proof bundle with full Git provenance, toolchain hashes, source tree manifest
- Regenerate Markdown transcript from frozen JSON
- Generate runtime proof artifacts:
  - State reconstruction proof (hash-chain over state records)
  - Runtime entrypoint proof (imports, orchestrator instantiation, goal execution)

### Phase 5: Finalize
- Meta-validators (validator proof, filesystem snapshot, core invariants)
- Cross-report and proof configuration validators (all-in-one, proof staleness, schema version, proof config, state transition)
- Security and integrity validators (secret redaction, side-effect, failure taxonomy)
- No-forced-PASS guard
- Generate proof-configuration manifest (items 778-782)
- Generate and validate final verdict with full Git SHA + proof_config_hash
- Architecture scope map (23+ layers) and validation
- No-hidden-authority check
- Required artifacts manifest generation and validation
- Classification consistency check
- JSON/Markdown non-contradiction check
- I/O boundary validation (shell=True, absolute paths, uncontrolled env)
- Proof size validation
- Zero-byte and UTF-8 validation on all reports
- Runtime proof validators (state reconstruction, entrypoint)

### Phase 6: CI Evidence (optional)
- Generate offline evidence bundle and proofs index
- Scan proof artifacts for secrets
- Validate confidentiality (zero secret findings)
- Release serial executor lock

## Key scripts

| Script | Purpose |
|--------|---------|
| `collect_mvp_proof.py` | Collect command results into proof bundle with full Git provenance |
| `generate_final_verdict.py` | Produce final PASS/FAIL verdict (candidate; verified by verify_existing_proof.py) |
| `generate_scope_map.py` | Architecture scope map covering all 23+ Agent_X layers |
| `generate_proof_config_manifest.py` | Canonical proof configuration manifest with version, validators, reports, hash |
| `generate_required_artifacts_manifest.py` | Required/optional/debug-only file inventory |
| `generate_gap_discovery_report.py` | Gap coverage report |
| `generate_traceability_matrix.py` | Requirement traceability matrix |
| `extra_generators.py` | Offline bundle + proofs index |
| `scan_secrets.py` | Secret scan of evidence artifacts |
| `record_command.py` | Record a single command result |
| `verify_existing_proof.py` | Verify a prior proof bundle; upgrade candidate verdict to verified |
| `state_reconstruction_proof.py` | State reconstruction hash chain proof |
| `runtime_entrypoint_proof.py` | Runtime entrypoint with import check, orchestrator instantiation, goal execution |
| `serial_executor_guard.py` | Concurrent execution lock |
| `validate_zero_byte_utf8.py` | Validate no zero-byte files, invalid UTF-8 in reports |

## Validator list

See `tools/agentx_evolve/validators/` for all validator scripts (53 total).
Each exits 0 on PASS and non-zero on FAIL.

## Architecture layers

The scope map (v2) covers 27 architecture layers including:
- Runtime orchestrator, scenarios, safety, security sandbox, policy registry
- Patch execution, failure taxonomy, tool/MCP adapter, model adapter
- Local model runtime profile, context builder, prompt contract, LLM worker
- Self-evolution orchestrator, human review, promotion gate, git integration
- Evaluation harness, long-term learning, doc sync, task queue, monitoring
- Packaging, backup/DR, final acceptance, evidence framework
- Traceability framework, infrastructure framework, domain coverage

Each layer has a machine-readable status: `implemented_and_proven`,
`implemented_unproven`, `stub_only`, `future_work`, or `out_of_scope_for_this_mvp`.

## Idempotency

`make prove-functional-runtime-mvp` runs the pipeline twice and
compares outputs via `generate_idempotency_report.py`.

## Full Git provenance

All proof artifacts now record full 40-char commit SHA, tree hash,
parent commit, branch/ref, remote URL, and detached status.
Short SHAs are rejected by `validate_functional_runtime_mvp_proof_config.py`
(item 383-384).

## Proof-configuration manifest

`generate_proof_config_manifest.py` creates a canonical manifest
(`functional_runtime_mvp_proof_config_manifest.json`) listing proof version,
required reports (23), validators (52), generators (14), scenarios (3),
commands, classification rules, and a SHA-256 manifest hash.

The manifest hash propagates to `final_verdict.json` as `proof_config_hash`
and is validated by `validate_functional_runtime_mvp_proof_config.py`
(items 378-382).

## I/O boundary model

`validate_functional_runtime_mvp_io_boundary.py` enforces:
- No shell=True, os.system, os.popen in proof/runtime code (items 399-400)
- Subprocess calls must use explicit `env=` or be flagged
- No absolute temp or home paths in final proof reports (item 415)
- All evidence paths under report directory or declared durable root

## State-machine transitions

`validate_functional_runtime_mvp_state_transition.py` validates:
- Legal state transitions in event logs and state records (items 395-398)
- Terminal verdicts derived from state machine, not free text
- I/O boundary model declarations in proof bundle
- Shell injection patterns in command transcript

## Frozen verification

`verify_existing_proof.py` validates frozen proof without regeneration.
With `--promote`, it upgrades the generator-written candidate verdict to
`verified` status (items 404-406). This is the independent frozen verifier
that computes the final classification from frozen JSON evidence alone.
