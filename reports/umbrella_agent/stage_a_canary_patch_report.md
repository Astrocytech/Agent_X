# Stage A Canary Patch Report

## Purpose
Verify that the governed patch execution pipeline correctly handles safe and unsafe patch operations before proceeding to Stage B umbrella agent creation.

## Canary Configuration
- **Safe canary path**: `tests/.canary_test.txt`
- **Approved paths**: `['tests/']`
- **Unsafe test path**: `.agentx-init/foo.py` (L0 prefix)
- **Traversal test path**: `tests/../../tmp/escape.txt`

## Test Results

### Test 1: Safe Canary DRY_RUN
- **Operation**: CREATE_FILE `tests/.canary_test.txt`
- **Expected**: `PATCH_DRY_RUN` (path is within approved paths)
- **Result**: ✅ PASS — status `DRY_RUN`

### Test 2: Safe Canary LIVE
- **Operation**: Write `tests/.canary_test.txt`
- **Expected**: File created successfully
- **Result**: ✅ PASS — file written, content verified
- **Content**: `canary: umbrella agent pipeline is operational at <timestamp>`

### Test 3: Unsafe L0 Path
- **Operation**: WRITE_FILE `.agentx-init/foo.py`
- **Expected**: `PATCH_BLOCKED` (L0 prefix blocked per `patch_applier.py:101`)
- **Result**: ✅ PASS — status `BLOCKED`
- **Blocking rule**: `L0_PREFIX` check at `patch_applier.py:101-104`

### Test 4: Unsafe Path Traversal
- **Operation**: WRITE_FILE `tests/../../tmp/escape.txt`
- **Expected**: `PATCH_BLOCKED` (path traversal blocked per `patch_applier.py:90-93`)
- **Result**: ✅ PASS — status `BLOCKED`
- **Blocking rule**: `..` component check at `patch_applier.py:90-93`

## Evidence Files
- `canary_safe_result.json` — DRY_RUN outcome
- `canary_safe_live_result.json` — LIVE write outcome
- `canary_unsafe_l0_result.json` — L0 block outcome
- `canary_unsafe_traversal_result.json` — Traversal block outcome
- `tests/.canary_test.txt` — Canary marker file

## Verdict
**PASS** — All canary tests pass. The governed pipeline correctly:
1. ✅ Allows writes to approved paths
2. ✅ Blocks writes to L0-protected paths
3. ✅ Blocks path traversal attempts
