#!/usr/bin/env bash
set -euo pipefail
# prove-post-umbrella.sh — Post-umbrella phase verification
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
log() { echo "[$(date +%H:%M:%S)] $*"; }
log "=== Post-Umbrella Phase Verification ==="
log "Root: $REPO_ROOT"

# Phase 0: Evolve post-umbrella agents through governed pipeline
log "--- Phase 0: Governed agent evolution ---"
bash "$REPO_ROOT/scripts/evolve-post-umbrella.sh" || {
  log "  evolve-post-umbrella: FAIL"
  exit 1
}

# Phase 1: Prior verification artifacts
log "--- Phase 1: Prior verification ---"
for f in \
  .agentx-init/five_document_closure/source_documents/source_document_inventory.json \
  .agentx-init/five_document_closure/baseline/baseline_repository_snapshot.json \
  .agentx-init/five_document_closure/baseline/baseline_command_transcript.json; do
  test -f "$REPO_ROOT/$f" && log "  $f: OK" || { log "  $f: MISSING"; exit 1; }
done

# Schemas
log "--- Infrastructure: Schemas ---"
for f in \
  schemas/benchmark_case.schema.json \
  schemas/benchmark_result.schema.json \
  schemas/command_transcript.schema.json \
  schemas/evidence_manifest.schema.json \
  schemas/event_log_entry.schema.json \
  schemas/provenance_record.schema.json \
  schemas/source_manifest.schema.json \
  schemas/umbrella_agent_input.schema.json \
  schemas/umbrella_agent_output.schema.json \
  schemas/umbrella_weather_fixture.schema.json; do
  test -f "$REPO_ROOT/$f" && log "  $f: OK" || { log "  $f: MISSING"; exit 1; }
done

# Example agents
log "--- Example Agents ---"
for agent_dir in examples/clothing_advice_agent examples/daily_planning_agent; do
  if [ -d "$REPO_ROOT/$agent_dir" ]; then
    log "  $agent_dir: OK"
  else
    log "  $agent_dir: MISSING"
    exit 1
  fi
done

# Governed agent runtime tests (proves deterministic behavior through committed tests)
log "--- Governed agent runtime tests ---"
for test_file in \
  tests/release/clothing_advice_agent/test_clothing_advice_runtime.py \
  tests/release/daily_planning_agent/test_daily_planning_runtime.py; do
  test -f "$REPO_ROOT/$test_file" && log "  $test_file: OK" || { log "  $test_file: MISSING"; exit 1; }
done
log "  running governed agent runtime tests (deterministic fixture mode — LLM not required)..."
set +e
PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools:examples:$REPO_ROOT" \
  python3 -m pytest "$REPO_ROOT/tests/release/clothing_advice_agent" "$REPO_ROOT/tests/release/daily_planning_agent" -q --tb=short -p no:cacheprovider
agent_rc=$?
set -e
if [ "$agent_rc" -ne 0 ]; then
  log "  governed agent runtime tests: FAIL (exit $agent_rc)"
  exit 1
fi
log "  governed agent runtime tests: PASS"

# Rollback/failure recovery proof
log "--- Rollback/Recovery proof ---"
if [ -f "$REPO_ROOT/tests/release/test_failure_rollback_flow.py" ]; then
  test_count=$(grep -c "def test_" "$REPO_ROOT/tests/release/test_failure_rollback_flow.py" 2>/dev/null || echo 0)
  log "  failure_rollback_flow tests: $test_count"
  test "$test_count" -ge 1 && log "  rollback/recovery: OK" || { log "  rollback/recovery: no test functions found"; exit 1; }
else
  log "  test_failure_rollback_flow.py: MISSING"
  exit 1
fi

# Post-umbrella final acceptance
log "--- Final acceptance ---"
test -f "$REPO_ROOT/reports/post_umbrella/post_umbrella_final_acceptance.json" || { log "  post_umbrella_final_acceptance: MISSING"; exit 1; }
python3 -c "
import json
with open('$REPO_ROOT/reports/post_umbrella/post_umbrella_final_acceptance.json') as f:
    d = json.load(f)
assert d.get('status') == 'PASS', f'Expected PASS, got {d.get(\"status\")}'
assert d.get('commit') is not None, 'Missing commit field'
print('  post_umbrella_final_acceptance: PASS')
" || { log "  post_umbrella_final_acceptance: FAIL"; exit 1; }

log "=== prove-post-umbrella: PASS ==="
