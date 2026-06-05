# Packaging Distribution Layer — Implementation Spec v4

**Roadmap Layer:** 18
**Roadmap Phase:** Phase E — Packaging
**Component:** agentx_evolve/packaging/

## Overview

Layer 18 provides a dedicated Packaging & Distribution layer that validates distribution readiness, checks command availability, verifies dependency group definitions, and persists check results for auditability.

## Modules

### packaging_checker.py
- **PackagingCheckResult** — dataclass tracking a single check outcome: check_name, status (PASS/FAIL/WARN), details, warnings, errors.
- **PackagingDistributionCheck** — dataclass with schema metadata, clone install status, optional dependencies status, base install status, commands_available, dep_groups_defined, checks list, checked_at, warnings, errors, result_hash.
- **PackagingResultHash** — hash wrapper that computes sha256 of canonical JSON over the check payload (excluding result_hash itself).
- **PackagingChecker** — runs distribution checks, persists reports, maintains history, acquires/releases file lock.
- **Schema validation** — `validate_schema` static method on `PackagingDistributionCheck` validates data against schemas/packaging_distribution_check.schema.json contract.

### Constants & Helpers
- `PKG_SCHEMA_VERSION`, `PKG_SCHEMA_ID`
- `PKG_CHECK_PASS`, `PKG_CHECK_FAIL`, `PKG_CHECK_WARN`
- `PKG_DEP_LOCAL_MODEL`, `PKG_DEP_MCP`, `PKG_DEP_GIT`, `PKG_DEP_DEV`, `PKG_DEP_HOSTED_MODEL`
- `canonical_json`, `sha256_dict`, `write_json_atomic`, `append_jsonl`

### Persistence
- Reports written to `.agentx-init/packaging/packaging_check_report.json`
- History appended to `.agentx-init/packaging/packaging_history.jsonl`
- File locking via `.agentx-init/packaging/.packaging.lock`

## Schema
`schemas/packaging_distribution_check.schema.json` (Draft-07) validates distribution check report payloads.

## Dependencies
- `agentx_evolve.model.model_models` — `new_id`, `to_dict`
