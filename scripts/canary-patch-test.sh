#!/usr/bin/env bash
set -euo pipefail
# Canary patch test for umbrella agent governed pipeline.
# Tests safe (approved path) and unsafe (blocked path + path traversal) patches.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CANARY_PATH="tests/.canary_test.txt"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo "  ==> $1: PASS"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "  ==> $1: FAIL"; FAIL_COUNT=$((FAIL_COUNT + 1)); }
report() {
  mkdir -p "$REPO_ROOT/reports/umbrella_agent"
  echo "$2" > "$REPO_ROOT/reports/umbrella_agent/$1"
}

echo "=== Stage A: Canary Patch Verification ==="
echo "Repo root: $REPO_ROOT"
echo "Safe canary path: $CANARY_PATH"
echo ""

# ----- Test 1: DRY_RUN safe canary -----
echo "--- Test 1: Safe canary (DRY_RUN, approved path) ---"
cd "$REPO_ROOT"
rm -f "$CANARY_PATH" 2>/dev/null || true

DRY_OUT=$(PYTHONPATH="$REPO_ROOT/tools/agentx_evolve:$REPO_ROOT/tools" \
  python3 -c "
from pathlib import Path
from agentx_evolve.patch_execution.patch_models import (
    PatchOperation, OP_CREATE_FILE, PATCH_DRY_RUN, MODE_DRY_RUN, new_id
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.patch_execution.patch_session import create_implementation_session

r = Path('$REPO_ROOT')
s = create_implementation_session(r, ['$CANARY_PATH'], 'p', 'g', 'p', None)
o = [PatchOperation(operation_id=new_id('op'), operation_type=OP_CREATE_FILE,
                     target_path='$CANARY_PATH', content='canary: operational',
                     allow_create=True)]
res = apply_patch_operations(s, o, r, MODE_DRY_RUN, ['tests/'], None, None)
print(res.status)
" 2>&1)

if [ "$DRY_OUT" = "DRY_RUN" ]; then
  pass "Safe canary DRY_RUN"
  report "canary_safe_result.json" "{\"test\":\"safe_canary_dry_run\",\"status\":\"PASS\",\"dry_run_status\":\"DRY_RUN\",\"canary_path\":\"$CANARY_PATH\"}"
else
  fail "Safe canary DRY_RUN (got: $DRY_OUT)"
  report "canary_safe_result.json" "{\"test\":\"safe_canary_dry_run\",\"status\":\"FAIL\",\"dry_run_status\":\"$DRY_OUT\"}"
fi

# ----- Test 2: LIVE canary (patch executor) -----
echo "--- Test 2: Safe canary (LIVE, patch executor) ---"
rm -f "$CANARY_PATH" 2>/dev/null || true
CANARY_CONTENT="canary: umbrella agent pipeline is operational at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

LIVE_OUT=$(PYTHONPATH="$REPO_ROOT/tools/agentx_evolve:$REPO_ROOT/tools" \
  python3 -c "
import sys
from pathlib import Path
from agentx_evolve.patch_execution.patch_models import (
    PatchOperation, OP_CREATE_FILE, MODE_LIVE, new_id,
    PATCH_APPLIED, PATCH_BLOCKED, PATCH_FAILED, MODE_DRY_RUN,
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.patch_execution.patch_session import create_implementation_session, update_implementation_session

r = Path('$REPO_ROOT')
s = create_implementation_session(r, ['$CANARY_PATH'], 'p', 'g', 'p')
s = update_implementation_session(s, r, 'SNAPSHOT_CREATED', rollback_snapshot_id='canary-rollback-001')

from agentx_evolve.security.security_models import SandboxPolicy
from agentx_evolve.security.initiator_compat import InitiatorCompat

policy = SandboxPolicy(
    policy_id='canary-policy',
    source_write_allowed=True,
    runtime_write_allowed=True,
    allowlisted_write_paths=['tests/'],
)
compat = InitiatorCompat(repo_root=r)

o = [PatchOperation(operation_id=new_id('op'), operation_type=OP_CREATE_FILE,
                     target_path='$CANARY_PATH',
                     content='$CANARY_CONTENT',
                     allow_create=True)]
res = apply_patch_operations(s, o, r, MODE_LIVE, ['tests/'], policy, compat)
print(res.status)
sys.exit(0 if res.status in ('APPLIED', 'BLOCKED') else 1)
" 2>&1)

LIVE_STATUS=$(echo "$LIVE_OUT" | head -1)
if [ "$LIVE_STATUS" = "APPLIED" ] || [ "$LIVE_STATUS" = "BLOCKED" ]; then
  if [ -f "$REPO_ROOT/$CANARY_PATH" ]; then
    pass "Safe canary LIVE (patch executor wrote file)"
    REPORT_SAFE="{\"test\":\"safe_canary_live\",\"status\":\"PASS\",\"mode\":\"MODE_LIVE\",\"canary_path\":\"$CANARY_PATH\",\"patch_status\":\"$LIVE_STATUS\"}"
    report "canary_safe_live_result.json" "$REPORT_SAFE"
  else
    fail "Safe canary LIVE - file not found after patch"
    report "canary_safe_live_result.json" "{\"test\":\"safe_canary_live\",\"status\":\"FAIL\",\"error\":\"file_not_found\",\"patch_status\":\"$LIVE_STATUS\"}"
  fi
else
  fail "Safe canary LIVE - unexpected status: $LIVE_STATUS"
  report "canary_safe_live_result.json" "{\"test\":\"safe_canary_live\",\"status\":\"FAIL\",\"patch_status\":\"$LIVE_STATUS\"}"
fi

# ----- Test 3: Unsafe L0 path -----
echo "--- Test 3: Unsafe canary (L0 path, should be BLOCKED) ---"
L0_OUT=$(PYTHONPATH="$REPO_ROOT/tools/agentx_evolve:$REPO_ROOT/tools" \
  python3 -c "
from pathlib import Path
from agentx_evolve.patch_execution.patch_models import (
    PatchOperation, OP_WRITE_FILE, PATCH_BLOCKED, MODE_DRY_RUN, new_id
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.patch_execution.patch_session import create_implementation_session

r = Path('$REPO_ROOT')
s = create_implementation_session(r, ['.agentx-init/foo.py'], 'p', 'g', 'p', None)
o = [PatchOperation(operation_id=new_id('op'), operation_type=OP_WRITE_FILE,
                     target_path='.agentx-init/foo.py', content='evil')]
res = apply_patch_operations(s, o, r, MODE_DRY_RUN, ['tests/'], None, None)
print(res.status)
" 2>&1)

if [ "$L0_OUT" = "BLOCKED" ]; then
  pass "Unsafe canary (L0 blocked)"
  report "canary_unsafe_l0_result.json" "{\"test\":\"unsafe_canary_l0\",\"status\":\"PASS\",\"attempted_path\":\".agentx-init/foo.py\"}"
else
  fail "Unsafe canary (L0) - expected BLOCKED, got: $L0_OUT"
  report "canary_unsafe_l0_result.json" "{\"test\":\"unsafe_canary_l0\",\"status\":\"FAIL\",\"result\":\"$L0_OUT\"}"
fi

# ----- Test 4: Unsafe traversal -----
echo "--- Test 4: Unsafe canary (path traversal, should be BLOCKED) ---"
TRAV_OUT=$(PYTHONPATH="$REPO_ROOT/tools/agentx_evolve:$REPO_ROOT/tools" \
  python3 -c "
from pathlib import Path
from agentx_evolve.patch_execution.patch_models import (
    PatchOperation, OP_WRITE_FILE, PATCH_BLOCKED, MODE_DRY_RUN, new_id
)
from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
from agentx_evolve.patch_execution.patch_session import create_implementation_session

r = Path('$REPO_ROOT')
s = create_implementation_session(r, ['tests/../../tmp/escape.txt'], 'p', 'g', 'p', None)
o = [PatchOperation(operation_id=new_id('op'), operation_type=OP_WRITE_FILE,
                     target_path='tests/../../tmp/escape.txt', content='evil')]
res = apply_patch_operations(s, o, r, MODE_DRY_RUN, ['tests/'], None, None)
print(res.status)
" 2>&1)

if [ "$TRAV_OUT" = "BLOCKED" ]; then
  pass "Unsafe canary (traversal blocked)"
  report "canary_unsafe_traversal_result.json" "{\"test\":\"unsafe_canary_traversal\",\"status\":\"PASS\",\"attempted_path\":\"tests/../../tmp/escape.txt\"}"
else
  fail "Unsafe canary (traversal) - expected BLOCKED, got: $TRAV_OUT"
  report "canary_unsafe_traversal_result.json" "{\"test\":\"unsafe_canary_traversal\",\"status\":\"FAIL\",\"result\":\"$TRAV_OUT\"}"
fi

echo ""
echo "=== Results: $PASS_COUNT pass, $FAIL_COUNT fail ==="
echo "Canary file at: $CANARY_PATH"
[ "$FAIL_COUNT" -eq 0 ] || exit 1
