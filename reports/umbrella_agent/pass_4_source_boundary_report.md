# Pass 4: Source Boundary Report

## Purpose
Document the source tree boundary enforcement mechanisms that protect L0/ and restricted paths during umbrella agent evolution.

## Boundary Mechanisms

### 1. L0 Prefix Protection (patch_applier.py)
- **File**: `tools/agentx_evolve/patch_execution/patch_applier.py:22`
- **Constant**: `L0_PREFIX = ".agentx-init/"`
- **Enforcement**: `patch_applier.py:101-104`
- **Scope**: Blocks any operation targeting `.agentx-init/` paths
- **Verified**: Canary test 3 (L0 blocked) ✅

### 2. Approved Paths Filter (patch_applier.py)
- **Function**: `_is_path_approved()` at `patch_applier.py:25-31`
- **Mechanism**: Exact match + prefix match (`path.startswith(prefix)` for prefixes ending in `/`)
- **Scope**: Only paths in `approved_paths` list pass through
- **Verified**: Canary test 1 (safe path approved) ✅

### 3. Path Traversal Protection (patch_applier.py)
- **Check**: `".." in op_path.split("/")` at `patch_applier.py:90-93`
- **Scope**: Blocks any `..` path components
- **Verified**: Canary test 4 (traversal blocked) ✅

### 4. Absolute Path Protection (patch_applier.py)
- **Check**: `op_path.startswith("/")` at `patch_applier.py:85-88`
- **Scope**: Blocks absolute paths (must be repo-relative)

### 5. Symlink Escape Protection (patch_applier.py)
- **Check**: Resolved path must start with repo root at `patch_applier.py:95-99`
- **Scope**: Blocks symlinks pointing outside the repo

### 6. SandboxPolicy Protected Paths
- **File**: `tools/agentx_evolve/security/sandbox_policy.py`
- **Default**: `protected_paths=["L0/", "agent_x/runtime/", "core/"]`

### 7. Source Change Guard
- **File**: `tools/agentx_evolve/patch_execution/source_change_guard.py`
- **Mechanism**: Verifies only approved paths were changed after patch execution

## Repository File Origin Summary

| Category | Count | Examples |
|----------|-------|---------|
| L0/ (seed) | ~120 | `L0/CODE/core_kernel/`, `L0/CODE/governance/` |
| L1/ (tools) | ~80 | `L1/validators/`, `L1/tests/` |
| L2/ (meta) | ~40 | `L2/validators/`, `L2/tests/` |
| tools/ | ~600 | `tools/agentx_evolve/`, `tools/agentx_initiator/` |
| tests/ | ~50 | `tests/smoke/`, `tests/integration/`, `tests/regression/` |
| schemas/ | ~10 | `schemas/umbrella_agent_*.schema.json` |

## Boundary Verdict
**PASS** — 7 layers of source boundary enforcement active and verified.
